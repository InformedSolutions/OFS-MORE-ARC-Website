from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.utils.decorators import method_decorator

from ...services.db_gateways import NannyGatewayActions
from ...review_util import build_url

from .nanny_contact_details import NannyContactDetailsSummary
from .nanny_personal_details import NannyPersonalDetailsSummary
from .nanny_childcare_address import NannyChildcareAddressSummary
from .nanny_first_aid import NannyFirstAidTrainingSummary
from .nanny_childcare_training import NannyChildcareTrainingSummary
from .nanny_dbs_check import NannyDbsCheckSummary
from .nanny_insurance_cover import NannyInsuranceCoverSummary


@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class NannyArcSummary(View):
    TEMPLATE_NAME = 'nanny_arc_summary.html'
    FORM_NAME = ''
    REDIRECT_NAME = 'nanny_confirmation'

    def get(self, request):

        # Get application ID
        application_id = request.GET["id"]

        context = self.create_context(application_id)

        return render(request, self.TEMPLATE_NAME, context=context)

    def post(self, request):

        # Get application ID
        application_id = request.POST["id"]

        redirect_address = build_url(self.REDIRECT_NAME, get={'id': application_id})

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
        childcare_address_context = NannyChildcareAddressSummary().create_context(application_id)
        first_aid_training_context = NannyFirstAidTrainingSummary().get_context_data(application_id)
        childcare_training_context = NannyChildcareTrainingSummary().get_context_data(application_id)
        dbs_check_context = NannyDbsCheckSummary().get_context_data(application_id)
        insurance_cover_context = NannyInsuranceCoverSummary().get_context_data(application_id)

        context_list = [
            contact_details_context,
            personal_details_context,
            childcare_address_context,
            first_aid_training_context,
            childcare_training_context,
            dbs_check_context,
            insurance_cover_context
        ]

        # Set up context
        context = {
            'application_id': application_id,
            'application_reference': application_reference,
            'title': 'Check and confirm all details',
            'html_title': 'Application summary',
            # 'form': '',
            'context_list': context_list

        }

        return context
