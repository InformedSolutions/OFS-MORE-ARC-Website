import datetime

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from ...services.db_gateways import HMGatewayActions
from ...models.arc import Arc
from ...views.base import release_application
from django.shortcuts import render
from ...decorators import group_required, user_assigned_application


@login_required
@group_required(settings.ARC_GROUP)
@user_assigned_application
def review(request):
    """
    Confirmation Page
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your App Review Confirmation template
    """
    application_id_local = request.GET["id"]
    application = HMGatewayActions().read('application', params={'token_id': application_id_local})
    application_record = application.record
    app_ref = HMGatewayActions().read('dpa-auth', params={'token_id': application_id_local}).record["URN"]

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
    if status.adult_update_review == 'COMPLETED' and not application_record['arc_flagged']:

        # If the application has not already been accepted.
        if application_record['application_status'] != 'ACCEPTED':

            application_record['application_status'] = "ACCEPTED"
            application_record['date_accepted'] = datetime.datetime.now()
            HMGatewayActions().put('application', params=application_record)

            # personalisation = {'first_name': first_name, 'ref': app_ref}
            # accepted_email(email, first_name, app_ref, application_id_local)
            # send_survey_email(email, personalisation, application)

        # If successful
        release_application(request, application_id_local, 'ACCEPTED')

        variables = {
            'application_id': application_id_local,
        }

        return render(request, 'review-confirmation.html', variables)

    else:
        if application_record["application_status"] != 'FURTHER_INFORMATION':

            # TODO: email to applicant
            # magic_link = generate_magic_link()
            # expiry = int(time.time())
            # # user_details.email_expiry_date = expiry
            # # user_details.magic_link_email = magic_link
            # # user_details.save()
            # # link = settings.CHILDMINDER_EMAIL_VALIDATION_URL + '/' + magic_link
            # # returned_email(email, first_name, app_ref, link)

            # TODO
            # if Arc.objects.filter(pk=application_id_local):
            #     arc = Arc.objects.get(pk=application_id_local)
            #     app = Application.objects.get(pk=application_id_local)
            #     app.save()

            release_application(request, application_id_local, 'FURTHER_INFORMATION')

        variables = {
            'application_id': application_id_local,
        }

        return render(request, 'review-sent-back.html', variables)