from unittest import mock

from django.test import TestCase, tag

from arc_application.models import Arc
from django.core.urlresolvers import reverse

from arc_application.views.nanny_views.nanny_view_helpers import *

class NannyHelperTests(TestCase):
    """
    Test suite for testing nanny helper functions
    """

    def setUp(self):

    @tag('unit')
    def test_parse_date_of_birth_correct(self):
        for test_case in self.dob_test_list_correct:
            self.assertTrue(testing_parse_date_of_birth(test_case))


def testing_parse_date_of_birth(test_case):
    test_input, expected_output = test_case
    return parse_date_of_birth(test_input) == expected_output
