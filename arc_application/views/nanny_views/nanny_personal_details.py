from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.utils.decorators import method_decorator

from arc_application.services.db_gateways import NannyGatewayActions
from arc_application.views.nanny_views.nanny_view_helpers import parse_date_of_birth
from arc_application.models import Arc
from arc_application.review_util import build_url


@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class NannyPersonalDetailsSummary(View):
    TEMPLATE_NAME = 'nanny_personal_details_summary.html'
    FORM_NAME = ''
    REDIRECT_NAME = 'nanny_childcare_address_summary'

    def get(self, request):

        # Get application ID
        application_id = request.GET["id"]

        context = self.create_context(application_id)

        return render(request, self.TEMPLATE_NAME, context=context)

    def post(self, request):

        # Get application ID
        application_id = request.POST["id"]

        # # Update task status to FLAGGED
        # arc_application = Arc.objects.get(application_id=application_id)
        # arc_application.personal_details_review = 'FLAGGED'
        # arc_application.save()

        # Update task status to COMPLETED
        arc_application = Arc.objects.get(application_id=application_id)
        arc_application.personal_details_review = 'COMPLETED'
        arc_application.save()

        redirect_address = build_url(self.REDIRECT_NAME, get={'id': application_id})

        return HttpResponseRedirect(redirect_address)

    def month_converter(self, dob_string):
        """
        Converts a numerical month into the related string month.
        :param dob_string: a Date Of Birth string in the format 'DD-MM-YYYY'
        :return: a DOB string in format 'DD-Month-YYYY'
        """

        # TODO: This could be done more simply with a DateTime object

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

    def create_context(self, application_id):
        """
        Creates the context dictionary for this view.
        :param application_id: Reviewed application's id.
        :return: Context dictionary.
        """

        # Get nanny information
        nanny_actions = NannyGatewayActions()
        personal_details = nanny_actions.read('applicant-personal-details',
                                              params={'application_id': application_id}).record
        home_address = nanny_actions.read('applicant-home-address',
                                          params={'application_id': application_id}).record

        first_name = personal_details['first_name']
        middle_names = personal_details['middle_names']
        last_name = personal_details['last_name']
        full_name = "{0} {1} {2}".format(first_name, middle_names, last_name)

        dob_string = personal_details['date_of_birth']
        dob_string_with_month = self.month_converter(dob_string)

        street_line1 = home_address['street_line1']
        street_line2 = home_address['street_line2']
        town = home_address['town']
        county = home_address['county']
        postcode = home_address['postcode']

        lived_abroad = personal_details['lived_abroad']

        # Set up context
        context = {
            'application_id': application_id,
            'title': 'Review: Your personal details',
            # 'form': '',
            'rows': [
                {
                    'id': 'your_name',
                    'name': 'Your name',
                    'info': full_name
                },
                {
                    'id': 'your_date_of_birth',
                    'name': 'Your date of birth',
                    'info': dob_string_with_month
                },
                {
                    'id': 'home_address',
                    'name': 'Home address',
                    'info': {
                        'street_line1': street_line1,
                        'street_line2': street_line2,
                        'town': town,
                        'county': county,
                        'postcode': postcode,
                    }
                },
                {
                    'id': 'lived_abroad',
                    'name': 'Have you lived abroad in the last 5 years?',
                    'info': lived_abroad
                }
            ]

        }

        return context