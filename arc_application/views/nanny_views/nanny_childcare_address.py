from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy

from arc_application.db_gateways import NannyGatewayActions
from arc_application.models import Arc


@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class NannyChildcareAddressSummary(View):
    TEMPLATE_NAME = 'nanny_general_template.html'
    FORM_NAME = ''
    # TODO -o Fix to allow use of reverse_lazy
    REDIRECT_LINK = '/nanny/first-aid-training' #reverse_lazy('nanny_childcare_address_summary')

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
        # arc_application.childcare_address_review = 'FLAGGED'
        # arc_application.save()

        # Update task status to COMPLETED
        arc_application = Arc.objects.get(application_id=application_id)
        arc_application.childcare_address_review = 'COMPLETED'
        arc_application.save()

        redirect_address = settings.URL_PREFIX + self.REDIRECT_LINK + '?id=' + application_id

        return HttpResponseRedirect(redirect_address)

    def create_context(self, application_id):
        '''

        :return: Context for the form
        '''

        # Get nanny information
        nanny_actions = NannyGatewayActions()
        home_address_info = nanny_actions.read('applicant-home-address',
                                               params={'application_id': application_id}).record

        work_location_bool = home_address_info['childcare_address']  # TODO Find work_location field
        work_at_home_bool = home_address_info['childcare_address']
        home_address_locations = nanny_actions.list('childcare-address',
                                                    params={'application_id': application_id}).record
        # TODO -o Implement first second third format
        # childcare_address_index_lookup_list = [
        #     'Childcare address',
        #     'Second childcare address',
        #     'Third childcare address',
        #     'Fourth childcare address',
        #     'Fifth childcare address',
        #     'Sixth childcare address'
        # ]

        # Set up context
        context = {
            # 'form': '',
            'application_id': application_id,
            'work_location_bool': work_location_bool,
            'work_at_home_bool': work_at_home_bool,
            'home_address_locations': home_address_locations,
            # 'childcare_address_index_lookup_list': childcare_address_index_lookup_list
        }

        context = {
            'application_id': application_id,
            'title': 'Review: Childcare address',
            # 'form': '',
            'rows': [
                {
                    'id': 'work_location_bool',
                    'name': 'Do you know where you will be working?',
                    'info': work_location_bool
                },
                {
                    'id': 'work_at_home_bool',
                    'name': 'Do you work and live at the same address?',
                    'info': work_at_home_bool
                },
                {
                    'id': 'home_address_locations',
                    'name': 'Childcare address',
                    'info': home_address_locations
                }
            ]

        }

        return context