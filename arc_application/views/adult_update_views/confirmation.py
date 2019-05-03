import datetime

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from ...services.db_gateways import HMGatewayActions
from django.http import HttpResponseRedirect
from ...models.arc import Arc
from ...views.base import release_application
from django.urls import reverse
from django.shortcuts import render
from ...decorators import group_required, user_assigned_application


def review(request, application_id_local):
    """
    Confirmation Page
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your App Review Confirmation template
    """

    adult_record = HMGatewayActions().read('adult', params={'adult_id': application_id_local}).record
    #TODO email to applicant

    # account = UserDetails.objects.get(application_id=application)
    # login_id = account.pk
    # first_name = ''
    #
    # # Get Application's related email and first_name to send an email.
    # if UserDetails.objects.filter(login_id=login_id).exists():
    #     user_details = UserDetails.objects.get(login_id=login_id)
    #     email = user_details.email
    #
    #     if ApplicantPersonalDetails.objects.filter(application_id=application_id_local).exists():
    #         personal_details = ApplicantPersonalDetails.objects.get(application_id=application_id_local)
    #         applicant_name = ApplicantName.objects.get(personal_detail_id=personal_details.personal_detail_id)
    #         first_name = applicant_name.first_name

    status = Arc.objects.get(pk=application_id_local)
    if status.adult_update_review == 'COMPLETED' and not adult_record['arc_flagged']:

        # If the application has not already been accepted.
        if adult_record['adult_status'] != 'ACCEPTED':

            adult_record['adult_status'] = "ACCEPTED"
            adult_record['date_accepted'] = datetime.datetime.now()
            HMGatewayActions().put('application', params=adult_record)

            # personalisation = {'first_name': first_name, 'ref': app_ref}
            # accepted_email(email, first_name, app_ref, application_id_local)
            # send_survey_email(email, personalisation, application)



        return HttpResponseRedirect(
            reverse('adults-confirmation') + '?id=' + application_id_local
        )

    else:
        if adult_record["adult_status"] != 'FURTHER_INFORMATION':

            # TODO: email to applicant
            # magic_link = generate_magic_link()
            # expiry = int(time.time())
            # # user_details.email_expiry_date = expiry
            # # user_details.magic_link_email = magic_link
            # # user_details.save()
            # # link = settings.CHILDMINDER_EMAIL_VALIDATION_URL + '/' + magic_link
            # # returned_email(email, first_name, app_ref, link)

            # TODO
            adult_record['adult_status'] = "FURTHER_INFORMATION"
            HMGatewayActions().put('application', params=adult_record)

        return HttpResponseRedirect(
            reverse('adults-returned') + '?id=' + application_id_local
        )

@login_required
@user_assigned_application
@group_required(settings.ARC_GROUP)
def returned_adult(request):
    application_id_local = request.GET["id"]
    release_application(request, application_id_local, 'FURTHER_INFORMATION')
    variables = {
        'application_id': application_id_local
    }
    return render(request, 'review-returned.html', variables)


@login_required
@user_assigned_application
@group_required(settings.ARC_GROUP)
def accepted_adult(request):
    application_id_local = request.GET["id"]
    release_application(request, application_id_local, 'ACCEPTED')
    variables = {
        'application_id': application_id_local
    }
    return render(request, 'review-confirmation.html', variables)