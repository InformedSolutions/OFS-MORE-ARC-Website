from datetime import datetime
import json

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied

from timeline_logger.models import TimelineLog

from ..models import Arc, Application, ApplicantName
from ..services.db_gateways import NannyGatewayActions


class GenericApplicationHandler:
    """
    Template class for adding applications from a given application pool.
    Override for Childminder and Nanny application handling.
    """
    def __init__(self, arc_user):
        self.arc_user = arc_user

    def __get_assigned_applications(self):
        return Arc.objects.filter(user_id=self.arc_user.id)

    def add_application_from_pool(self):
        if self.__get_assigned_applications().count() <= (settings.APPLICATION_LIMIT-1):

            app_id = self._get_oldest_app_id()
            self._assign_app_to_user(app_id)

        else:
            raise PermissionDenied('Maximum applications reached.')

    def get_all_table_data(self):
        assigned_applications = self.__get_assigned_applications()

        table_data = []

        if not assigned_applications.exists():
            return table_data

        for assigned_application in assigned_applications:
            if assigned_application.app_type == 'Childminder':
                table_data.append(self.__get_childminder_table_data(assigned_application.application_id))
                
            if settings.ENABLE_NANNIES:
                if assigned_application.app_type == 'Nanny':
                    table_data.append(self.__get_nanny_table_data(assigned_application.application_id))

        return table_data

    def _get_oldest_app_id(self):
        raise NotImplementedError

    def _assign_app_to_user(self, application_id):
        raise NotImplementedError

    def _list_tasks_for_review(self):
        raise NotImplementedError

    def __get_nanny_table_data(self, application_id):
        row_data = dict()

        application_record = NannyGatewayActions().read('application', params={'application_id': str(application_id)}).record
        row_data['application_id'] = application_record['application_id']
        row_data['date_submitted'] = datetime.strptime(application_record['date_submitted'][:10], '%Y-%m-%d').strftime('%d/%m/%Y')
        row_data['last_accessed'] = datetime.strptime(application_record['date_updated'][:10], '%Y-%m-%d').strftime('%d/%m/%Y')
        row_data['app_type'] = 'Nanny'

        personal_details_record = NannyGatewayActions().read(
            'applicant-personal-details', params={'application_id': str(application_id)}).record

        row_data['applicant_name'] = personal_details_record['first_name'] + ' ' + personal_details_record['last_name']

        return row_data

    def __get_childminder_table_data(self, application_id):
        row_data = dict()

        application = Application.objects.get(application_id=application_id)
        row_data['application_id'] = application_id
        row_data['date_submitted'] = application.date_submitted.date().strftime('%d/%m/%Y')
        row_data['last_accessed'] = application.date_updated.date().strftime('%d/%m/%Y')
        row_data['app_type'] = 'Childminder'

        applicant_name = ApplicantName.objects.get(application_id=application_id)

        row_data['applicant_name'] = applicant_name.first_name + ' ' + applicant_name.last_name

        return row_data


class ChildminderApplicationHandler(GenericApplicationHandler):

    def _get_oldest_app_id(self):
        childminder_apps_for_review = Application.objects.filter(application_status='SUBMITTED')

        if childminder_apps_for_review.exists():
            childminder_apps_for_review = childminder_apps_for_review.order_by('date_updated')
            return childminder_apps_for_review[0].application_id

        else:
            raise ObjectDoesNotExist('No applications available.')

    def _assign_app_to_user(self, application_id):
        application_record = Application.objects.get(application_id=application_id)
        application_record.application_status = 'ARC_REVIEW'
        application_record.save()

        if not Arc.objects.filter(pk=application_id).exists():
            app_review = Arc.objects.create(application_id=application_id)

            for field in self._list_tasks_for_review():
                setattr(app_review, field, 'NOT_STARTED')

            app_review.app_type = 'Childminder'
            app_review.last_accessed = application_record.date_updated
            app_review.user_id = self.arc_user.id
            app_review.save()

        else:
            arc_user = Arc.objects.get(pk=application_id)
            arc_user.last_accessed = application_record.date_updated
            arc_user.user_id = self.arc_user.id
            arc_user.save()

        TimelineLog.objects.create(
            content_object=self.arc_user,
            user=self.arc_user,
            template='timeline_logger/application_action.txt',
            extra_data={'user_type': 'reviewer', 'action': 'assigned to', 'entity': 'application'}
        )

    def _list_tasks_for_review(self):
        example_application = Application.objects.all()[0]
        return [i.name[:-12] for i in example_application._meta.fields if i.name[-12:] == '_arc_flagged']


class NannyApplicationHandler(GenericApplicationHandler):

    def _get_oldest_app_id(self):
        response = NannyGatewayActions().list(
            'application', params={'application_status': 'SUBMITTED', 'ordering': 'date_submitted'})

        if response.status_code == 200:
            submitted_apps = response.record
            return submitted_apps[0]['application_id']

        else:
            raise ObjectDoesNotExist('No applications available.')

    def _assign_app_to_user(self, application_id):
        app_record = NannyGatewayActions().read('application', params={'application_id': application_id}).record
        app_record['application_status'] = 'ARC_REVIEW'
        NannyGatewayActions().put('application', params=app_record)

        if not Arc.objects.filter(pk=application_id).exists():
            app_review = Arc.objects.create(application_id=application_id)

            for field in self._list_tasks_for_review():
                setattr(app_review, field, 'NOT_STARTED')

            app_review.app_type = 'Nanny'
            app_review.last_accessed = app_record['date_updated']
            app_review.user_id = self.arc_user.id
            app_review.save()

        else:
            arc_user = Arc.objects.get(pk=application_id)
            arc_user.last_accessed = app_record['date_updated']
            arc_user.user_id = self.arc_user.id
            arc_user.save()

        # Log assigning application to ARC user.
        extra_data = {
                'user_type': 'reviewer',
                'action': 'assigned to',
                'entity': 'application'
            }

        log_data = {
            'object_id': app_record['application_id'],
            'template': 'timeline_logger/application_action.txt',
            'user': self.arc_user.username,
            'extra_data': json.dumps(extra_data)
        }

        NannyGatewayActions().create('timeline-log', params=log_data)

    def _list_tasks_for_review(self):
        example_application = NannyGatewayActions().list('application', params={}).record[0]
        return [i[:-12] for i in example_application.keys() if i[-12:] == '_arc_flagged']