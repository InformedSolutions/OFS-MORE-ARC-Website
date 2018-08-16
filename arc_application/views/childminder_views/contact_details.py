from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render

<<<<<<< HEAD:arc_application/views/childminder_views/contact_details.py
from arc_application.forms.childminder_forms.form import LogInDetailsForm
from arc_application.models import Application, Arc, UserDetails
from arc_application.review_util import redirect_selection, request_to_comment, save_comments
from arc_application.decorators import group_required, user_assigned_application
=======
from ..models import Application, Arc, UserDetails
from ..review_util import redirect_selection
from ..decorators import group_required, user_assigned_application
>>>>>>> release/v1.2.0:arc_application/views/contact_details.py


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

    if request.method == 'GET':
        application_id_local = request.GET["id"]
        application = Application.objects.get(pk=application_id_local)
        user_details = UserDetails.objects.get(application_id=application)
        email = user_details.email
        mobile_number = user_details.mobile_number
        add_phone_number = user_details.add_phone_number
        variables = {
            'application_id': application_id_local,
            'email': email,
            'mobile_number': mobile_number,
            'add_phone_number': add_phone_number,
            'login_details_status': application.login_details_status,
            'childcare_type_status': application.childcare_type_status
        }
        return render(request, 'contact-summary.html', variables)

    elif request.method == 'POST':
        # As there is no actual flagging to be done for this section, the status is just set to completed on POST
        application_id_local = request.POST["id"]
        application = Application.objects.get(pk=application_id_local)
<<<<<<< HEAD:arc_application/views/childminder_views/contact_details.py
        account = UserDetails.objects.get(application_id=application)
        login_id = account.login_id
        form = LogInDetailsForm(request.POST, table_keys=[login_id])

        if form.is_valid():

            status = Arc.objects.get(pk=application_id_local)
            status.login_details_review = 'COMPLETED'
            status.save()
            default = '/childcare/age-groups'
            redirect_link = redirect_selection(request, default)

            return HttpResponseRedirect(settings.URL_PREFIX + redirect_link + '?id=' + application_id_local)

    application = Application.objects.get(pk=application_id_local)
    user_details = UserDetails.objects.get(application_id=application)
    email = user_details.email
    mobile_number = user_details.mobile_number
    add_phone_number = user_details.add_phone_number
    variables = {
        'form': form,
        'application_id': application_id_local,
        'email': email,
        'mobile_number': mobile_number,
        'add_phone_number': add_phone_number,
        'login_details_status': application.login_details_status,
        'childcare_type_status': application.childcare_type_status
    }
    return render(request, 'childminder_templates/contact-summary.html', variables)
=======
        application.login_details_arc_flagged = False
        application.save()

        status = Arc.objects.get(pk=application_id_local)
        section_status = 'COMPLETED'
        status.login_details_review = section_status
        status.save()

        default = '/childcare/age-groups'
        redirect_link = redirect_selection(request, default)
        return HttpResponseRedirect(settings.URL_PREFIX + redirect_link + '?id=' + application_id_local)

>>>>>>> release/v1.2.0:arc_application/views/contact_details.py
