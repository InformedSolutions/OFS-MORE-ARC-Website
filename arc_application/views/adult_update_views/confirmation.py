import datetime
import time

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from application.services.notify import send_email
from ...magic_link import generate_magic_link
from ...services.db_gateways import HMGatewayActions, IdentityGatewayActions
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
    identity_gateway_response = HMGatewayActions().read('user', params={'application_id': application_id_local})

    if identity_gateway_response.status_code == 200:
        identity_record = identity_gateway_response.record
        email = identity_record['email']
    first_name = 'An applicant'

    status = Arc.objects.get(pk=application_id_local)
    if status.adult_update_review == 'COMPLETED' and not application_record['arc_flagged']:

        # If the application has not already been accepted.
        if application_record['application_status'] != 'ACCEPTED':

            application_record['application_status'] = "ACCEPTED"
            application_record['date_accepted'] = datetime.datetime.now()
            HMGatewayActions().put('application', params=application_record)

            #personalisation = {'first_name': first_name}
            accepted_email(email, first_name, app_ref, application_id_local)

        # If successful
        release_application(request, application_id_local, 'ACCEPTED')

        variables = {
            'application_id': application_id_local,
        }

        return render(request, 'review-confirmation.html', variables)

    else:
        if application_record["application_status"] != 'FURTHER_INFORMATION':

            identity_record = identity_gateway_response.record
            magic_link = generate_magic_link()
            expiry = int(time.time())
            identity_record['email_expiry_date'] = expiry
            identity_record['magic_link_email'] = magic_link
            IdentityGatewayActions().put('user', params=identity_record)
            link = settings.CHILDMINDER_EMAIL_VALIDATION_URL + '/' + magic_link
            returned_email(email, first_name, app_ref, link)

            # TODO
            application_record['application_status'] = "FURTHER_INFORMATION"
            HMGatewayActions().put('application', params=application_record)


            release_application(request, application_id_local, 'FURTHER_INFORMATION')

        variables = {
            'application_id': application_id_local,
        }

        return render(request, 'review-sent-back.html', variables)

# Add personalisation and create template
def accepted_email(email, first_name, ref, application_id):
    """
    Method to send an email using the Notify Gateway API
    :param email: string containing the e-mail address to send the e-mail to
    :param first_name: string first name
    :param ref: string ref
    :param application_id: application ID
    :return: HTTP response
    """
    if hasattr(settings, 'NOTIFY_URL'):
        email = str(email)

        template_id = '6af4d98f-a67e-4291-af15-74862d231493'

        personalisation = {'first_name': first_name}
        return send_email(email, personalisation, template_id)

# Add personalisation and create template
def returned_email(email, first_name, ref, link):
    """
    Method to send an email using the Notify Gateway API
    :param email: string containing the e-mail address to send the e-mail to
    :param first_name: string first name
    :param ref: string ref
    :return: HTTP response
    """
    if hasattr(settings, 'NOTIFY_URL'):
        email = str(email)
        template_id = '7e605128-909e-4203-a40a-15d397a0f7f0'
        personalisation = {'first_name': first_name, 'link': link}
        return send_email(email, personalisation, template_id)