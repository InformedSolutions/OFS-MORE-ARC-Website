import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views import View

from .nanny_childcare_address import NannyChildcareAddressSummary
from .nanny_childcare_training import NannyChildcareTrainingSummary
from .nanny_contact_details import NannyContactDetailsSummary
from .nanny_dbs_check import NannyDbsCheckSummary
from .nanny_first_aid import NannyFirstAidTrainingSummary
from .nanny_insurance_cover import NannyInsuranceCoverSummary
from .nanny_personal_details import NannyPersonalDetailsSummary
from ...services.db_gateways import NannyGatewayActions
from ..base import has_group


@method_decorator(login_required, name='get')
class NannySearchSummary(View):
    """
    View to render the Search Application Summary
    Shares many similarities with the NannyArcSummary View
    """
    TEMPLATE_NAME = 'nanny_search_summary.html'

    def get(self, request):
        application_id = request.GET["id"]
        context = self.create_context(application_id)
        log_user_opened_application(request, application_id)
        return render(request, self.TEMPLATE_NAME, context=context)

    def create_context(self, application_id):
        """
        Creates the context dictionary for this view.

        Major changes with the Search view include the try_get_context_data method calls.
        The general strategy of this view is the same, gather all context_dicts and generate the view.
        :param application_id: Reviewed application's id.
        :return: Context dictionary.
        """
        nanny_actions = NannyGatewayActions()
        nanny_application_dict = nanny_actions.read('application',
                                                    params={'application_id': application_id}).record

        application_reference = nanny_application_dict['application_reference']

        contact_details_context = self.try_get_context_data(NannyContactDetailsSummary().create_context, application_id)
        personal_details_context = self.try_get_context_data(NannyPersonalDetailsSummary().get_context_data,
                                                             application_id)
        childcare_address_context = self.try_get_context_data(NannyChildcareAddressSummary().create_context,
                                                              application_id)
        first_aid_training_context = self.try_get_context_data(NannyFirstAidTrainingSummary().get_context_data,
                                                               application_id)
        childcare_training_context = self.try_get_context_data(NannyChildcareTrainingSummary().get_context_data,
                                                               application_id)
        dbs_check_context = self.try_get_context_data(NannyDbsCheckSummary().get_context_data, application_id)
        insurance_cover_context = self.try_get_context_data(NannyInsuranceCoverSummary().get_context_data,
                                                            application_id)

        # Custom change_links for each individual field within the context_dict.
        contact_details_context['search_table'] = True
        contact_details_context['rows'][0]['change_link'] = 'nanny_update_email_address'
        contact_details_context['rows'][1]['change_link'] = 'nanny_update_phone_number'
        contact_details_context['rows'][2]['change_link'] = 'nanny_update_add_number'

        # Some values in this context_list may be None
        context_list = [
            contact_details_context,
            personal_details_context,
            childcare_address_context,
            first_aid_training_context,
            childcare_training_context,
            dbs_check_context,
            insurance_cover_context
        ]

        valid_context_list = [context for context in context_list if context]

        # Remove 'Review: ' from page titles.
        for context in valid_context_list:
            context['title'] = context['title'][7:]

        context = {
            'application_id': application_id,
            'application_reference': application_reference,
            'context_list': valid_context_list,
            'summary_page': False
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
        'entity': 'application'
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

    NannyGatewayActions().create('timeline-log', params=log_data)

    return None
