import logging
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views import View
from django.utils.decorators import method_decorator

from ...services.db_gateways import NannyGatewayActions

# Initiate logging
log = logging.getLogger()

@method_decorator(login_required, name='get')
class NannyArcSummaryConfirmation(View):
    TEMPLATE_NAMES = ('review-confirmation.html', 'review-sent-back.html')
    FORM_NAME = ''

    def get(self, request):

        # Get application ID
        application_id = request.GET["id"]

        # Choose which template to display
        template = self.get_template(application_id)
        log.debug("Rendering nanny arc review confirmation page")
        # Render chosen template
        return render(request, template)

    def get_template(self, application_id):
        """
        Decides which template should be rendered and performs a send_email for the relevant template.
        :param application_id: Reviewed application's id.
        :return: A string of a template's name, one of the self.TEMPLATE_NAMES defined.
        """
        # Get possible templates
        confirmation, sent_back = self.TEMPLATE_NAMES

        nanny_application = NannyGatewayActions().read('application', params={'application_id': application_id}).record

        if nanny_application['application_status'] == 'ACCEPTED':
            return confirmation
        elif nanny_application['application_status'] == 'FURTHER_INFORMATION':
            return sent_back
        else:
            raise ValueError("""
            nanny_application["application_status"] should be either "ACCEPTED" or "FURTHER_INFORMATION",
             but is {0}.'.format()nanny_application['application_status']""")
