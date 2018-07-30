from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render

from ..forms.form import LogInDetailsForm
from ..models import Application, Arc, UserDetails
from ..review_util import redirect_selection, request_to_comment, save_comments
from ..decorators import group_required, user_assigned_application


@login_required
@group_required(settings.ARC_GROUP)
@user_assigned_application
def contact_summary(request):
    """
    Method returning the template for the Your login and contact details: summary page (for a given application)
    displaying entered data for this task and navigating to the Type of childcare page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your login and contact details: summary template
    """
    table_name = 'USER_DETAILS'

    if request.method == 'GET':
        application_id_local = request.GET["id"]
        application = Application.objects.get(pk=application_id_local)
        account = UserDetails.objects.get(application_id=application)
        login_id = account.login_id
        # Table keys are supplied in a list format for use in init
        form = LogInDetailsForm(table_keys=[login_id])
        application_id_local = request.GET["id"]

    elif request.method == 'POST':
        # Populate the form with the received data
        application_id_local = request.POST["id"]
        application = Application.objects.get(pk=application_id_local)
        account = UserDetails.objects.get(application_id=application)
        login_id = account.login_id
        form = LogInDetailsForm(request.POST, table_keys=[login_id])

        if form.is_valid():
            # Convert the data from the form into a series of comments with the
            # table id to be stored in the ARC COMMENTS Table
            comment_list = request_to_comment(login_id, table_name, form.cleaned_data)
            save_successful = save_comments(request, comment_list)

            # If no comments have been made, the status has not been flagged
            # Therefore it has been completed
            if not comment_list:
                section_status = 'COMPLETED'
                application.login_details_arc_flagged = False
            else:
                section_status = 'FLAGGED'
                application.login_details_arc_flagged = True

            application.save()

            # If the save has been successful , save and redirect
            if save_successful:
                status = Arc.objects.get(pk=application_id_local)
                status.login_details_review = section_status
                status.save()
                default = '/childcare/age-groups'
                redirect_link = redirect_selection(request, default)

                return HttpResponseRedirect(settings.URL_PREFIX + redirect_link + '?id=' + application_id_local)
            else:
                return ChildProcessError

    application = Application.objects.get(pk=application_id_local)
    user_details = UserDetails.objects.get(application_id=application)
    email = user_details.email
    mobile_number = user_details.mobile_number
    add_phone_number = user_details.add_phone_number
    form.error_summary_title = 'There was a problem'
    variables = {
        'form': form,
        'application_id': application_id_local,
        'email': email,
        'mobile_number': mobile_number,
        'add_phone_number': add_phone_number,
        'login_details_status': application.login_details_status,
        'childcare_type_status': application.childcare_type_status
    }
    return render(request, 'contact-summary.html', variables)
