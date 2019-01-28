from django.http import HttpResponse
from django_xhtml2pdf.utils import generate_pdf

from ..models import *
from .childminder_views.arc_summary import load_json, add_comments


def get_document_summary(request):

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
