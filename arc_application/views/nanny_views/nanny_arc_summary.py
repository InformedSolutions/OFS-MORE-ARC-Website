from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View

from arc_application.services.arc_comments_handler import update_returned_application_statuses
from arc_application.services.nanny_email_helpers import send_accepted_email, send_returned_email
from arc_application.services.nanny_view_helpers import nanny_all_completed
from arc_application.views.base import log_applcation_release
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

        no_flags_exist = nanny_all_completed(arc_application)

        if no_flags_exist:
            send_accepted_email(**email_personalisation)
            nanny_application['application_status'] = 'ACCEPTED'
        else:
            send_returned_email(application_id, **email_personalisation)
            nanny_application['application_status'] = 'FURTHER_INFORMATION'

        update_response = NannyGatewayActions().put('application', params=nanny_application)

        if update_response.status_code != 200:
            raise BrokenPipeError('Failed to update nanny_application status')

        update_returned_application_statuses(application_id)
        log_applcation_release(request, arc_application, nanny_application, nanny_application['application_status'])
        arc_application.delete()

        return HttpResponseRedirect(redirect_address)

    def create_context(self, application_id):
        """
        Creates the context dictionary for this view.
        :param application_id: Reviewed application's id.
        :return: Context dictionary.
        """
        nanny_actions = NannyGatewayActions()
        nanny_application_dict = nanny_actions.read('application',
                                                    params={'application_id': application_id}).record

        application_reference = nanny_application_dict['application_reference']

        contact_details_context = NannyContactDetailsSummary().create_context(application_id)
        personal_details_context = NannyPersonalDetailsSummary().get_context_data(application_id)
        your_children_context = NannyYourChildrenSummary().get_context_data(application_id)
        childcare_address_context = NannyChildcareAddressSummary().get_context_data(application_id)
        first_aid_training_context = NannyFirstAidTrainingSummary().get_context_data(application_id)
        childcare_training_context = NannyChildcareTrainingSummary().get_context_data(application_id)
        dbs_check_context = NannyDbsCheckSummary().get_context_data(application_id)
        insurance_cover_context = NannyInsuranceCoverSummary().get_context_data(application_id)

        contact_details_context['change_link'] = 'nanny_contact_summary'
        personal_details_context['change_link'] = 'nanny_personal_details_summary'
        your_children_context['change_link'] = 'nanny_your_children_summary'
        childcare_address_context['change_link'] = 'nanny_childcare_address_summary'
        first_aid_training_context['change_link'] = 'nanny_first_aid_training_summary'
        childcare_training_context['change_link'] = 'nanny_childcare_training_summary'
        dbs_check_context['change_link'] = 'nanny_dbs_summary'
        insurance_cover_context['change_link'] = 'nanny_insurance_cover_summary'

        context_list = [
            contact_details_context,
            personal_details_context,
            your_children_context,
            childcare_address_context,
            first_aid_training_context,
            childcare_training_context,
            dbs_check_context,
            insurance_cover_context
        ]

        # Remove 'Review: ' from page titles.
        for context in context_list:
            context['title'] = context['title'][7:]

        context = {
            'application_id': application_id,
            'application_reference': application_reference,
            'title': 'Check and confirm all your details',
            'html_title': 'Application summary',
            'context_list': context_list,
            'summary_page': True
        }

        return context
