from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy

from arc_application.db_gateways import IdentityGatewayActions
from arc_application.views.nanny_views.nanny_view_helpers import parse_date_of_birth


@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class NannyContactDetailsSummary(View):
    TEMPLATE_NAME = 'nanny_contact_details_summary.html'
    FORM_NAME = ''
    # TODO Fix to allow use of reverse_lazy
    REDIRECT_LINK = '/nanny/personal-details' #reverse_lazy('nanny_childcare_address_summary')

    def get(self, request):

        # Get application ID
        application_id = request.GET["id"]

        # Get nanny information
        identity_actions = IdentityGatewayActions()
        contact_details = identity_actions.read('user',
                                                params={'application_id': application_id}).record

        email = contact_details['email']
        mobile_phone_number = contact_details['mobile_number']
        other_phone_number = contact_details['add_phone_number']

        # Set up context
        context = {
            # 'form': '',
            'application_id': application_id,
            'email': email,
            'mobile_number': mobile_phone_number,
            'add_phone_number': other_phone_number
        }

        return render(request, self.TEMPLATE_NAME, context=context)

    def post(self, request):
        # TODO contact_details post

        # Get application ID
        application_id = request.GET["id"]

        context = {}

        redirect_address = settings.URL_PREFIX + self.REDIRECT_LINK + '?id=' + application_id

        return HttpResponseRedirect(redirect_address)

    def month_converter(self, dob_string):
        month_list = ["January",
                      "Februrary",
                      "March",
                      "April",
                      "May",
                      "June",
                      "July",
                      "August",
                      "September",
                      "October",
                      "November",
                      "December"]

        dob_dict = parse_date_of_birth(dob_string)
        birth_day = dob_dict['birth_day']
        birth_month = dob_dict['birth_month']
        birth_year = dob_dict['birth_year']

        month = month_list[int(birth_month) + 1]

        return "{0} {1} {2}".format(birth_day, month, birth_year)