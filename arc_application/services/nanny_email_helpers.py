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

        if settings.DEBUG:
            print('send_returned_email was sent')

        personalisation = {'first_name': first_name, 'ref': ref}
        return send_email(email, personalisation, template_id, nanny_email=True)
    else:
        raise EnvironmentError('No settings attribute for APP_NOTIFY_URL found')


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
        template_id = 'ea2bb1f9-246c-4d42-9dbf-2411cd34aa5f'
        link = settings.NANNY_PUBLIC_URL + '/sign-in/new-application/?'

        if settings.DEBUG:
            print('send_returned_email was sent')
            print(link)

        personalisation = {'first_name': first_name, 'ref': ref, 'link': link}
        return send_email(email, personalisation, template_id, nanny_email=True)
    else:
        raise EnvironmentError('No settings attribute for APP_NOTIFY_URL found')
