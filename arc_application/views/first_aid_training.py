from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render

from ..forms.form import FirstAidTrainingForm
from ..models import Application, Arc, FirstAidTraining
from ..review_util import redirect_selection, request_to_comment, save_comments


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
            save_successful = save_comments(comment_list)

            if not comment_list:
                section_status = 'COMPLETED'
            else:
                section_status = 'FLAGGED'

            if save_successful:
                status = Arc.objects.get(pk=application_id_local)
                status.first_aid_review = section_status
                status.save()
                default = '/dbs-check/summary'
                redirect_link = redirect_selection(request, default)

                return HttpResponseRedirect(settings.URL_PREFIX + redirect_link + '?id=' + application_id_local)
            else:
                return render(request, '500.html')

    training_organisation = FirstAidTraining.objects.get(application_id=application_id_local).training_organisation
    training_course = FirstAidTraining.objects.get(application_id=application_id_local).course_title
    certificate_day = FirstAidTraining.objects.get(application_id=application_id_local).course_day
    certificate_month = FirstAidTraining.objects.get(application_id=application_id_local).course_month
    certificate_year = FirstAidTraining.objects.get(application_id=application_id_local).course_year
    application = Application.objects.get(pk=application_id_local)
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

    return render(request, 'first-aid-summary.html', variables)
