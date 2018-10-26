import random
import string
import time

from django.conf import settings

from arc_application.notify import send_email
from arc_application.services.db_gateways import IdentityGatewayActions


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

        full_link, magic_link, sent_time = __generate_magic_link()
        __update_nanny_magic_link(email, magic_link, sent_time)

        if settings.DEBUG:
            print('send_returned_email was sent')
            print(full_link)

        personalisation = {'first_name': first_name, 'ref': ref, 'link': full_link}
        return send_email(email, personalisation, template_id, nanny_email=True)
    else:
        raise EnvironmentError('No settings attribute for APP_NOTIFY_URL found')


def __update_nanny_magic_link(email, magic_link, expiry_date):
    identity_actions = IdentityGatewayActions()

    # Create an update record with the magic_link information
    magic_link_patch_record = {
        'email': email,
        'magic_link_email': magic_link,
        'email_expiry_date': expiry_date
    }

    identity_actions.patch('user', params=magic_link_patch_record)


def __generate_magic_link():
    """
    Generates a magic_link to be used for verification
    :return: A tuple containing the full link to the nanny application,
        the magic link generated and
        the current time.
    """
    link = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(12)]).upper()
    full_link = str(settings.NANNY_PUBLIC_URL) + '/validate/' + link

    return full_link, link, int(time.time())
