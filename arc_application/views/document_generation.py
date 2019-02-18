from django.http import HttpResponse
from django_xhtml2pdf.utils import generate_pdf

from ..models import *
from .childminder_views.arc_summary import get_application_summary_variables


def get_full_application_summary(request):

    """
    Renders a full application summary in a PDF format
    """

    resp = HttpResponse(content_type='application/pdf')

    if request.method == 'GET':
        application_id_local = request.GET["id"]
        variables = get_application_summary_variables(application_id_local)
        result = generate_pdf('pdf-summary.html', file_object=resp, context=variables)
        return result


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

        current_illnesses_list = [{"title": "Current Treatment", "id": adult_id_local},
                                  {"name":"Current Treatment", "value":("Yes" if adult.current_treatment == True else "No")}]
        for record in current_illnesses:
            current_illnesses_list.append({"name": "Description", "value": record.description})
        summary_table.append(current_illnesses_list)

        serious_illnesses_list = [{"title": "Serious Illnesses", "id": adult_id_local},
                                  {"name":"Serious Illness", "value":("Yes" if adult.serious_illness == True else "No")}]
        for record in serious_illnesses:
            serious_illnesses_list.append({"name": "Description", "value": record.description})
            serious_illnesses_list.append({"name": "Start Date", "value": record.start_date})
            serious_illnesses_list.append({"name": "End Date", "value": record.end_date})
        summary_table.append(serious_illnesses_list)

        hospital_admissions_list = [{"title": "Hospital Admissions", "id": adult_id_local},
                                    {"name": "Hospital Admissions",
                                     "value": ("Yes" if adult.hospital_admission == True else "No")}
                                    ]
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

