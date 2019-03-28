import logging
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render

from ...childminder_task_util import get_show_people_in_the_home, get_show_references
from ...forms.childminder_forms.form import DBSCheckForm
from ...models import Application, Arc, CriminalRecordCheck
from ...review_util import redirect_selection, request_to_comment, save_comments
from ...decorators import group_required, user_assigned_application

# Initiate logging
log = logging.getLogger('')

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

                show_people_in_the_home = get_show_people_in_the_home(application_id_local)
                show_references = get_show_references(application_id_local)

                if show_people_in_the_home:
                    default = '/people/summary'
                    log.debug("Conditional logic - Direct to people in the home task next")
                elif show_references:
                    default = '/references/summary'
                    log.debug("Conditional logic - Direct to references task next")
                else:
                    default = '/review'
                    log.debug("Conditional logic - Direct to review task next")

                redirect_link = redirect_selection(request, default)

                log.debug("Handling submissions for criminal record check page - save successful")
                return HttpResponseRedirect(settings.URL_PREFIX + redirect_link + '?id=' + application_id_local)
            else:
                log.debug("Handling submissions for criminal record check page - save unsuccessful")
                return render(request, '500.html')

    criminal_record_check = CriminalRecordCheck.objects.get(application_id=application_id_local)
    dbs_certificate_number = criminal_record_check.dbs_certificate_number
    cautions_convictions = criminal_record_check.cautions_convictions
    lived_abroad = criminal_record_check.lived_abroad
    military_base = criminal_record_check.military_base
    capita = criminal_record_check.capita
    on_update = criminal_record_check.on_update
    application = Application.objects.get(pk=application_id_local)
    within_three_months = criminal_record_check.within_three_months
    enhanced_check = criminal_record_check.enhanced_check

    form.error_summary_title = 'There was a problem'
    variables = {
        'form': form,
        'application_id': application_id_local,
        'dbs_certificate_number': dbs_certificate_number,
        'cautions_convictions': cautions_convictions,
        'criminal_record_check_status': application.criminal_record_check_status,
        'lived_abroad': lived_abroad,
        'military_base': military_base,
        'capita': capita,
        'on_update': on_update,
        'within_three_months': within_three_months,
        'enhanced_check': enhanced_check,
    }

    log.debug("Rendering criminal record check page")
    return render(request, 'childminder_templates/dbs-check-summary.html', variables)
