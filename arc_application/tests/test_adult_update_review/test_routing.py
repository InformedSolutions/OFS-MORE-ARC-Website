from datetime import datetime
from unittest import skipUnless, mock
from unittest.mock import patch

from django.test import tag, TestCase
from django.urls import reverse, resolve
from django.conf import settings

from arc_application.tests.utils import create_arc_user
from ...models import Arc
from ...services.db_gateways import HMGatewayActions, IdentityGatewayActions
from ...views import new_adults_summary, adult_previous_registration_view, \
    adult_update_view, arc_summary
from ...tests import utils

ARC_STATUS_FLAGGED = 'FLAGGED'
ARC_STATUS_COMPLETED = 'COMPLETED'

APP_STATUS_FLAGGED = 'FLAGGED'
APP_STATUS_NOT_STARTED = 'NOT_STARTED'
APP_STATUS_COMPLETED = 'COMPLETED'
APP_STATUS_FURTHER_INFO = 'FURTHER_INFORMATION'
APP_STATUS_REVIEW = 'ARC_REVIEW'
APP_STATUS_ACCEPTED = 'ACCEPTED'


@tag('http')
@skipUnless(settings.ENABLE_HM, 'Skipping test as HM feature toggle equated to False')
class HMReviewFuncTestsBase(TestCase):

    def setUp(self):

        # make sure we're logged in as an arc user for each test
        self.arc_user = utils.create_arc_user()
        self.client.login(username='arc_test', password='my_secret')

        # stub out the nanny gateway and store mocks for each method
        self.hm_gateway = utils.StubHMGatewayActions()
        for meth in ('read', 'list', 'put', 'patch', 'create', 'delete'):
            mk = utils.patch_object_for_setUp(self, HMGatewayActions, meth,
                                              side_effect=getattr(self.hm_gateway, meth))
            setattr(self, 'ngw_{}_mock'.format(meth), mk)

        # create arc record for test application
        self.test_app_id = self.hm_gateway.hm_application['adult_id']
        self.arc_record = utils.create_adult_review(self.test_app_id, self.arc_user.pk)

        # stub out the identity gateway and store mock for read method
        self.identity_gateway = utils.StubIdentityGatewayActions()
        for meth in ('read',):
            mk = utils.patch_object_for_setUp(self, IdentityGatewayActions, meth,
                                              side_effect=getattr(self.identity_gateway, meth))
            setattr(self, 'igw_{}_mock'.format(meth), mk)

    # -------------- #
    # Helper methods #
    # -------------- #

    @staticmethod
    def _create_post_data(fields_to_flag):
        post_data = dict((field + '_declare', 'on') for field in fields_to_flag)

        for field in fields_to_flag:
            post_data[field + '_comments'] = 'Flagged'

        post_data['cygnum_relationship'] = 'test'
        return post_data

    @staticmethod
    def _assert_create_call_made_with_given_params(create_mock, endpoint, params):
        """
        Use to assert that a 'create' method was called with a given endpoint and parameters at least once.
        Custom method easier than accessing table pk for a given form and using bulit-in mock.assert_any_call()
        """
        # Get all calls made to the given endpoint.
        endpoint_calls = [call for call in create_mock.call_args_list if call[0][0] == endpoint]

        if len(endpoint_calls) == 0:
            raise AssertionError('The "create" method was not called with the endpoint "{0}".'.format(endpoint))

        # Iterate through list of calls to endpoint.
        # Iterate through the expected parameter values.
        # If any value in call != expected value, break, then move to next call.
        # If all values match that call, return None; a match for the expected parameters values was found. Test passes.
        # If any no calls match, raise AssertionError. Test fails.

        for call in endpoint_calls:
            for param_name, exp_param_val in params.items():
                if not call[1]['params'][param_name] == exp_param_val or (
                        type(exp_param_val) == str and not call[1]['params'][param_name] in exp_param_val):
                    break
            else:
                return None

        raise AssertionError(
            'The "create" method was called using the "{0}" endpoint, but not with the specified parameters.'.format(
                endpoint))

class AdultUpdateReviewTests(HMReviewFuncTestsBase):

    def test_can_render_adult_review_page(self):
        """
        Test to ensure that the page for reviewing an adult update can be rendered
        """
        response = self.client.get(reverse('new_adults_summary') + '?id=' + self.test_app_id)

        self.assertEqual(response.status_code, 200)
        utils.assertView(response, adult_update_view.new_adults_summary)

@skipUnless(settings.ENABLE_HM, 'Skipping test as HM feature toggle equated to False')
class PreviousRegistrationTests(HMReviewFuncTestsBase):

    def test_can_render_previous_registration_page(self):
        """
        Test to ensure that the page for entering previous registration details can be rendered.
        """
        response = self.client.get(reverse('adults-previous-registration') + '?id=' + self.test_app_id)

        self.assertEqual(response.status_code, 200)
        utils.assertView(response, adult_previous_registration_view)

    def test_redirect_after_submitting_valid_details(self):
        """
         Test to assert that clicking 'Continue' on the guidance page takes you to the
         'Type-Of-Childcare-Training' page.
        """
        data = {'id': self.test_app_id,
                'previous_registration': True,
                'individual_id': 1234567,
                'five_years_in_UK': True}

        response = self.client.post(reverse('adults-previous-registration') + '?id=' + self.test_app_id, data)
        redirect_url = "/arc/review/new-adult?id={0}".format(self.test_app_id)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, redirect_url)

    def test_redirect_after_submitting_page_without_entering_details(self):
        """
         Test to assert that clicking 'Continue' on the guidance page takes you to the
         'Type-Of-Childcare-Training' page.
        """
        self.hm_gateway.previous_registration_read_response.record = None

        data = {'id': self.test_app_id}

        response = self.client.post(reverse('adults-previous-registration') + '?id=' + self.test_app_id, data)

        self.assertEqual(response.status_code, 200)
        utils.assertView(response, adult_previous_registration_view)

@skipUnless(settings.ENABLE_HM, 'Skipping test as HM feature toggle equated to False')
class HMPreviousNamesTests(HMReviewFuncTestsBase):

    def setUp(self):
        super().setUp()
        self.valid_previous_name_data = [
            {
                'form-0-previous_name_id': '',
                'form-0-first_name': 'David',
                'form-0-middle_names': 'Anty',
                'form-0-last_name': 'Goliath',
                'form-0-start_date_0': 1,
                'form-0-start_date_1': 3,
                'form-0-start_date_2': 1996,
                'form-0-end_date_0': 15,
                'form-0-end_date_1': 8,
                'form-0-end_date_2': 1996,
            },
            {
                'form-1-previous_name_id': '',
                'form-1-first_name': 'James',
                'form-1-middle_names': 'Rather-Large',
                'form-1-last_name': 'Peach',
                'form-1-start_date_0': 12,
                'form-1-start_date_1': 8,
                'form-1-start_date_2': 1996,
                'form-1-end_date_0': 4,
                'form-1-end_date_1': 12,
                'form-1-end_date_2': 2002,
            }
        ]
    def _make_post_data(self, num_names, action=None, last_is_new=False):
        data = {
            'id': self.test_app_id,
            'form-TOTAL_FORMS': num_names,
            'form-INITIAL_FORMS': num_names - 1 if last_is_new else num_names,
            'form-MIN_NUM_FORMS': 0,
            'form-MAX_NUM_FORMS': 1000,
        }
        if action is not None:
            data['action'] = action
        return data

@skipUnless(settings.ENABLE_HM, 'Skipping test as HM feature toggle equated to False')
class ReviewSummaryAndConfirmationFunctionalTests(HMReviewFuncTestsBase):

    def test_can_render_arc_summary_page(self):

        response = self.client.get(reverse('new_adults') + '?id=' + self.test_app_id)

        self.assertEqual(response.status_code, 200)
        utils.assertView(response, arc_summary)



