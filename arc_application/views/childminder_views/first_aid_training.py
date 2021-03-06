import logging
import sys
from time import asctime

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render

from ...forms.childminder_forms.form import FirstAidTrainingForm
from ...models import Application, Arc, FirstAidTraining
from ...review_util import redirect_selection, request_to_comment, save_comments
from ...decorators import group_required, user_assigned_application

# Initiate logging
log = logging.getLogger()

@login_required
@group_required(settings.ARC_GROUP)
@user_assigned_application
def first_aid_training_summary(request):
    """
    Method returning the template for the First aid training: summary page (for a given application)
    displaying entered data for this task and navigating to the task list when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered First aid training: summary template
    """
    table_name = 'FIRST_AID_TRAINING'

    if request.method == 'GET':
        application_id_local = request.GET["id"]
        first_aid_id = FirstAidTraining.objects.get(application_id=application_id_local).first_aid_id
        form = FirstAidTrainingForm(table_keys=[first_aid_id])
    elif request.method == 'POST':
        application_id_local = request.POST["id"]
        first_aid_id = FirstAidTraining.objects.get(application_id=application_id_local).first_aid_id
        form = FirstAidTrainingForm(request.POST, table_keys=[application_id_local])

        if form.is_valid():
            comment_list = request_to_comment(first_aid_id, table_name, form.cleaned_data)
            save_successful = save_comments(request, comment_list)

            application = Application.objects.get(pk=application_id_local)

            if not comment_list:
                section_status = 'COMPLETED'
                application.first_aid_training_arc_flagged = False
            else:
                section_status = 'FLAGGED'
                application.first_aid_training_arc_flagged = True

            application.save()

            if save_successful:
                status = Arc.objects.get(pk=application_id_local)
                status.first_aid_review = section_status
                status.save()
                default = '/childcare-training-check/summary/'
                redirect_link = redirect_selection(request, default)

                log.debug("Handling submissions for first aid training page - save successful")
                return HttpResponseRedirect(settings.URL_PREFIX + redirect_link + '?id=' + application_id_local)
            else:
                log.debug("Handling submissions for contact details page - save unsuccessful")
                return render(request, '500.html')

    training_organisation = FirstAidTraining.objects.get(application_id=application_id_local).training_organisation
    training_course = FirstAidTraining.objects.get(application_id=application_id_local).course_title
    certificate_day = FirstAidTraining.objects.get(application_id=application_id_local).course_day
    certificate_month = FirstAidTraining.objects.get(application_id=application_id_local).course_month
    certificate_year = FirstAidTraining.objects.get(application_id=application_id_local).course_year
    application = Application.objects.get(pk=application_id_local)

    form.error_summary_title = 'There was a problem'

    variables = {
        'form': form,
        'application_id': application_id_local,
        'training_organisation': training_organisation,
        'training_course': training_course,
        'certificate_day': certificate_day,
        'certificate_month': certificate_month,
        'certificate_year': certificate_year,
        'first_aid_training_status': application.first_aid_training_status
    }

    log.debug("Rendering first aid training page")
    return render(request, 'childminder_templates/first-aid-summary.html', variables)
