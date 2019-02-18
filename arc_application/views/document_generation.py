from django.http import HttpResponse
from django_xhtml2pdf.utils import generate_pdf

from ..models import *
from .childminder_views.arc_summary import load_json, add_comments


def get_full_application_summary(request):

    """
    Renders a full application summary in a PDF format
    """

    resp = HttpResponse(content_type='application/pdf')

    ordered_models = [UserDetails, ChildcareType, [ApplicantPersonalDetails, ApplicantName], ApplicantHomeAddress,
                      FirstAidTraining, ChildcareTraining, CriminalRecordCheck]

    if request.method == 'GET':
        application_id_local = request.GET["id"]
        # Only display People in your Home tables if the applicant does not work in another childminder's home
        application = Application.objects.get(application_id=application_id_local)

        if application.working_in_other_childminder_home is False:
            ordered_models.append(AdultInHome)
            ordered_models.append(Application)
            ordered_models.append(ChildInHome)
            ordered_models.append(Child)
        zero_to_five = ChildcareType.objects.get(application_id=application_id_local).zero_to_five

        if zero_to_five:
            ordered_models.insert(6, HealthDeclarationBooklet)
            ordered_models.append(Reference)
        json = load_json(application_id_local, ordered_models, False)
        json = add_comments(json, application_id_local)

        application_reference = application.application_reference
        publish_details = application.publish_details

        variables = {
            'json': json,
            'application_id': application_id_local,
            'application_reference': application_reference,
            'publish_details': publish_details
        }

        result = generate_pdf('pdf-summary.html', file_object=resp, context=variables)
        return result

# Need a method here for creating a PDF for the information entered by an adult on their health questionnaires
# e.g. Illnesses, Hospital admissions etc

def get_adult_details_summary(request):

    resp = HttpResponse(content_type='application/pdf')

    if request.method == 'GET':
        application_id_local = request.GET["id"]
        application = Application.objects.get(application_id=application_id_local)
        application_reference = application.application_reference
        adult_id_local = request.GET["adult_id"]
        adult= AdultInHome.objects.get(adult_id=adult_id_local)

        summary_table = [adult.get_summary_table()]
        current_illnesses = HealthCheckCurrent.objects.filter(person_id=adult_id_local)
        serious_illnesses = HealthCheckSerious.objects.filter(person_id=adult_id_local)
        hospital_admissions = HealthCheckHospital.objects.filter(person_id=adult_id_local)

        if adult.current_treatment:
            current_illnesses_list = [{"title": "Current Treatment", "id": adult_id_local}]
            for record in current_illnesses:
                current_illnesses_list.append({"name": "Description", "value": record.description})
            summary_table.append(current_illnesses_list)

        if adult.serious_illness:
            serious_illnesses_list = [{"title": "Serious Illnesses", "id": adult_id_local}]
            for record in serious_illnesses:
                serious_illnesses_list.append({"name": "Description", "value": record.description})
                serious_illnesses_list.append({"name": "Start Date", "value": record.start_date})
                serious_illnesses_list.append({"name": "End Date", "value": record.end_date})
            summary_table.append(serious_illnesses_list)

        if adult.hospital_admission:
            hospital_admissions_list = [{"title": "Hospital Admissions", "id": adult_id_local}]
            for record in hospital_admissions:
                hospital_admissions_list.append({"name": "Description", "value": record.description})
                hospital_admissions_list.append({"name": "Start Date", "value": record.start_date})
                hospital_admissions_list.append({"name": "End Date", "value": record.end_date})
            summary_table.append(hospital_admissions_list)

        variables = {
            'json':  summary_table,
            'adult_id': adult_id_local,
            'application_id': application_id_local,
            'application_reference': application_reference,
        }

        result = generate_pdf('pdf-summary.html', file_object=resp, context=variables)
        return result


# Steps are effectively to build up data object including all the bits from the questionnaire
# Push them into PDF using same approach as above

