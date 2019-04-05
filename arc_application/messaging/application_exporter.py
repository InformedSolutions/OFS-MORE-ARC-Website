import json

from django.conf import settings
from django.core import serializers

from ..models import Application, ApplicantName, ApplicantHomeAddress, ApplicantPersonalDetails, AdultInHome, \
    ChildInHome, PreviousName, PreviousAddress, HealthCheckHospital, HealthCheckSerious, HealthCheckCurrent, \
    CriminalRecordCheck, ChildcareType, ChildcareTraining, FirstAidTraining, HealthDeclarationBooklet, \
    PreviousRegistrationDetails, Reference, UserDetails, OtherPersonPreviousRegistrationDetails

from .document_generator import DocumentGenerator

from ..services.db_gateways import NannyGatewayActions, IdentityGatewayActions

from . import SQSHandler

cm_application_sqs_handler = SQSHandler(settings.CM_APPLICATION_QUEUE_NAME)
na_application_sqs_handler = SQSHandler(settings.NA_APPLICATION_QUEUE_NAME)


class ApplicationExporter:

    @staticmethod
    def export_childminder_application(application_id):
        """
        Method for exporting a full application in a dictionary format
        :param application_id: the identifier of the application to be exported
        """

        export = {}

        application = Application.objects.filter(application_id=application_id)
        export['application'] = serializers.serialize('json', list(application))

        adults_in_home = AdultInHome.objects.filter(application_id=application_id).order_by('adult')
        adults_in_home_export = []
        export['adults_in_home'] = serializers.serialize('json', list(adults_in_home))

        # Iterate adults in home, appending prior names and addresses

        for adult_in_home in adults_in_home:
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

        applicant_name = ApplicantName.objects.filter(application_id=application_id)
        export['applicant_name'] = serializers.serialize('json', applicant_name)

        applicant_personal_details = ApplicantPersonalDetails.objects.filter(application_id=application_id)
        export['applicant_personal_details'] = serializers.serialize('json', list(applicant_personal_details))

        applicant_home_address = ApplicantHomeAddress.objects.filter(application_id=application_id)
        export['applicant_home_address'] = serializers.serialize('json', list(applicant_home_address))

        ApplicationExporter.set_moved_in_dates_on_childminder_applicant_home_address(export)

        applicant_previous_names = PreviousName.objects.filter(other_person_type='APPLICANT', person_id=application_id)
        export['applicant_previous_names'] = serializers.serialize('json', list(applicant_previous_names))

        applicant_previous_addresses = PreviousAddress.objects.filter(person_type='APPLICANT', person_id=application_id)
        export['applicant_previous_addresses'] = serializers.serialize('json', list(applicant_previous_addresses))

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
        export['applicant_personal_details'] = json.dumps(applicant_personal_details)

        applicant_home_address = NannyGatewayActions().read('applicant-home-address',
                                                            params={'application_id': application_id}).record
        export['applicant_home_address'] = json.dumps(applicant_home_address)

        ApplicationExporter.set_moved_in_dates_on_nanny_home_address(export)

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
    def set_moved_in_dates_on_childminder_applicant_home_address(export_object):
        """
        Helper method for setting move in dates on an applicant's current address
        :param export_object: The export object to be sent to SQS
        """
        try:
            decoded_home_address = json.loads(export_object['applicant_home_address'])[0]
            decoded_personal_details = json.loads(export_object['applicant_personal_details'])[0]
            decoded_home_address['fields']['moved_in_day'] = decoded_personal_details['fields']['moved_in_day']
            decoded_home_address['fields']['moved_in_month'] = decoded_personal_details['fields']['moved_in_month']
            decoded_home_address['fields']['moved_in_year'] = decoded_personal_details['fields']['moved_in_year']
            export_object['applicant_home_address'] = json.dumps([decoded_home_address])
        except:
            pass

    @staticmethod
    def set_moved_in_dates_on_nanny_home_address(export_object):
        """
        Helper method for setting move in dates on an applicant's current address
        :param export_object: The export object to be sent to SQS
        """
        try:
            decoded_home_address = json.loads(export_object['applicant_home_address'])
            decoded_personal_details = json.loads(export_object['applicant_personal_details'])
            decoded_home_address['moved_in_date'] = decoded_personal_details['moved_in_date']
            export_object['applicant_home_address'] = json.dumps(decoded_home_address)
        except:
            pass
