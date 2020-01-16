import json
import logging
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from .adult_update_summary import load_json
from ..base import has_group
from ...services.db_gateways import HMGatewayActions, IdentityGatewayActions
from ..base import has_group


# Initiate logging
log = logging.getLogger()

@method_decorator(login_required, name='get')
class AdultUpdateSearchSummary(View):
    """
    View to render the Search Application Summary
    Shares many similarities with the NannyArcSummary View
    """
    TEMPLATE_NAME = 'adult_update_templates/hm_search_summary.html'

    def get(self, request):
        application_id = request.GET["id"]
        context = self.create_context(application_id)
        log_user_opened_application(request, application_id)
        log.debug("Rendering adult update search summary")
        return render(request, self.TEMPLATE_NAME, context=context)

    def create_context(self, application_id):
        """
        Creates the context dictionary for this view.

        Major changes with the Search view include the try_get_context_data method calls.
        The general strategy of this view is the same, gather all context_dicts and generate the view.
        :param application_id: Reviewed application's id.
        :return: Context dictionary.
        """
        json = load_json(application_id)
        adult_record = HMGatewayActions().read('adult', params={'adult_id': application_id}).record
        token_id = adult_record['token_id']
        applicant_record = IdentityGatewayActions().read('user', params={'application_id': adult_record['token_id']}).record
        dpa_auth = HMGatewayActions().read('dpa-auth', params={'token_id': token_id})
        ey_number = dpa_auth.record['URN']

        # add in applicant's login details
        applicant_details_summary = [
                    {"title": "Applicant's details",
                    "id": token_id},
                    {"name": "Email address",
                    "value": applicant_record['email'],
                     "pd_link": 'hm_update_email_address'},
                    {"name": 'Phone number',
                    "value": applicant_record['mobile_number'],
                     "pd_link": 'hm_update_phone_number'}
                ]

        json.insert(0, applicant_details_summary)
        json = json[:2]


        context = {
            'json': json,
            'application_id': application_id,
            'ey_number': ey_number
        }
        return context

    @staticmethod
    def try_get_context_data(get_context_data_func, app_id):
        """
        The application summary page can be reached without the application being completed.
        As such, calling get_context_data will sometimes return AttributeErrors when trying to get certain DB records.
        If this occurs, it is assumed the task for that application is not completed and does not display that data.
        :param get_context_data_func: A view's get_context_data or create_context function
        :param app_id: An application id, used to call the context func with.
        :return: A context dictionary or None.
        """
        try:
            return get_context_data_func(app_id)
        except AttributeError:
            return None

def log_user_opened_application(request, application_id):
    extra_data = {
        'action': 'opened by',
        'entity': 'new association'
    }

    if has_group(request.user, settings.CONTACT_CENTRE):
        extra_data['user_type'] = 'contact centre'
    elif has_group(request.user, settings.ARC_GROUP):
        extra_data['user_type'] = 'reviewer'
    else:
        return

    log_data = {
        'object_id': application_id,
        'template': 'timeline_logger/application_action.txt',
        'user': request.user.username,
        'extra_data': json.dumps(extra_data)
    }

    HMGatewayActions().create('timeline-log', params=log_data)

    return None

