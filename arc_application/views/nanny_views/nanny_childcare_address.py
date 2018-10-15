from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.utils.decorators import method_decorator

from arc_application.services.db_gateways import NannyGatewayActions
from arc_application.models import Arc
from arc_application.review_util import build_url


@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class NannyChildcareAddressSummary(View):
    TEMPLATE_NAME = 'nanny_general_template.html'
    FORM_NAME = ''
    REDIRECT_NAME = 'nanny_first_aid_training_summary'

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
        arc_application.childcare_address_review = 'COMPLETED'
        arc_application.save()

        redirect_address = build_url(self.REDIRECT_NAME, get={'id': application_id})

        return HttpResponseRedirect(redirect_address)

    def create_context(self, application_id):
        """
        Creates the context dictionary for this view.
        :param application_id: Reviewed application's id.
        :return: Context dictionary.
        """

        # Get nanny information
        nanny_actions = NannyGatewayActions()
        nanny_application = nanny_actions.read('application',
                                               params={'application_id': application_id}).record
        home_address_info = nanny_actions.read('applicant-home-address',
                                               params={'application_id': application_id,
                                                       'current_address': True}).record
        childcare_address_info = nanny_actions.read('applicant-home-address',
                                               params={'application_id': application_id,
                                                       'childcare_address': True}).record

        work_location_bool = nanny_application['address_to_be_provided']
        if home_address_info == childcare_address_info:
            work_at_home_bool = 'Yes'
        else:
            work_at_home_bool = 'No'

        if work_location_bool:
            home_address_locations = nanny_actions.list('childcare-address',
                                                        params={'application_id': application_id}).record
        else:
            home_address_locations = {}

        # Set up context
        context = {
            'application_id': application_id,
            'title': 'Review: Childcare address',
            # 'form': '',
            'rows': [
                {
                    'id': 'work_location_bool',
                    'name': "Do you know where you'll be working?",
                    'info': work_location_bool
                },
                {
                    'id': 'work_at_home_bool',
                    'name': 'Will you work and live at the same address?',
                    'info': work_at_home_bool
                },
                {
                    'id': 'home_address_locations',
                    'name': 'Childcare address',
                    'info': home_address_locations
                },
            ]

        }

        return context
