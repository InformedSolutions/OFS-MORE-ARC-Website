from django.views.generic import TemplateView

from arc_application.models import Arc

from arc_application.db_gateways import NannyGatewayActions


class ARCUserSummaryView(TemplateView):
    pass


class ApplicationHandlerTemplate:
    """
    Template class for adding applications from a given application pool.
    Override for Childminder and Nanny application handling.
    """
    def __count_assigned_apps(self):
        return Arc.objects.filter(user_id=request.user.id).count()

    def add_application_from_pool(self,  arc_user):
        app_id = self._get_oldest_app_id()
        self._assign_app_to_user(arc_user, app_id)
        # self._get_table_data()

    def release_application(self):
        pass

    def _get_oldest_app_id(self):
        raise NotImplementedError

    def _assign_app_to_user(self, arc_user, application_id):
        raise NotImplementedError

    def _list_tasks_for_review(self):
        raise NotImplementedError


class ChildminderApplicationHandler(ApplicationHandlerTemplate):

    def _get_oldest_app_id(self):
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

    def _assign_app_to_user(self, arc_user, application_id):
        pass

    def _list_tasks_for_review(self):
        example_application = NannyGatewayActions().list('application', params={})[0]
        return [i[:-12] for i in example_application.keys() if i[-12:] == '_arc_flagged']
