from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views import View
from django.utils.decorators import method_decorator

from timeline_logger.models import TimelineLog

from arc_application.models import Arc, Application, ApplicantName
from arc_application.db_gateways import NannyGatewayActions


@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class ARCUserSummaryView(View):
    template_name = 'arc_user_summary.html'

    def get(self, request):
        context = self.get_context_data()
        return render(request, self.template_name, context=context)

    def post(self, request):

        if 'add_nanny_application' in request.POST:
            app_handler = NannyApplicationHandler(arc_user=request.user)

        elif 'add_childminder_application' in request.POST:
            app_handler = ChildminderApplicationHandler(arc_user=request.user)

        try:
            app_handler.add_application_from_pool()
            context = self.get_context_data()
        except ObjectDoesNotExist:
            context = self.get_context_data()
            context['error_exist'] = 'true'
            context['error_title'] = 'No available applications'
            context['error_text'] = 'There are currently no more applications ready for a review'

        return render(request, self.template_name, context=context)

    def get_context_data(self):
        context = dict()
        context['entries'] = ApplicationHandlerTemplate(arc_user=self.request.user).get_all_table_data()

        if not len(context['entries']):
            context['empty'] = 'true'

        return context


class ApplicationHandlerTemplate:
    """
    Template class for adding applications from a given application pool.
    Override for Childminder and Nanny application handling.
    """
    def __init__(self, arc_user):
        self.arc_user = arc_user

    def __count_assigned_apps(self, arc_user):
        return Arc.objects.filter(user_id=arc_user.id).count()

    def add_application_from_pool(self):
        if self.__count_assigned_apps(arc_user=self.arc_user) < settings.APPLICATION_LIMIT:
            app_id = self._get_oldest_app_id()
            if app_id is not None:
                self._assign_app_to_user(app_id)
            else:
                raise ObjectDoesNotExist('No applications available.')
        else:
            raise RuntimeError('Maximum applications reached.')

    def release_application(self):
        pass

    def get_all_table_data(self):
        assigned_applications = Arc.objects.filter(user_id=self.arc_user.id)

        table_data = []

        if not assigned_applications.exists():
            return table_data

        for assigned_application in assigned_applications:
            if assigned_application.app_type == 'Childminder':
                table_data.append(self.__get_childminder_table_data(assigned_application.application_id))
            elif assigned_application.app_type == 'Nanny':
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
        row_data['date_submitted'] = application_record['date_submitted']
        row_data['last_accessed'] = application_record['date_updated']  #self.arc_user.last_accessed
        row_data['app_type'] = 'Nanny'

        personal_details_record = NannyGatewayActions().read(
            'applicant-personal-details',
            params={
                'application_id': str(application_id)
            }
        ).record

        row_data['applicant_name'] = personal_details_record['first_name'] + ' ' + personal_details_record['last_name']

        return row_data

    def __get_childminder_table_data(self, application_id):
        row_data = dict()

        application = Application.objects.get(application_id=application_id)
        row_data['application_id'] = application_id
        row_data['date_submitted'] = application.date_submitted
        row_data['last_accessed'] = application.date_updated
        row_data['app_type'] = 'Childminder'

        applicant_name = ApplicantName.objects.get(application_id=application_id)

        row_data['applicant_name'] = applicant_name.first_name + ' ' + applicant_name.last_name

        return row_data


class ChildminderApplicationHandler(ApplicationHandlerTemplate):

    def _get_oldest_app_id(self):

        childminder_apps_for_review = Application.objects.filter(application_status='SUBMITTED')
        if childminder_apps_for_review.exists():
            childminder_apps_for_review.order_by('date_updated')
            return childminder_apps_for_review[0].application_id
        else:
            return None

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


class NannyApplicationHandler(ApplicationHandlerTemplate):

    def _get_oldest_app_id(self):
        response = NannyGatewayActions().list(
            'application',
            params={
                'application_status': 'SUBMITTED',
                'ordering': 'date_submitted'
            }
        )
        if response.status_code == 200:
            submitted_apps = response.record
            return submitted_apps[0]['application_id']  # TODO Check that this returns newest application.
        else:
            return None

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

    def _list_tasks_for_review(self):
        example_application = NannyGatewayActions().list('application', params={}).record[0]
        return [i[:-12] for i in example_application.keys() if i[-12:] == '_arc_flagged']
