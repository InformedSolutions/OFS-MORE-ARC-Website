from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views import View
from django.utils.decorators import method_decorator

from arc_application.models import Arc

from arc_application.db_gateways import NannyGatewayActions


@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class ARCUserSummaryView(View):
    template_name = 'arc_user_summary.html'

    def get(self, request):
        context = self.get_context_data(request)
        return render(request, self.template_name, context=context)

    def post(self, request):

        if 'add_nanny_application' in request.POST:
            pass
        elif 'add_childminder_application' in request.POST:
            pass

        return self.get(request)

    def get_context_data(self, request):
        return {}


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
            self._assign_app_to_user(self.arc_user, app_id)
            # self._get_table_data()
        else:
            raise RuntimeError('Maximum applications reached.')

    def release_application(self):
        pass

    def _get_oldest_app_id(self):
        raise NotImplementedError

    def _assign_app_to_user(self, application_id):
        raise NotImplementedError

    def _list_tasks_for_review(self):
        raise NotImplementedError


class ChildminderApplicationHandler(ApplicationHandlerTemplate):

    def _get_oldest_app_id(self):
        pass

    def _assign_app_to_user(self, application_id):
        pass

    def _list_tasks_for_review(self):
        pass


class NannyApplicationHandler(ApplicationHandlerTemplate):

    def _get_oldest_app_id(self):
        submitted_apps = NannyGatewayActions().list(
            'application',
            params={
                'application_status': 'SUBMITTED',
                'ordering': 'date_submitted'
            }
        )
        return submitted_apps[0]['application_id']

    def _assign_app_to_user(self, application_id):
        app_record = NannyGatewayActions().read('application', params={'application_id': application_id}).record
        app_record['application_status'] = 'ARC_REVIEW'
        NannyGatewayActions().put('application', params=app_record)

        if not Arc.objects.filter(pk=application_id).exists():
            app_review = Arc.objects.create(application_id=application_id)

            for field in self._list_tasks_for_review():
                setattr(app_review, field, 'NOT_STARTED')

            app_review.app_type = 'Nanny'
            app_review.last_accessed = str(app_record['date_updated'].strftime('%d/%m/%Y'))
            app_review.user_id = self.arc_user.id
            app_review.save()

        else:
            arc_user = Arc.objects.get(pk=application_id)
            arc_user.last_accessed = str(app_record['date_updated'].strftime('%d/%m/%Y'))
            arc_user.user_id = self.arc_user.id
            arc_user.save()

    def _list_tasks_for_review(self):
        example_application = NannyGatewayActions().list('application', params={})[0]
        return [i[:-12] for i in example_application.keys() if i[-12:] == '_arc_flagged']
