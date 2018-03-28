"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- magic_link.py --

@author: Informed Solutions
"""

import random
import string
import time


def generate_magic_link(request):
    """
    Method returning a random magic link and expiry (but it still needs to be saved to DB)
    :param request: a request object used to generate the HttpResponse
    :return: a dictionary with the link and expiry date
    """
    link = generate_random(12, 'link')
    expiry = int(time.time())

    return {'link':link,'expiry':expiry}



def generate_random(digits, type):
    """
    Method to generate a random code or random string of varying size for the SMS code or Magic Link URL
    :param digits: integer indicating the desired length
    :param type: flag to indicate the SMS code or Magic Link URL
    :return:
    """
    if type == 'code':
        r = ''.join([random.choice(string.digits) for n in range(digits)])
    elif type == 'link':
        r = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(digits)])
    r = r.upper()
    return r


