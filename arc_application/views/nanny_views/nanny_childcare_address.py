from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy

from arc_application.db_gateways import NannyGatewayActions
from arc_application.views.nanny_views.nanny_view_helpers import parse_date_of_birth


@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class NannyChildcareAddressSummary(View):
    TEMPLATE_NAME = 'nanny_childcare_address_summary.html'
    FORM_NAME = ''
    # TODO -o Fix to allow use of reverse_lazy
    REDIRECT_LINK = '/nanny/first-aid-training' #reverse_lazy('nanny_childcare_address_summary')

    def get(self, request):

        # Get application ID
        application_id = request.GET["id"]

        # Get nanny information
        nanny_actions = NannyGatewayActions()
        home_address_info = nanny_actions.read('applicant-home-address',
                                                params={'application_id': application_id}).record


        work_location_bool = home_address_info['childcare_address'] # TODO Find work_location field
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

        return render(request, self.TEMPLATE_NAME, context=context)

    def post(self, request):
        # TODO -o childcare_address post

        # Get application ID
        application_id = request.GET["id"]

        context = {}

        redirect_address = settings.URL_PREFIX + self.REDIRECT_LINK + '?id=' + application_id

        return HttpResponseRedirect(redirect_address)