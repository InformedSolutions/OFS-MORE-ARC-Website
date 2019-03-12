from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View

from ...services.arc_comments_handler import update_returned_application_statuses
from ...services.nanny_email_helpers import send_accepted_email, send_returned_email
from ...services.nanny_view_helpers import nanny_all_completed
from ...views.base import release_application
from ...models import Arc
from ...review_util import build_url
from ...services.db_gateways import NannyGatewayActions, IdentityGatewayActions
from .nanny_utils import get_nanny_summary_variables


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

        context_list = get_nanny_summary_variables(application_id)

        context = {
            'application_id': application_id,
            'application_reference': application_reference,
            'title': 'Check and confirm all your details',
            'html_title': 'Application summary',
            'context_list': context_list,
            'summary_page': True,
            'publish_details': publish_details
        }

        return context

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
