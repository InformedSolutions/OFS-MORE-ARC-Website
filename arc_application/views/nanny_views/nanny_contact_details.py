from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View

from arc_application.forms.nanny_forms.form_data import SIGN_IN_DATA
from ...models import Arc
from ...review_util import build_url
from ...services.db_gateways import IdentityGatewayActions


@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class NannyContactDetailsSummary(View):
    TEMPLATE_NAME = 'nanny_general_template.html'
    FORM_NAME = ''
    REDIRECT_NAME = 'nanny_personal_details_summary'

    def get(self, request):
        # Get application ID
        application_id = request.GET["id"]

        context = self.create_context(application_id)

        return render(request, self.TEMPLATE_NAME, context=context)

    def post(self, request):
        # Get application ID
        application_id = request.POST["id"]

        # Update task status to COMPLETED
        arc_application = Arc.objects.get(application_id=application_id)
        arc_application.login_details_review = 'COMPLETED'
        arc_application.save()

        redirect_address = build_url(self.REDIRECT_NAME, get={'id': application_id})

        return HttpResponseRedirect(redirect_address)

    @staticmethod
    def create_context(application_id):
        """
        Creates the context dictionary for this view.
        :param application_id: Reviewed application's id.
        :return: Context dictionary.
        """

        # Get nanny information
        identity_actions = IdentityGatewayActions()
        contact_details = identity_actions.read('user',
                                                params={'application_id': application_id}).record

        email = contact_details['email']
        mobile_phone_number = contact_details['mobile_number']
        other_phone_number = contact_details['add_phone_number']

        # Set up context
        context = {
            'application_id': application_id,
            'title': 'Review: Your sign in details',
            'change_link': 'nanny_contact_summary',
            'rows': [
                {
                    'id': 'email',
                    'name': SIGN_IN_DATA['email'],
                    'info': email
                },
                {
                    'id': 'mobile_phone_number',
                    'name': SIGN_IN_DATA['mobile_phone'],
                    'info': mobile_phone_number
                },
                {
                    'id': 'other_phone_number',
                    'name': SIGN_IN_DATA['other_phone'],
                    'info': other_phone_number
                }
            ]

        }

        return context
