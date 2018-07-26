from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render

from ...forms.childminder_forms.form import DBSCheckForm
from arc_application.models import Application, Arc, CriminalRecordCheck
from arc_application.review_util import redirect_selection, request_to_comment, save_comments
from arc_application.decorators import group_required, user_assigned_application


@login_required
@group_required(settings.ARC_GROUP)
@user_assigned_application
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
            save_successful = save_comments(request, comment_list)
            application = Application.objects.get(pk=application_id_local)

            if not comment_list:
                section_status = 'COMPLETED'
                application.criminal_record_check_arc_flagged = False
            else:
                section_status = 'FLAGGED'
                application.criminal_record_check_arc_flagged = True

            application.save()

            if save_successful:
                status = Arc.objects.get(pk=application_id_local)
                status.dbs_review = section_status
                status.save()
                default = '/people/summary'
                redirect_link = redirect_selection(request, default)

                return HttpResponseRedirect(settings.URL_PREFIX + redirect_link + '?id=' + application_id_local)
            else:
                return render(request, '500.html')

    criminal_record_check = CriminalRecordCheck.objects.get(application_id=application_id_local)
    dbs_certificate_number = criminal_record_check.dbs_certificate_number
    cautions_convictions = criminal_record_check.cautions_convictions
    application = Application.objects.get(pk=application_id_local)
    variables = {
        'form': form,
        'application_id': application_id_local,
        'dbs_certificate_number': dbs_certificate_number,
        'cautions_convictions': cautions_convictions,
        'criminal_record_check_status': application.criminal_record_check_status
    }

    return render(request, 'childminder_templates/dbs-check-summary.html', variables)
