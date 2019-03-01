from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View

from arc_application.services.arc_comments_handler import update_returned_application_statuses
from arc_application.services.nanny_email_helpers import send_accepted_email, send_returned_email
from arc_application.services.nanny_view_helpers import nanny_all_completed
from arc_application.views.base import release_application
from arc_application.views.nanny_views.nanny_your_children import NannyYourChildrenSummary
from .nanny_childcare_address import NannyChildcareAddressSummary
from .nanny_childcare_training import NannyChildcareTrainingSummary
from .nanny_contact_details import NannyContactDetailsSummary
from .nanny_dbs_check import NannyDbsCheckSummary
from .nanny_first_aid import NannyFirstAidTrainingSummary
from .nanny_insurance_cover import NannyInsuranceCoverSummary
from .nanny_personal_details import NannyPersonalDetailsSummary
from ...models import Arc
from ...review_util import build_url
from ...services.db_gateways import NannyGatewayActions, IdentityGatewayActions


@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class NannyArcSummary(View):

    TEMPLATE_NAME = 'nanny_arc_summary.html'
    FORM_NAME = ''
    REDIRECT_NAME = 'nanny_confirmation'

    def get(self, request):
        application_id = request.GET["id"]
        context = self.create_context(application_id)
        return render(request, self.TEMPLATE_NAME, context=context)

    def post(self, request):
        application_id = request.POST["id"]
        redirect_address = build_url(self.REDIRECT_NAME, get={'id': application_id})

        arc_application = Arc.objects.get(application_id=application_id)
        params = {'application_id': application_id}
        nanny_application = NannyGatewayActions().read('application', params=params).record
        nanny_personal_details = NannyGatewayActions().read('applicant-personal-details', params=params).record
        identity_user = IdentityGatewayActions().read('user', params=params).record

        email_personalisation = {'email': identity_user['email'],
                                 'first_name': nanny_personal_details['first_name'],
                                 'ref': nanny_application['application_reference']}

        no_flags_exist = nanny_all_completed(arc_application, application_id)

        if no_flags_exist:
            send_accepted_email(**email_personalisation)
            release_application(request, application_id, 'ACCEPTED')
        else:
            send_returned_email(application_id, **email_personalisation)
            release_application(request, application_id, 'FURTHER_INFORMATION')

        update_returned_application_statuses(application_id)

        return HttpResponseRedirect(redirect_address)

    def create_context(self, application_id):
        """
        Creates the context dictionary for this view.
        :param application_id: Reviewed application's id.
        :return: Context dictionary.
        """

        application_reference = self.get_application_reference(application_id)
        publish_details = self.get_publish_details(application_id)

        context_function_list = self.get_context_function_list(application_id)

        context_list = [context_func(application_id) for context_func in context_function_list if context_func]

        # Remove 'Review: ' from page titles.
        # FIXME Change each view to use verbose_task_name property instead.
        for context in context_list:
            context['title'] = context['title'][7:]

        context = {
            'application_id': application_id,
            'application_reference': application_reference,
            'title': 'Check and confirm all your details',
            'html_title': 'Application summary',
            'context_list': context_list,
            'summary_page': True,
            'your_children_context_index': 2,
            'publish_details': publish_details
        }

        return context

    @staticmethod
    def get_context_function_list(application_id):
        """
        A method to return the contexts to be rendered on the master summary page.
        :return: A list of functions that can be called with application_id to return a context dictionary.
        """
        show_your_children = NannyArcSummary.get_show_your_children(application_id)

        return [
            NannyContactDetailsSummary.create_context,
            NannyPersonalDetailsSummary().get_context_data,
            NannyYourChildrenSummary().get_context_data if show_your_children else None,
            NannyChildcareAddressSummary().get_context_data,
            NannyFirstAidTrainingSummary().get_context_data,
            NannyChildcareTrainingSummary().get_context_data,
            NannyDbsCheckSummary().get_context_data,
            NannyInsuranceCoverSummary().get_context_data
        ]

    @staticmethod
    def get_show_your_children(application_id):
        """
        A method to return the condition on which to show the your_children task as part of the summary.
        :return: A boolean True if the your_children summary should be shown.
        Optional TODO: Relocate this function to a routing helper file.
        """
        nanny_personal_details_dict = NannyGatewayActions().read('applicant-personal-details',
                                                                 params={'application_id': application_id}).record
        return nanny_personal_details_dict['your_children']

    @staticmethod
    def get_publish_details(application_id):
        nanny_actions = NannyGatewayActions()
        nanny_application_dict = nanny_actions.read('application',
                                                    params={'application_id': application_id}).record
        return nanny_application_dict['share_info_declare']

    @staticmethod
    def get_application_reference(application_id):
        nanny_actions = NannyGatewayActions()
        nanny_application_dict = nanny_actions.read('application',
                                                    params={'application_id': application_id}).record
        return nanny_application_dict['application_reference']
