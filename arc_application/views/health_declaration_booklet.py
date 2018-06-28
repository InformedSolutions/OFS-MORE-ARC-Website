from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render

from ..forms.form import HealthForm
from ..models import Application, Arc, HealthDeclarationBooklet
from ..review_util import redirect_selection, request_to_comment, save_comments
from .base import group_required


@group_required(settings.ARC_GROUP)
def health_check_answers(request):
    """
    Method returning the template for the Your health: answers page (for a given application)
    displaying entered data for this task and navigating to the task list when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your health: answers template
    """
    table_name = 'HDB'

    if request.method == 'GET':
        application_id_local = request.GET["id"]
        hdb_id = HealthDeclarationBooklet.objects.get(application_id=application_id_local).hdb_id
        form = HealthForm(table_keys=[hdb_id])

    elif request.method == 'POST':
        application_id_local = request.POST["id"]
        hdb_id = HealthDeclarationBooklet.objects.get(application_id=application_id_local).hdb_id
        form = HealthForm(request.POST, table_keys=[hdb_id])

        if form.is_valid():
            comment_list = request_to_comment(hdb_id, table_name, form.cleaned_data)
            save_successful = save_comments(request, comment_list)

            if not comment_list:
                section_status = 'COMPLETED'
            else:
                section_status = 'FLAGGED'

            if save_successful:
                status = Arc.objects.get(pk=application_id_local)
                status.health_review = section_status
                status.save()
                default = '/dbs-check/summary'
                redirect_link = redirect_selection(request, default)

                return HttpResponseRedirect(settings.URL_PREFIX + redirect_link + '?id=' + application_id_local)

            else:
                return render(request, '500.html')

    send_hdb_declare = HealthDeclarationBooklet.objects.get(application_id=application_id_local).send_hdb_declare
    application = Application.objects.get(pk=application_id_local)
    variables = {
        'form': form,
        'application_id': application_id_local,
        'send_hdb_declare': send_hdb_declare,
        'health_status': application.health_status,
    }

    return render(request, 'health-check-answers.html', variables)
