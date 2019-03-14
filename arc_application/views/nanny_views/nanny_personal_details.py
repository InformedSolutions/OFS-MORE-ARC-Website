import datetime

from .nanny_form_view import NannyARCFormView
from ...forms.nanny_forms.nanny_form_builder import HomeAddressForm, PersonalDetailsForm, PreviousRegistrationForm
from ...services.db_gateways import NannyGatewayActions


class NannyPersonalDetailsSummary(NannyARCFormView):
    template_name = 'nanny_personal_details_summary.html'
    task_for_review = 'personal_details_review'
    verbose_task_name = 'Your personal details'

    # def get_initial(self):
    #     initial = {}
    #     application_id = self.request.GET.get('id')
    #     previous_registration_details = NannyGatewayActions().read('previous-registration-details',
    #                                                        params={'application_id': application_id})
    #     if previous_registration_details.status_code != 404:
    #         self.form_class = [PersonalDetailsForm, HomeAddressForm, PreviousRegistrationForm]
    #     else:
    #         self.form_class = [PersonalDetailsForm, HomeAddressForm]
    #
    #         return initial

    def get_form_class(self, **kwargs):
        if hasattr(self, 'request'):
            application_id = self.request.GET.get('id')
        else:
            application_id = kwargs.pop('application_id')

        previous_registration_details = NannyGatewayActions().read('previous-registration-details',
                                                                   params={'application_id': application_id})
        if previous_registration_details.status_code != 404:
            return [PersonalDetailsForm, HomeAddressForm, PreviousRegistrationForm]
        else:
            return [PersonalDetailsForm, HomeAddressForm]

    @staticmethod
    def month_converter(dob_string):
        """
        Converts a numerical month into the related string month.
        :param dob_string: a Date Of Birth string in the format 'YYYY-MM-DD'
        :return: a DOB string in format 'DD-Month-YYYY'
        """
        birth_datetime = datetime.datetime.strptime(dob_string, '%Y-%m-%d')

        return birth_datetime.strftime('%d %b %Y')

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
        previous_registration_details = nanny_actions.read('previous-registration-details',
                                          params={'application_id': application_id})



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

        known_to_social_services = personal_details['known_to_social_services']

        reasons_known_to_social_services = personal_details['reasons_known_to_social_services']

        previous_registration_record_exists = False

        forms = self.get_forms(application_id)
        personal_details_form = forms[0]
        home_address_form = forms[1]

        if previous_registration_details.status_code != 404:
            previous_registration_record_exists = True
            previous_registration_details = nanny_actions.read('previous-registration-details',
                                                               params={'application_id': application_id}).record
            previous_registration = previous_registration_details['previous_registration']
            individual_id = str(previous_registration_details['individual_id'])
            five_years_in_UK = previous_registration_details['five_years_in_UK']
            previous_registration_form = forms[2]



        context = {
            'application_id': application_id,
            'title': 'Review: ' + self.verbose_task_name,
            'show_previous_registration':  previous_registration_record_exists,
            'change_link': 'nanny_personal_details_summary',
            'rows': [
                {
                    'id': 'name',
                    'name': 'Your name',
                    'info': full_name,
                    # Prevent checkbox appearing if summary page is calling get_context_data.
                    'declare': personal_details_form['name_declare'] if hasattr(self, 'request') else '',
                    'comments': personal_details_form['name_comments'],
                },
                {
                    'id': 'date_of_birth',
                    'name': 'Date of birth',
                    'info': dob_string_with_month,
                    'declare': personal_details_form['date_of_birth_declare'] if hasattr(self, 'request') else '',
                    'comments': personal_details_form['date_of_birth_comments'],
                },
                {
                    'id': 'home_address',
                    'name': 'Your home address',
                    'declare': home_address_form['home_address_declare'] if hasattr(self, 'request') else '',
                    'comments': home_address_form['home_address_comments'],
                    'info': {
                        'street_line1': street_line1,
                        'street_line2': street_line2,
                        'town': town,
                        'county': county,
                        'postcode': postcode,
                    }
                },
                {
                    'id': 'known_to_social_services',
                    'name': 'Known to council social Services?',
                    'info': known_to_social_services,
                    'declare': personal_details_form['known_to_social_services_declare'] if hasattr(self,
                                                                                                    'request') else '',
                    'comments': personal_details_form['known_to_social_services_comments'],

                }
            ]
        }

        if known_to_social_services is True:
            context['rows'].append(
                {
                    'id': 'reasons_known_to_social_services',
                    'name': 'Tell us why',
                    'info': reasons_known_to_social_services,
                    'declare': personal_details_form['reasons_known_to_social_services_declare'] if hasattr(self,
                                                                                                            'request') else '',
                    'comments': personal_details_form['reasons_known_to_social_services_comments'],
                }
            )

        if previous_registration_record_exists is True:
            context['rows'].append(
                {
                    'id': 'previous_registration',
                    'name': 'Previously registered with Ofsted?',
                    'info': previous_registration,
                    'declare': previous_registration_form['previous_registration_declare'] if hasattr(self,
                                                                                                      'request') else '',
                    'comments': previous_registration_form['previous_registration_comments'],
                })
            if previous_registration is True:
                context['rows'].append(
                    {
                        'id': 'individual_id',
                        'name': 'Individual ID',
                        'info': individual_id,
                        'declare': previous_registration_form['individual_id_declare'] if hasattr(self, 'request') else '',
                        'comments': previous_registration_form['individual_id_comments'],
                    })
            context['rows'].append(
                {
                    'id': 'five_years_in_UK',
                    'name': 'Lived in England for more than 5 years?',
                    'info': five_years_in_UK,
                    'declare': previous_registration_form['five_years_in_UK_declare'] if hasattr(self,
                                                                                                 'request') else '',
                    'comments': previous_registration_form['five_years_in_UK_comments'],
                })

        return context

    def get_forms(self, application_id):
        return [self.get_form(form_class=form_class) for form_class in self.get_form_class(application_id=application_id)]

    def get_success_url(self):
        return 'nanny_childcare_address_summary'
