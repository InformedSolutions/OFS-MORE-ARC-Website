from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render

from ..forms.form import DBSCheckForm
from ..models import Application, Arc, CriminalRecordCheck
from ..review_util import redirect_selection, request_to_comment, save_comments


def dbs_check_summary(request):
    """
    Method returning the template for the Your criminal record (DBS) check: summary page (for a given application)
    displaying entered data for this task and navigating to the task list when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your criminal record (DBS) check: summary template
    """
    table_name = 'CRIMINAL_RECORD_CHECK'

    if request.method == 'GET':
        application_id_local = request.GET["id"]
        criminal_record_id = CriminalRecordCheck.objects.get(application_id=application_id_local).criminal_record_id

        form = DBSCheckForm(table_keys=[criminal_record_id])
    elif request.method == 'POST':
        application_id_local = request.POST["id"]
        criminal_record_id = CriminalRecordCheck.objects.get(application_id=application_id_local).criminal_record_id
        form = DBSCheckForm(request.POST, table_keys=[criminal_record_id])

        if form.is_valid():
            comment_list = request_to_comment(criminal_record_id, table_name, form.cleaned_data)
            save_successful = save_comments(comment_list)

            if not comment_list:
                section_status = 'COMPLETED'
            else:
                section_status = 'FLAGGED'

            if save_successful:
                status = Arc.objects.get(pk=application_id_local)
                status.dbs_review = section_status
                status.save()
                default = '/health/check-answers'
                redirect_link = redirect_selection(request, default)

                return HttpResponseRedirect(settings.URL_PREFIX + redirect_link + '?id=' + application_id_local)
            else:
                return render(request, '500.html')

    criminal_record_check = CriminalRecordCheck.objects.get(application_id=application_id_local)
    dbs_certificate_number = criminal_record_check.dbs_certificate_number
    cautions_convictions = criminal_record_check.cautions_convictions
    send_certificate_declare = criminal_record_check.send_certificate_declare
    application = Application.objects.get(pk=application_id_local)
    variables = {
        'form': form,
        'application_id': application_id_local,
        'dbs_certificate_number': dbs_certificate_number,
        'cautions_convictions': cautions_convictions,
        'criminal_record_check_status': application.criminal_record_check_status,
        'declaration': send_certificate_declare
    }

    return render(request, 'dbs-check-summary.html', variables)