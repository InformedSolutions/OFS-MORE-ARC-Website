from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views import View
from django.utils.decorators import method_decorator

from arc_application.models import Arc
from arc_application.services.db_gateways import NannyGatewayActions, IdentityGatewayActions

from arc_application.views.nanny_views.nanny_view_helpers import nanny_all_completed
from arc_application.views.nanny_views.nanny_email_helpers import send_accepted_email, send_returned_email


@method_decorator(login_required, name='get')
class NannyArcSummaryConfirmation(View):
    TEMPLATE_NAMES = ('review-confirmation.html', 'review-sent-back.html')
    FORM_NAME = ''

    def get(self, request):

        # Get application ID
        application_id = request.GET["id"]

        # Choose which template to display
        template = self.get_template(application_id)

        # Render chosen template
        return render(request, template)

    def get_template(self, application_id):
        """
        Decides which template should be rendered and performs a send_email for the relevant template.
        :param application_id: Reviewed application's id.
        :return: A string of a template's name, one of the self.TEMPLATE_NAMES defined.
        """

        # Get applications
        arc_application = Arc.objects.get(application_id=application_id)
        nanny_actions = NannyGatewayActions()
        identity_actions = IdentityGatewayActions()
        params = {'application_id': application_id}
        nanny_personal_details = nanny_actions.read('applicant-personal-details', params=params).record
        nanny_application = nanny_actions.read('application', params=params).record
        identity_user = identity_actions.read('user', params=params).record

        send_email_dict = {'email': identity_user['email'],
                           'first_name': nanny_personal_details['first_name'],
                           'ref': nanny_application['application_reference']}


        # Get possible templates
        confirmation, sent_back = self.TEMPLATE_NAMES

        # If all sections are marked 'COMPLETED'
        if nanny_all_completed(arc_application):
            send_accepted_email(**send_email_dict)
            return confirmation
        # If any section is 'FLAGGED'
        else:
            send_returned_email(**send_email_dict)
            return sent_back
