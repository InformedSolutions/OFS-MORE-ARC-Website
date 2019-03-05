import base64

from django.http import HttpResponse
from django_xhtml2pdf.utils import generate_pdf

from ..models import Application, AdultInHome, \
    HealthCheckHospital, HealthCheckSerious, HealthCheckCurrent

from ..views.childminder_views.arc_summary import get_application_summary_variables


class DocumentGenerator:

    @staticmethod
    def get_full_application_summary(application_id):
        """
        Generates a full application summary in a PDF format that has been base64 encoded
        (for EYC portions of a document submission to NOO)
        """
        resp = HttpResponse(content_type='application/pdf')
        variables = get_application_summary_variables(application_id, apply_filtering_for_eyc=True)
        result = generate_pdf('pdf-summary.html', file_object=resp, context=variables)
        base64_string = str(base64.b64encode(result.content).decode("utf-8"))
        return base64_string

    @staticmethod
    def get_adult_details_summary(application_id, adult_id):
        """
        Generates a summary of household member details in a PDF format that has been base64 encoded
        (for EY2 portions of a document submission to NOO)
        """
        resp = HttpResponse(content_type='application/pdf')

        application = Application.objects.get(application_id=application_id)
        application_reference = application.application_reference

        adult = AdultInHome.objects.get(adult_id=adult_id)

        summary_table = [adult.get_summary_table()]
        current_illnesses = HealthCheckCurrent.objects.filter(person_id=adult_id)
        serious_illnesses = HealthCheckSerious.objects.filter(person_id=adult_id)
        hospital_admissions = HealthCheckHospital.objects.filter(person_id=adult_id)

        current_illnesses_list = [{"title": "Current Treatment", "id": adult_id},
                                  {"name": "Current Treatment",
                                   "value": ("Yes" if adult.current_treatment == True else "No")}]
        for record in current_illnesses:
            current_illnesses_list.append({"name": "Description", "value": record.description})
        summary_table.append(current_illnesses_list)

        serious_illnesses_list = [{"title": "Serious Illnesses", "id": adult_id},
                                  {"name": "Serious Illness",
                                   "value": ("Yes" if adult.serious_illness == True else "No")}]
        for record in serious_illnesses:
            serious_illnesses_list.append({"name": "Description", "value": record.description})
            serious_illnesses_list.append({"name": "Start Date", "value": record.start_date})
            serious_illnesses_list.append({"name": "End Date", "value": record.end_date})
        summary_table.append(serious_illnesses_list)

        hospital_admissions_list = [{"title": "Hospital Admissions", "id": adult_id},
                                    {"name": "Hospital Admissions",
                                     "value": ("Yes" if adult.hospital_admission == True else "No")}
                                    ]
        for record in hospital_admissions:
            hospital_admissions_list.append({"name": "Description", "value": record.description})
            hospital_admissions_list.append({"name": "Start Date", "value": record.start_date})
            hospital_admissions_list.append({"name": "End Date", "value": record.end_date})
        summary_table.append(hospital_admissions_list)

        variables = {
            'json': summary_table,
            'adult_id': adult_id,
            'application_id': application_id,
            'application_reference': application_reference,
        }

        result = generate_pdf('pdf-summary.html', file_object=resp, context=variables)
        base64_string = str(base64.b64encode(result.content).decode("utf-8"))
        return base64_string
