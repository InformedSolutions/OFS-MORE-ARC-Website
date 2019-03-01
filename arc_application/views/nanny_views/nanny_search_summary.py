import json

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View

from arc_application.views import NannyArcSummary
from ..base import has_group
from ...services.db_gateways import NannyGatewayActions


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
        application_reference = NannyArcSummary.get_application_reference(application_id)
        publish_details = NannyArcSummary.get_publish_details(application_id)

        context_function_list = NannyArcSummary.get_context_function_list()

        context_list = [self.try_get_context_data(context_func, application_id) for context_func in
                        context_function_list if
                        context_func]

        # Remove None values
        context_list = [context_dict for context_dict in context_list if context_dict]

        # Remove all change_links
        for context_dict in context_list:
            context_dict['change_link'] = None

        # Custom change_links for each individual field within the contact_details_context
        # This context is assumed to be at context_list[0].

        context_list[0]['search_table'] = True
        context_list[0]['rows'][0]['change_link'] = 'nanny_update_email_address'
        context_list[0]['rows'][1]['change_link'] = 'nanny_update_phone_number'
        context_list[0]['rows'][2]['change_link'] = 'nanny_update_add_number'

        valid_context_list = [context for context in context_list if context]

        # Remove 'Review: ' from page titles.
        for context in valid_context_list:
            context['title'] = context['title'][7:]

        context = {
            'application_id': application_id,
            'application_reference': application_reference,
            'context_list': valid_context_list,
            'summary_page': False,
            'publish_details': publish_details
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
