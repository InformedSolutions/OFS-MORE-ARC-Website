from ...forms.nanny_forms.nanny_form_builder import HomeAddressForm, PersonalDetailsForm
from ...services.db_gateways import NannyGatewayActions
from .nanny_form_view import NannyARCFormView

from .nanny_view_helpers import parse_date_of_birth


class NannyPersonalDetailsSummary(NannyARCFormView):
    template_name = 'nanny_general_template.html'
    success_url = 'nanny_childcare_address_summary'
    task_for_review = 'personal_details_review'
    form_class = [PersonalDetailsForm, HomeAddressForm]

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

        month = month_list[int(birth_month) - 1]

        return "{0} {1} {2}".format(birth_day, month, birth_year)

    def get_context_data(self, application_id):
        """
        Creates the context dictionary for this view.
        :param application_id: Reviewed application's id.
        :return: Context dictionary.
        """
        self.application_id = application_id
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

        forms = self.get_forms()
        personal_details_form = forms[0]
        home_address_form = forms[1]

        context = {
            'application_id': application_id,
            'title': 'Review: Your personal details',
            'rows': [
                {
                    'id': 'name',
                    'name': 'Your name',
                    'info': full_name,
                    'declare': personal_details_form['name_declare'] if hasattr(self, 'request') else '',
                    'comments': personal_details_form['name_comments'] if hasattr(self, 'request') else '',
                },
                {
                    'id': 'date_of_birth',
                    'name': 'Your date of birth',
                    'info': dob_string_with_month,
                    'declare': personal_details_form['date_of_birth_declare'] if hasattr(self, 'request') else '',
                    'comments': personal_details_form['date_of_birth_comments'] if hasattr(self, 'request') else '',
                },
                {
                    'id': 'home_address',
                    'name': 'Home address',
                    'declare': home_address_form['home_address_declare'] if hasattr(self, 'request') else '',
                    'comments': home_address_form['home_address_comments'] if hasattr(self, 'request') else '',
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
                    'info': lived_abroad,
                    'declare': personal_details_form['lived_abroad_declare'] if hasattr(self, 'request') else '',
                    'comments': personal_details_form['lived_abroad_comments'] if hasattr(self, 'request') else '',
                }
            ]
        }

        return context