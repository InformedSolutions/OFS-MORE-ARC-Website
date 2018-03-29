"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- magic_link.py --

@author: Informed Solutions
"""

import random
import string


def generate_magic_link():
    """
    Method returning a random magic link and expiry (but it still needs to be saved to DB)
    :param request: a request object used to generate the HttpResponse
    :return: a dictionary with the link and expiry date
    """
    digits = 12
    link = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(digits)])
    link = link.upper()
    return link
