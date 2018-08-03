from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy

from arc_application.db_gateways import IdentityGatewayActions
from arc_application.models import Arc


@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class NannyContactDetailsSummary(View):
    TEMPLATE_NAME = 'nanny_general_template.html'
    FORM_NAME = ''
    # TODO Fix to allow use of reverse_lazy
    REDIRECT_LINK = '/nanny/personal-details' #reverse_lazy('nanny_childcare_address_summary')

    def get(self, request):

        # Get application ID
        application_id = request.GET["id"]

        context = self.create_context(application_id)

        return render(request, self.TEMPLATE_NAME, context=context)

    def post(self, request):
        # TODO -o contact_details post

        # Get application ID
        application_id = request.POST["id"]

        # # Update task status to FLAGGED
        # arc_application = Arc.objects.get(application_id=application_id)
        # arc_application.first_aid_review = 'FLAGGED'
        # arc_application.save()

        # Update task status to COMPLETED
        arc_application = Arc.objects.get(application_id=application_id)
        arc_application.login_details_review = 'COMPLETED'
        arc_application.save()

        redirect_address = settings.URL_PREFIX + self.REDIRECT_LINK + '?id=' + application_id

        return HttpResponseRedirect(redirect_address)

    def create_context(self, application_id):
        '''

        :return: Context for the form
        '''

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
            # 'form': '',
            'rows': [
                {
                    'id': 'email',
                    'name': 'Email',
                    'info': email
                },
                {
                    'id': 'mobile_phone_number',
                    'name': 'Mobile phone number',
                    'info': mobile_phone_number
                },
                {
                    'id': 'mobile_phone_number',
                    'name': 'Other phone number',
                    'info': other_phone_number
                }
            ]

        }

        return context