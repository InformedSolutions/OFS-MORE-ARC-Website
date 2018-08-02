from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy

from arc_application.db_gateways import IdentityGatewayActions, NannyGatewayActions
from arc_application.models import Arc

# Nanny View Classes

from arc_application.views.nanny_views.nanny_contact_details import NannyContactDetailsSummary
from arc_application.views.nanny_views.nanny_personal_details import NannyPersonalDetailsSummary
from arc_application.views.nanny_views.nanny_childcare_address import NannyChildcareAddressSummary
from arc_application.views.nanny_views.nanny_first_aid import NannyFirstAidTrainingSummary
from arc_application.views.nanny_views.nanny_childcare_training import NannyChildcareTrainingSummary
from arc_application.views.nanny_views.nanny_dbs_check import NannyDbsCheckSummary
from arc_application.views.nanny_views.nanny_insurance_cover import NannyInsuranceCoverSummary


@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class NannyArcSummary(View):
    TEMPLATE_NAME = 'nanny_arc_summary.html'
    FORM_NAME = ''
    # TODO -o Fix to allow use of reverse_lazy
    REDIRECT_LINK = '/nanny/review-confirmation' #reverse_lazy('nanny_childcare_address_summary')

    def get(self, request):

        # Get application ID
        application_id = request.GET["id"]

        context = self.create_context(application_id)

        return render(request, self.TEMPLATE_NAME, context=context)

    def post(self, request):
        # TODO -o first_aid_training post

        # Get application ID
        application_id = request.POST["id"]

        # # Update task status to FLAGGED
        # arc_application = Arc.objects.get(application_id=application_id)
        # arc_application.first_aid_review = 'FLAGGED'
        # arc_application.save()

        # Update task status to COMPLETED
        arc_application = Arc.objects.get(application_id=application_id)
        arc_application.first_aid_review = 'COMPLETED'
        arc_application.save()

        redirect_address = settings.URL_PREFIX + self.REDIRECT_LINK + '?id=' + application_id

        return HttpResponseRedirect(redirect_address)

    def create_context(self, application_id):
        '''

        :return: Dictionary of all view's contexts.
        '''

        nanny_actions = NannyGatewayActions()
        nanny_application_dict = nanny_actions.read('application',
                                                    params={'application_id': application_id}).record
        application_reference = nanny_application_dict['application_reference']
        application_reference_dict = {'application_reference': application_reference}

        contact_details_context = NannyContactDetailsSummary().create_context(application_id)
        personal_details_context = NannyPersonalDetailsSummary().create_context(application_id)
        childcare_address_context = NannyChildcareAddressSummary().create_context(application_id)
        first_aid_training_context = NannyFirstAidTrainingSummary().create_context(application_id)
        childcare_training_context = NannyChildcareTrainingSummary().create_context(application_id)
        dbs_check_context = NannyDbsCheckSummary().create_context(application_id)
        insurance_cover_context = NannyInsuranceCoverSummary().create_context(application_id)

        context_list = [application_reference_dict,
                        contact_details_context,
                        personal_details_context,
                        childcare_address_context,
                        first_aid_training_context,
                        childcare_training_context,
                        dbs_check_context,
                        insurance_cover_context]

        summary_context = {}

        for context in context_list:
            summary_context = self.merge_dicts(summary_context, context)

        nanny_summary_dict = nanny_actions.read('summary',
                                                    params={'application_id': application_id}).record

        print(nanny_summary_dict)

        return summary_context

    def make_json(self, application_id):
        pass



    def merge_dicts(self, dict1, dict2):
        new_dict = dict1.copy()
        new_dict.update(dict2)
        return new_dict
