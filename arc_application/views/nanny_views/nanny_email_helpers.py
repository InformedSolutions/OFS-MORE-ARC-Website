from django.conf import settings
from arc_application.notify import send_email


def send_accepted_email(email, first_name, ref):
    """
    Method to send a nanny application accepted email using the Notify Gateway API
    :param email: string containing the e-mail address to send the e-mail to
    :param first_name: string first name
    :param ref: string ref
    :return: HTTP response
    """
    if hasattr(settings, 'NOTIFY_URL'):
        email = str(email)
        template_id = '4b9d4146-cbec-436a-81ea-efb444ef5180'

        personalisation = {'first_name': first_name, 'ref': ref}
        return send_email(email, personalisation, template_id)


def send_returned_email(email, first_name, ref):
    """
    Method to send a nanny application returned email using the Notify Gateway API
    :param email: string containing the e-mail address to send the e-mail to
    :param first_name: string first name
    :param ref: string ref
    :return: HTTP response
    """
    if hasattr(settings, 'NOTIFY_URL'):
        email = str(email)
        template_id = '4b9d4146-cbec-436a-81ea-efb444ef5180'
        link = settings.NANNY_EMAIL_VALIDATION_URL + '/sign-in/new-application/?'

        personalisation = {'first_name': first_name, 'ref': ref, 'link': link}
        return send_email(email, personalisation, template_id)
