from ..nanny_forms import form_data
from .nanny_form_builder import NannyFormBuilder

PersonalDetailsForm = NannyFormBuilder(form_data.PERSONAL_DETAILS_DATA,
                                       api_endpoint_name='applicant-personal-details').create_form()
HomeAddressForm = NannyFormBuilder(form_data.HOME_ADDRESS_DATA,
                                   api_endpoint_name='applicant-home-address').create_form()
PreviousRegistrationForm = NannyFormBuilder(form_data.PREVIOUS_REGISTRATION_DATA,
                                            api_endpoint_name='previous-registration-details').create_form()
WhereYouWillWorkForm = NannyFormBuilder(form_data.WHERE_YOU_WILL_WORK_DATA,
                                        api_endpoint_name='application').create_form()
ChildcareAddressFormset = NannyFormBuilder(form_data.CHILDCARE_ADDRESS_DATA,
                                           api_endpoint_name='childcare-address').create_formset()
FirstAidForm = NannyFormBuilder(form_data.FIRST_AID_TRAINING_DATA, api_endpoint_name='first-aid').create_form()
ChildcareTrainingForm = NannyFormBuilder(form_data.CHILDCARE_TRAINING_DATA,
                                         api_endpoint_name='childcare-training').create_form()
DBSForm = NannyFormBuilder(form_data.DBS_CHECK_DATA, api_endpoint_name='dbs-check').create_form()
InsuranceCoverForm = NannyFormBuilder(form_data.INSURANCE_COVER_DATA, api_endpoint_name='insurance-cover').create_form()
