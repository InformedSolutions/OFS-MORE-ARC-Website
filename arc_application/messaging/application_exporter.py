import json

from django.conf import settings
from django.core import serializers

from ..models import Application, ApplicantName, ApplicantHomeAddress, ApplicantPersonalDetails,  AdultInHome, \
    ChildInHome, PreviousName, PreviousAddress, HealthCheckHospital, HealthCheckSerious, HealthCheckCurrent, \
    CriminalRecordCheck, ChildcareType, ChildcareTraining, FirstAidTraining, HealthDeclarationBooklet, \
    PreviousRegistrationDetails, Reference, UserDetails

from .document_generator import DocumentGenerator

from . import SQSHandler

sqs_handler = SQSHandler(settings.APPLICATION_QUEUE_NAME)


class ApplicationExporter:

    @staticmethod
    def export_childminder_application(application_id):
        payload = ApplicationExporter.create_full_application_export(application_id)
        sqs_handler.send_message(payload)

    @staticmethod
    def create_full_application_export(application_id):
        """
        Method for exporting a full application in a dictionary format
        :param application_id: the identifier of the application to be exported
        :return: a dictionary export of an application
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

            adults_in_home_export.append({
                'adult': adult_in_home.adult,
                'previous_names': serializers.serialize('json', list(previous_name)),
                'previous_address': serializers.serialize('json', list(previous_address)),
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

        documents = {}

        base64_string = DocumentGenerator.get_full_application_summary(application_id)

        documents['EYC'] = base64_string

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

        return export