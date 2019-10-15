import json

from django.conf import settings
from django.core import serializers

from ..models import Application, ApplicantName, ApplicantHomeAddress, ApplicantPersonalDetails, AdultInHome, \
    ChildInHome, PreviousName, PreviousAddress, HealthCheckHospital, HealthCheckSerious, HealthCheckCurrent, \
    CriminalRecordCheck, ChildcareType, ChildcareTraining, FirstAidTraining, HealthDeclarationBooklet, \
    PreviousRegistrationDetails, Reference, UserDetails, OtherPersonPreviousRegistrationDetails

from .document_generator import DocumentGenerator

from ..services.db_gateways import NannyGatewayActions, IdentityGatewayActions, HMGatewayActions
from ..utils import get_title_data, TITLE_OPTIONS

from . import SQSHandler

cm_application_sqs_handler = SQSHandler(settings.CM_APPLICATION_QUEUE_NAME)
na_application_sqs_handler = SQSHandler(settings.NA_APPLICATION_QUEUE_NAME)
adult_update_application_sqs_handler = SQSHandler(settings.ADDITIONAL_ADULT_APPLICATION_QUEUE_NAME)


class ApplicationExporter:

    @staticmethod
    def export_childminder_application(application_id):
        """
        Method for exporting a full application in a dictionary format
        :param application_id: the identifier of the application to be exported
        """

        export = {}
        export['application_type'] = json.dumps('Childminder')
        application = Application.objects.filter(application_id=application_id)
        export['application'] = serializers.serialize('json', list(application))

        adults_in_home = AdultInHome.objects.filter(application_id=application_id).order_by('adult')
        adults_in_home_export = []
        export['adults_in_home'] = serializers.serialize('json', list(adults_in_home))

        # Iterate adults in home, appending prior names and addresses

        for adult_in_home in adults_in_home:
            if adult_in_home.title not in TITLE_OPTIONS:
                adult_in_home.other_title= adult_in_home.title
                adult_in_home.title = 'Other'
                adult_in_home.save()
                adults_in_home = AdultInHome.objects.filter(application_id=application_id).order_by('adult')
                export['adults_in_home'] = serializers.serialize('json', list(adults_in_home))
            previous_name = PreviousName.objects.filter(person_id=adult_in_home.pk)
            previous_address = PreviousAddress.objects.filter(person_id=adult_in_home.pk)
            serious_illness = HealthCheckSerious.objects.filter(person_id=adult_in_home.pk)
            hospital_admissions = HealthCheckHospital.objects.filter(person_id=adult_in_home.pk)
            current_illnesses = HealthCheckCurrent.objects.filter(person_id=adult_in_home.pk)
            previous_registrations = OtherPersonPreviousRegistrationDetails.objects.filter(person_id_id=adult_in_home.pk)

            adults_in_home_export.append({
                'adult': adult_in_home.adult,
                'previous_names': serializers.serialize('json', list(previous_name)),
                'previous_address': serializers.serialize('json', list(previous_address)),
                'previous_registrations': serializers.serialize('json', list(previous_registrations)),
                'serious_illness': serializers.serialize('json', list(serious_illness)),
                'hospital_admissions': serializers.serialize('json', list(hospital_admissions)),
                'current_illnesses': serializers.serialize('json', list(current_illnesses))
            })

        export['additional_adult_details'] = json.dumps(adults_in_home_export)

        applicant_name = ApplicantName.objects.get(application_id=application_id)
        if applicant_name.title not in TITLE_OPTIONS:
            applicant_name.other_title = applicant_name.title
            applicant_name.title = 'Other'
            applicant_name.save()

        applicant_name = ApplicantName.objects.filter(application_id=application_id)
        export['applicant_name'] = serializers.serialize('json', list(applicant_name))

        applicant_personal_details = ApplicantPersonalDetails.objects.filter(application_id=application_id)
        export['applicant_personal_details'] = serializers.serialize('json', list(applicant_personal_details))

        applicant_home_address = ApplicantHomeAddress.objects.filter(application_id=application_id,
                                                                     current_address=True)
        export['applicant_home_address'] = serializers.serialize('json', list(applicant_home_address))

        applicant_previous_names = PreviousName.objects.filter(other_person_type='APPLICANT', person_id=application_id)
        export['applicant_previous_names'] = serializers.serialize('json', list(applicant_previous_names))

        applicant_previous_addresses = PreviousAddress.objects.filter(person_type='APPLICANT', person_id=application_id)
        export['applicant_previous_addresses'] = serializers.serialize('json', list(applicant_previous_addresses))

        childcare_address = ApplicantHomeAddress.objects.filter(personal_detail_id=applicant_personal_details.first(),
                                                                childcare_address=True)
        export['childcare_address'] = serializers.serialize('json', list(childcare_address))

        child_in_home = ChildInHome.objects.filter(application_id=application_id)
        export['child_in_home'] = serializers.serialize('json', list(child_in_home))

        childcare_type = ChildcareType.objects.filter(application_id=application_id)
        export['childcare_type'] = serializers.serialize('json', list(childcare_type))

        criminal_record_check = CriminalRecordCheck.objects.filter(application_id=application_id)
        export['criminal_record_check'] = serializers.serialize('json', list(criminal_record_check))

        eyfs = ChildcareTraining.objects.filter(application_id=application_id)
        export['eyfs'] = serializers.serialize('json', list(eyfs))

        first_aid_training = FirstAidTraining.objects.filter(application_id=application_id)
        export['first_aid_training'] = serializers.serialize('json', list(first_aid_training))

        health_declaration_booklet = HealthDeclarationBooklet.objects.filter(application_id=application_id)
        export['health_declaration_booklet'] = serializers.serialize('json', list(health_declaration_booklet))

        previous_registration_details = PreviousRegistrationDetails.objects.filter(application_id=application_id)
        export['previous_registration'] = serializers.serialize('json', list(previous_registration_details))

        references = Reference.objects.filter(application_id=application_id)
        for reference in references:
            if reference.title not in TITLE_OPTIONS:
                reference.other_title = reference.title
                reference.title = 'Other'
                reference.save()
                references = Reference.objects.filter(application_id=application_id)
        export['references'] = serializers.serialize('json', list(references))

        user_details = UserDetails.objects.filter(application_id=application_id)
        export['user_details'] = serializers.serialize('json', list(user_details))

        # Create document exports

        documents = {'EYC': DocumentGenerator.get_full_childminder_application_summary(application_id)}

        # If adults in home are present, append EY2 documents
        if len(adults_in_home):

            adult_documents = []

            for adult in adults_in_home:
                base64_string = DocumentGenerator.get_adult_details_summary(application_id, adult.adult_id)

                adult_document_object = {
                    "adult_id": str(adult.adult_id),
                    "document": base64_string,
                }

                adult_documents.append(adult_document_object)

            documents['EY2'] = adult_documents

        export['documents'] = json.dumps(documents)

        cm_application_sqs_handler.send_message(export)

    @staticmethod
    def export_nanny_application(application_id, application_reference):
        """
        Method for exporting a full nanny application in a dictionary format
        :param application_id: the identifier of the application to be exported
        :param application_reference: the customer facing reference number assigned to an application
        """

        export = {}

        application = NannyGatewayActions().read('application', params={'application_id': application_id}).record

        export['application'] = json.dumps(application)

        # Try fetch childcare address if it exists
        childcare_addresses = NannyGatewayActions().list('childcare-address',
                                                         params={'application_id': application_id})

        if childcare_addresses.status_code == 404:
            export['childcare_addresses'] = json.dumps({})
        else:
            export['childcare_addresses'] = json.dumps(childcare_addresses.record)

        applicant_personal_details = NannyGatewayActions().read('applicant-personal-details',
                                                                params={'application_id': application_id}).record
        applicant_personal_details  = get_title_data(applicant_personal_details)
        export['applicant_personal_details'] = json.dumps(applicant_personal_details)

        applicant_home_address = NannyGatewayActions().read('applicant-home-address',
                                                            params={'application_id': application_id}).record
        export['applicant_home_address'] = json.dumps(applicant_home_address)

        childcare_training = NannyGatewayActions().read('childcare-training',
                                                        params={'application_id': application_id}).record
        export['childcare_training'] = json.dumps(childcare_training)

        criminal_record_check = NannyGatewayActions().read('dbs-check',
                                                           params={'application_id': application_id}).record
        export['criminal_record_check'] = json.dumps(criminal_record_check)

        first_aid_training = NannyGatewayActions().read('first-aid', params={'application_id': application_id}).record
        export['first_aid_training'] = json.dumps(first_aid_training)

        insurance_declaration = NannyGatewayActions().read('insurance-cover',
                                                           params={'application_id': application_id}).record
        export['insurance_declaration'] = json.dumps(insurance_declaration)

        # In the event no previous registrations, names or addresses have been listed, the below methods will 404.
        # Explicit case handling is included for this. Other errors (500 etc.) will cause exception to be raised
        # as the record property will be absent.

        previous_registration_details = NannyGatewayActions().read('previous-registration-details',
                                                                       params={'application_id': application_id})

        if previous_registration_details.status_code == 404:
            export['previous_registration'] = json.dumps({})
        else:
            export['previous_registration'] = json.dumps(previous_registration_details.record)

        previous_names = NannyGatewayActions().list('previous-name', params={'application_id': application_id})

        if previous_names.status_code == 404:
            export['applicant_previous_names'] = json.dumps({})
        else:
            export['applicant_previous_names'] = json.dumps(previous_names.record)

        previous_addresses = NannyGatewayActions().list('previous-address',
                                   params={'person_id': application_id, 'person_type': 'APPLICANT'})

        if previous_addresses.status_code == 404:
            export['applicant_previous_addresses'] = json.dumps({})
        else:
            export['applicant_previous_addresses'] = json.dumps(previous_addresses.record)

        user_details = IdentityGatewayActions().read('user', params={'application_id': application_id}).record
        export['user_details'] = json.dumps(user_details)

        documents = {
            'CR': DocumentGenerator.get_full_nanny_application_summary(application_id, application_reference)
        }

        export['documents'] = json.dumps(documents)

        na_application_sqs_handler.send_message(export)

    @staticmethod
    def export_adult_update_application(adult_id):
        export = {}
        adult_details_export = {}
        additional_adult_details_export = {}

        adult_record = HMGatewayActions().read('adult', params={'adult_id': adult_id}).record

        dpa_auth_id = adult_record['token_id']
        dpa_record = HMGatewayActions().read('dpa-auth', params={'token_id': dpa_auth_id}).record

        setting_address_record = HMGatewayActions().read('setting-address', params={'token_id': dpa_auth_id}).record

        urn = dpa_record['URN']
        registration_id = dpa_record['registration_id']
        date_accepted = adult_record['date_accepted']

        adult_details_export['pk'] = adult_id
        adult_details_export['fields'] = get_title_data(adult_record)

        additional_adult_details_export['adult'] = int(adult_record['order'])

        if adult_record['currently_being_treated']:
            current_illnesses = json.dumps(adult_record['illness_details'])
        else:
            current_illnesses = json.dumps([])

        adult_details_export['fields']['current_treatment'] = adult_record['currently_being_treated']
        additional_adult_details_export['current_treatments'] = current_illnesses

        if adult_record['has_serious_illness']:
            serious_illnesses_record = HMGatewayActions().list('serious-illness', params={'adult_id': adult_id}).record
            serious_illnesses = json.dumps([{'fields': r} for r in serious_illnesses_record])
        else:
            serious_illnesses = json.dumps([])

        adult_details_export['fields']['serious_illness'] = adult_record['has_serious_illness']
        additional_adult_details_export['serious_illness'] = serious_illnesses

        if adult_record['has_hospital_admissions']:
            hospital_admissions_record = HMGatewayActions().list("hospital-admissions", params={'adult_id': adult_id}).record
            hospital_admissions = json.dumps([{'fields': r} for r in hospital_admissions_record])
        else:
            hospital_admissions = json.dumps([])

        adult_details_export['fields']['hospital_admission'] = adult_record['has_hospital_admissions']
        additional_adult_details_export['hospital_admissions'] = hospital_admissions

        previous_names_response = HMGatewayActions().list('previous-name', params={'adult_id': adult_id})

        if previous_names_response.status_code == 200:
            additional_adult_details_export['previous_names'] = json.dumps([{'fields': r} for r in previous_names_response.record])
        else:
            additional_adult_details_export['previous_names'] = json.dumps([])

        previous_address_response = HMGatewayActions().list('previous-address', params={'adult_id': adult_id})

        if previous_address_response.status_code == 200:
            additional_adult_details_export['previous_address'] = json.dumps([{'fields': r} for r in previous_address_response.record])
        else:
            additional_adult_details_export['previous_address'] = json.dumps([])

        previous_reg_response = HMGatewayActions().list('previous-registration', params={'adult_id': adult_id})

        if previous_reg_response.status_code == 200:
            additional_adult_details_export['previous_registrations'] = json.dumps([{'fields': r} for r in previous_reg_response.record])
        else:
            additional_adult_details_export['previous_registrations'] = json.dumps([])

        adult_document_object = {
            'adult_id': str(adult_id),
            'document': DocumentGenerator.get_adult_update_application_summary(adult_id),
        }

        export['application'] = json.dumps([{'fields': {'application_reference': urn, 'registration_id': registration_id, 'date_accepted': date_accepted}}])
        export['childcare_address'] = json.dumps([{'fields': setting_address_record}])
        export['adults_in_home'] = json.dumps([adult_details_export])
        export['additional_adult_details'] = json.dumps([additional_adult_details_export])
        export['documents'] = json.dumps({'EY2': [adult_document_object]})

        adult_update_application_sqs_handler.send_message(export)
