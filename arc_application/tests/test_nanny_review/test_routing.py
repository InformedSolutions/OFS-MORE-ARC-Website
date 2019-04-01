from datetime import datetime
from unittest import skipUnless, mock
from unittest.mock import patch

from django.test import tag, TestCase
from django.urls import reverse, resolve
from django.conf import settings

from arc_application.tests.utils import create_arc_user
from ...models import Arc
from ...services.db_gateways import NannyGatewayActions, IdentityGatewayActions
from ...views import NannyDbsCheckSummary, NannyContactDetailsSummary, NannyArcSummary, \
    NannyPersonalDetailsSummary, NannyChildcareAddressSummary, NannyFirstAidTrainingSummary, \
    NannyChildcareTrainingSummary, NannyInsuranceCoverSummary, NannyTaskList, NannyPreviousRegistrationView
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
@skipUnless(settings.ENABLE_NANNIES, 'Skipping test as Nanny feature toggle equated to False')
class NannyReviewFuncTestsBase(TestCase):

    def setUp(self):

        # make sure we're logged in as an arc user for each test
        self.arc_user = utils.create_arc_user()
        self.client.login(username='arc_test', password='my_secret')

        # stub out the nanny gateway and store mocks for each method
        self.nanny_gateway = utils.StubNannyGatewayActions()
        for meth in ('read', 'list', 'put', 'patch', 'create', 'delete'):
            mk = utils.patch_object_for_setUp(self, NannyGatewayActions, meth,
                                              side_effect=getattr(self.nanny_gateway, meth))
            setattr(self, 'ngw_{}_mock'.format(meth), mk)

        # create arc record for test application
        self.test_app_id = self.nanny_gateway.nanny_application['application_id']
        self.arc_record = utils.create_nanny_review(self.test_app_id, self.arc_user.pk)

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


class ReviewTaskListTests(NannyReviewFuncTestsBase):

    def test_complete_review_button_appears_if_all_tasks_reviewed(self):
        self.skipTest('testNotImplemented')

    def test_complete_review_button_appears_if_all_tasks_flagged(self):
        self.skipTest('testNotImplemented')

    def test_complete_review_button_does_not_appear_if_not_all_tasks_flagged_or_reviewed(self):
        self.skipTest('testNotImplemented')


class ReviewSignInDetailsTests(NannyReviewFuncTestsBase):

    def test_can_render_sign_in_details_page(self):
        """
        Test to ensure that the page for flagging sign in details can be rendered.
        """
        response = self.client.get(reverse('nanny_contact_summary') + '?id=' + self.test_app_id)

        self.assertEqual(response.status_code, 200)
        utils.assertView(response, NannyContactDetailsSummary.as_view())

    def test_sign_in_details_redirects_to_personal_details(self):
        """
        Test that a POST request to the sign in details page redirects to the personal details page.
        """
        response = self.client.post(reverse('nanny_contact_summary') + '?id=' + self.test_app_id,
                                    data={
                                        'id': self.test_app_id
                                    })

        self.assertEqual(response.status_code, 302)
        utils.assertRedirectView(response, NannyPersonalDetailsSummary.as_view())


class ReviewPersonalDetailsTests(NannyReviewFuncTestsBase):

    def test_can_render_personal_details_page(self):
        """
        Test to ensure that the page for flagging personal details can be rendered.
        """
        response = self.client.get(reverse('nanny_personal_details_summary') + '?id=' + self.test_app_id)

        self.assertEqual(response.status_code, 200)
        utils.assertView(response, NannyPersonalDetailsSummary.as_view())

    def test_flagging_personal_details_creates_arc_comments(self):
        """
        Test to ensure that personal details can be flagged.
        """
        self.skipTest('This test is failing due to endpoints, but the lived_abroad field '
                      'will be removed from here anyway. FIXME then.')
        fields_to_flag = [
            'name',
            'date_of_birth',
            'home_address',
            'known_to_social_services',
            'reasons_known_to_social_services'
        ]

        post_data = self._create_post_data(fields_to_flag)

        self.client.post(reverse('nanny_personal_details_summary') + '?id=' + self.test_app_id, data=post_data)

        for field in fields_to_flag:
            self._assert_create_call_made_with_given_params(self.ngw_create_mock, 'arc-comments', params={
                'application_id': self.test_app_id,
                'endpoint_name': ['applicant-personal-details', 'applicant-home-address'],
                'field_name': field,
                'comment': 'Flagged',
                'flagged': True,
            })

    def test_flagging_personal_details_sets_status_to_flagged(self, ):
        fields_to_flag = [
            'name',
            'date_of_birth',
            'home_address',
            'known_to_social_services',
            'reasons_known_to_social_services'
        ]

        post_data = self._create_post_data(fields_to_flag)

        self.client.post(reverse('nanny_personal_details_summary') + '?id=' + self.test_app_id, data=post_data)

        self.assertEqual(Arc.objects.get(pk=self.test_app_id).personal_details_review, 'FLAGGED')

    def test_flagging_home_address_only_sets_personal_details_status_to_flagged(self):
        fields_to_flag = [
            'home_address'
        ]

        post_data = self._create_post_data(fields_to_flag)

        self.client.post(reverse('nanny_personal_details_summary') + '?id=' + self.test_app_id, data=post_data)

        self.assertEqual(Arc.objects.get(pk=self.test_app_id).personal_details_review, 'FLAGGED')

    def test_flagging_name_only_sets_personal_details_status_to_flagged(self):
        fields_to_flag = [
            'name'
        ]

        post_data = self._create_post_data(fields_to_flag)

        self.client.post(reverse('nanny_personal_details_summary') + '?id=' + self.test_app_id, data=post_data)

        self.assertEqual(Arc.objects.get(pk=self.test_app_id).personal_details_review, 'FLAGGED')

    def test_not_flagging_personal_details_sets_status_to_reviewed(self):
        self.client.post(reverse('nanny_personal_details_summary') + '?id=' + self.test_app_id,
                         data={
                             'id': self.test_app_id,
                         })

        self.assertEqual(Arc.objects.get(pk=self.test_app_id).personal_details_review, 'COMPLETED')

    def test_submit_redirects_to_childcare_address_page_if_valid(self):
        fields_to_flag = [
            'name',
            'date_of_birth',
            'lived_abroad',
            'home_address',
            'known_to_social_services',
            'reasons_known_to_social_services'
        ]

        post_data = self._create_post_data(fields_to_flag)
        response = self.client.post(reverse('nanny_personal_details_summary') + '?id=' + self.test_app_id,
                                    data=post_data)

        self.assertEqual(response.status_code, 302)

    def test_shows_Add_Previous_Names_button(self):
        # GET request to personal details summary
        response = self.client.get(reverse('nanny_personal_details_summary') + '?id=' + self.test_app_id)

        # Assert that the 'Add previous names' button is on the page.
        utils.assertXPath(response, '//a[@href="{url}?id={app_id}"]'.format(
            url=reverse('nanny_previous_names'), app_id=self.test_app_id))

    def test_shows_previous_names_in_creation_order(self):
        self.nanny_gateway.previous_name_list_response = self.nanny_gateway.make_response(record=[
            self.nanny_gateway.previous_name_record,
            {
                'application_id': '998fd8ec-b96b-4a71-a1a1-a7a3ae186729',
                'previous_name_id': '9935bf3b-8ba9-4162-a25b-4c55e7d33d67',
                'first_name': 'Hi',
                'middle_names': 'Hello',
                'last_name': 'Hey',
                'start_day': 3,
                'start_month': 12,
                'start_year': 2004,
                'end_day': 7,
                'end_month': 12,
                'end_year': 2004,
                'order': 1
            }
        ])

        response = self.client.get(reverse('nanny_personal_details_summary') + '?id=' + self.test_app_id)
        self.assertEqual(200, response.status_code)

        heading = "Name and date of birth"
        utils.assertSummaryField(response, 'Previous name 1', 'Robin Hood', heading=heading)
        utils.assertSummaryField(response, 'Start date', '01/12/2003', heading=heading)
        utils.assertSummaryField(response, 'End date', '03/12/2004', heading=heading)
        utils.assertSummaryField(response, 'Previous name 2', 'Hi Hello Hey', heading=heading)
        utils.assertSummaryField(response, 'Start date', '03/12/2004', heading=heading)
        utils.assertSummaryField(response, 'End date', '07/12/2004', heading=heading)


class PreviousRegistrationTests(NannyReviewFuncTestsBase):

    def test_can_render_previous_registration_page(self):
        """
        Test to ensure that the page for entering previous registration details can be rendered.
        """
        response = self.client.get(reverse('nanny_previous_registration') + '?id=' + self.test_app_id)

        self.assertEqual(response.status_code, 200)
        utils.assertView(response, NannyPreviousRegistrationView.as_view())

    def test_redirect_after_submitting_valid_details(self):
        """
         Test to assert that clicking 'Continue' on the guidance page takes you to the
         'Type-Of-Childcare-Training' page.
        """
        data = {'id': self.test_app_id,
                'previous_registration': True,
                'individual_id': 1234567,
                'five_years_in_UK': True}

        response = self.client.post(reverse('nanny_previous_registration') + '?id=' + self.test_app_id, data)

        self.assertEqual(response.status_code, 302)
        utils.assertRedirectView(response, NannyPersonalDetailsSummary.as_view())

    def test_redirect_after_submitting_page_without_entering_details(self):
        """
         Test to assert that clicking 'Continue' on the guidance page takes you to the
         'Type-Of-Childcare-Training' page.
        """
        self.nanny_gateway.previous_registration_read_response.record = None

        data = {'id': self.test_app_id}

        response = self.client.post(reverse('nanny_previous_registration') + '?id=' + self.test_app_id, data)

        self.assertEqual(response.status_code, 200)
        utils.assertView(response, NannyPreviousRegistrationView.as_view())

    def test_previous_registration_appears_on_review_page(self):
        """
        Testing previous registration appears on the review page when there is a previous registration record
        """
        response = self.client.get(reverse('nanny_personal_details_summary') + '?id=' + self.test_app_id)

        self.assertContains(response, "Previous registration", status_code=200)
        self.assertContains(response, "Previously registered with Ofsted?", status_code=200)
        self.assertContains(response, "Individual ID", status_code=200)
        self.assertContains(response, "Lived in England for more than 5 years?", status_code=200)


class NannyPreviousNamesTests(NannyReviewFuncTestsBase):

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

    def test_can_render_page(self):
        """
        Test can render previous name form
        """
        application_id = self.test_app_id
        url = '{0}?id={1}'.format(
            reverse('nanny_previous_names'), application_id)

        response = self.client.get(url)

        self.assertEqual(200, response.status_code)
        utils.assertView(response, 'nanny_add_previous_name')

    def test_shows_fields_for_existing_stored_names(self):
        """
        Test previous names saved appear in form
        """
        with patch.object(NannyGatewayActions, 'list') as nanny_api_list:
            prev_name_record_2 = {
                'application_id': '998fd8ec-b96b-4a71-a1a1-a7a3ae186729',
                'previous_name_id': '9935bf3b-8ba9-4162-a25b-4c55e7d33d67',
                'first_name': 'Buffy',
                'middle_names': '',
                'last_name': 'Summers',
                'start_day': 3,
                'start_month': 12,
                'start_year': 2004,
                'end_day': 7,
                'end_month': 12,
                'end_year': 2004,
                'order': 1
            }
            nanny_api_list.return_value.record = [self.nanny_gateway.previous_name_record, prev_name_record_2]

            nanny_api_list.return_value.status_code = 200
            application_id = self.test_app_id

            url = '{0}?id={1}'.format(reverse('nanny_previous_names'), application_id)

            response = self.client.get(url)

            self.assertEqual(200, response.status_code)

            for field, ftype, value in [
                ('form-0-first_name', 'text', 'Robin'), ('form-1-first_name', 'text', 'Buffy'),
                ('form-0-middle_names', 'text', ''), ('form-1-middle_names', 'text', ''),
                ('form-0-last_name', 'text', 'Hood'), ('form-1-last_name', 'text', 'Summers'),
                ('form-0-start_date_0', 'number', '1'), ('form-1-start_date_0', 'number', '3'),
                ('form-0-start_date_1', 'number', '12'), ('form-1-start_date_1', 'number', '12'),
                ('form-0-start_date_2', 'number', '2003'), ('form-1-start_date_2', 'number', '2004'),
                ('form-0-end_date_0', 'number', '3'), ('form-1-end_date_0', 'number', '7'),
                ('form-0-end_date_1', 'number', '12'), ('form-1-end_date_1', 'number', '12'),
                ('form-0-end_date_2', 'number', '2004'), ('form-1-end_date_2', 'number', '2004')]:
                utils.assertXPathValue(
                    response,
                    'string(//input[normalize-space(@type)="{ftype}" and normalize-space(@name)="{field}"]/@value)'
                        .format(field=field, ftype=ftype),
                    value,
                    strip=True
                )

    def test_submit_confirm_returns_to_page_with_error_for_new_blank_form(self):

        url = '{0}?id={1}'.format(
            reverse('nanny_previous_names'), self.test_app_id)

        data = self._make_post_data(1, 'Confirm and continue', last_is_new=True)
        # add blank versions of form fields
        blanks = {k: '' for k, v in self.valid_previous_name_data[0].items()}
        data.update(blanks)

        response = self.client.post(url, data)

        self.assertEqual(200, response.status_code)
        utils.assertView(response, 'nanny_add_previous_name')
        utils.assertXPath(response, '//*[normalize-space(@class)="field-error" '
                                    'or normalize-space(@class)="error-message"]')

    def test_submit_confirm_returns_to_page_with_error_if_any_not_valid(self):

        with patch.object(NannyGatewayActions, 'list') as nanny_api_list:
            prev_name_record_2 = {'application_id': '998fd8ec-b96b-4a71-a1a1-a7a3ae186729',
                                  'previous_name_id': '9935bf3b-8ba9-4162-a25b-4c55e7d33d67',
                                  'first_name': 'Buffy',
                                  'middle_names': '',
                                  'last_name': 'Summers',
                                  'start_day': 3,
                                  'start_month': 12,
                                  'start_year': 2004,
                                  'end_day': 7,
                                  'end_month': 12,
                                  'end_year': 2004,
                                  'order': 1}
            nanny_api_list.return_value.record = [prev_name_record_2]

            nanny_api_list.return_value.status_code = 200
            application_id = self.test_app_id

            url = '{0}?id={1}'.format(reverse('nanny_previous_names'), application_id)

            data = self._make_post_data(2, 'Confirm and continue', last_is_new=True)
            data.update(self.valid_previous_name_data[0])
            data.update(self.valid_previous_name_data[1])

            # make first name an existing one
            data['form-0-previous_name_id'] = prev_name_record_2['previous_name_id']
            # make second one invalid
            data['form-1-start_date_0'] = 32

            response = self.client.post(url, data)

            self.assertEqual(200, response.status_code)
            utils.assertView(response, 'nanny_add_previous_name')
            utils.assertXPath(response, '//*[normalize-space(@class)="field-error" '
                                        'or normalize-space(@class)="error-message"]')

    def test_submit_confirm_redirects_to_personal_details_summary_if_all_valid(self):

        with patch.object(NannyGatewayActions, 'list') as nanny_api_list:
            prev_name_record_2 = {'application_id': '998fd8ec-b96b-4a71-a1a1-a7a3ae186729',
                                  'previous_name_id': '9935bf3b-8ba9-4162-a25b-4c55e7d33d67',
                                  'first_name': 'Buffy',
                                  'middle_names': '',
                                  'last_name': 'Summers',
                                  'start_day': 3,
                                  'start_month': 12,
                                  'start_year': 2004,
                                  'end_day': 7,
                                  'end_month': 12,
                                  'end_year': 2004,
                                  'order': 1}

            nanny_api_list.return_value.record = [prev_name_record_2]
            nanny_api_list.return_value.status_code = 200
            application_id = self.test_app_id

            url = '{0}?id={1}'.format(reverse('nanny_previous_names'), application_id)

            data = self._make_post_data(2, 'Confirm and continue', last_is_new=True)
            data.update(self.valid_previous_name_data[0])
            data.update(self.valid_previous_name_data[1])

            # make first name an existing one
            data['form-0-previous_name_id'] = prev_name_record_2['previous_name_id']

            response = self.client.post(url, data)

            # Assert response redirected to personal_details_summary
            self.assertEqual(302, response.status_code)
            utils.assertRedirectView(response, 'NannyPersonalDetailsSummary')

    def test_submit_confirm_calls_create_on_data_inputted(self):

        with patch.object(NannyGatewayActions, 'list') as nanny_api_list, \
                patch.object(NannyGatewayActions, 'create') as nanny_api_create:
            url = '{0}?id={1}'.format(reverse('nanny_previous_names'), self.test_app_id)

            data = self._make_post_data(2, 'Confirm and continue', last_is_new=True)
            data.update(self.valid_previous_name_data[0])
            data.update(self.valid_previous_name_data[1])

            response = self.client.post(url, data)

            valid_data_dict = {
                'application_id': self.test_app_id,
                'first_name': self.valid_previous_name_data[1]['form-1-first_name'],
                'middle_names': self.valid_previous_name_data[1]['form-1-middle_names'],
                'last_name': self.valid_previous_name_data[1]['form-1-last_name'],
                'start_day': self.valid_previous_name_data[1]['form-1-start_date_0'],
                'start_month': self.valid_previous_name_data[1]['form-1-start_date_1'],
                'start_year': self.valid_previous_name_data[1]['form-1-start_date_2'],
                'end_day': self.valid_previous_name_data[1]['form-1-end_date_0'],
                'end_month': self.valid_previous_name_data[1]['form-1-end_date_1'],
                'end_year': self.valid_previous_name_data[1]['form-1-end_date_2'],
                'order': 1
            }

            self.assertEqual(302, response.status_code)
            nanny_api_create.assert_called_with('previous-name', params=valid_data_dict)

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


class ReviewChildcareAddressTests(NannyReviewFuncTestsBase):

    def test_can_render_childcare_address_details_page(self):
        """
        Test to ensure that the page for flagging childcare address details can be rendered.
        """
        response = self.client.get(reverse('nanny_childcare_address_summary') + '?id=' + self.test_app_id)

        self.assertEqual(response.status_code, 200)
        utils.assertView(response, NannyChildcareAddressSummary.as_view())

    def test_can_render_childcare_address_page_if_no_addresses_provided(self):
        """
        Test to ensure that the page for flagging childcare details can be rendered, even if the applicant has specified
        that addresses will be provided at a later time.
        """
        self.nanny_gateway.nanny_application['application_id'] = '998fd8ec-b96b-4a71-a1a1-a7a3ae186729'
        self.nanny_gateway.nanny_application['address_to_be_provided'] = False

        self.nanny_gateway.childcare_address_read_response = self.nanny_gateway.make_response(404)

        response = self.client.get(reverse('nanny_childcare_address_summary') + '?id=' + self.test_app_id)

        self.assertEqual(response.status_code, 200)
        utils.assertView(response, NannyChildcareAddressSummary.as_view())

    def test_flagging_first_two_childcare_address_questions_creates_arc_comments(self):
        fields_to_flag = [
            'address_to_be_provided',
            'both_work_and_home_address'
        ]

        post_data = self._create_post_data(fields_to_flag)

        post_data.update(
            {
                'form-TOTAL_FORMS': '2',
                'form-INITIAL_FORMS': '2',
                'form-MAX_NUM_FORMS': '2',
            }
        )

        self.client.post(reverse('nanny_childcare_address_summary') + '?id=' + self.test_app_id, post_data)

        for field in fields_to_flag:
            self._assert_create_call_made_with_given_params(self.ngw_create_mock, 'arc-comments', params={
                'application_id': self.test_app_id,
                'endpoint_name': 'application',
                'field_name': field,
                'comment': 'Flagged',
                'flagged': True,
            })

    def test_flagging_childcare_address_details_creates_arc_comments(self):
        self.skipTest('testNotImplemented')

    def test_flagging_childcare_address_details_sets_status_to_flagged(self):
        fields_to_flag = [
            'address_to_be_provided',
            'both_work_and_home_address'
        ]

        post_data = self._create_post_data(fields_to_flag)

        post_data.update(
            {
                'form-TOTAL_FORMS': '2',
                'form-INITIAL_FORMS': '2',
                'form-MAX_NUM_FORMS': '2',
            }
        )

        self.client.post(reverse('nanny_childcare_address_summary') + '?id=' + self.test_app_id, post_data)

        self.assertEqual(Arc.objects.get(pk=self.test_app_id).childcare_address_review, 'FLAGGED')

    def test_not_flagging_childcare_address_details_sets_status_to_reviewed(self):
        self.client.post(reverse('nanny_childcare_address_summary') + '?id=' + self.test_app_id,
                         data={
                             'id': self.test_app_id,
                             'form-TOTAL_FORMS': '2',
                             'form-INITIAL_FORMS': '2',
                             'form-MAX_NUM_FORMS': '2',
                         })

        self.assertEqual(Arc.objects.get(pk=self.test_app_id).childcare_address_review, 'COMPLETED')

    def test_childcare_address_details_redirects_to_the_first_aid_page(self):
        """
        Test that a POST request to the childcare address details page redirects to the first aid details page.
        """
        response = self.client.post(reverse('nanny_childcare_address_summary') + '?id=' + self.test_app_id,
                                    data={
                                        'id': self.test_app_id,
                                        'form-TOTAL_FORMS': '2',
                                        'form-INITIAL_FORMS': '2',
                                        'form-MAX_NUM_FORMS': '2',
                                    })
        found = resolve(response.url)

        self.assertEqual(response.status_code, 302)
        utils.assertRedirectView(response, NannyFirstAidTrainingSummary.as_view())


class ReviewFirstAidDetailsTests(NannyReviewFuncTestsBase):

    def test_can_render_first_aid_details_page(self):
        """
        Test to ensure that the page for flagging first aid details can be rendered.
        """
        response = self.client.get(reverse('nanny_first_aid_training_summary') + '?id=' + self.test_app_id)

        self.assertEqual(response.status_code, 200)
        utils.assertView(response, NannyFirstAidTrainingSummary.as_view())

    def test_flagging_first_aid_details_sets_status_to_flagged(self):
        self.skipTest('testNotImplemented')

    def test_flagging_first_aid_details_creates_arc_comments(self):
        fields_to_flag = [
            'training_organisation',
            'course_title',
            'course_date',
        ]

        post_data = self._create_post_data(fields_to_flag)

        self.client.post(reverse('nanny_first_aid_training_summary') + '?id=' + self.test_app_id, post_data)

        for field in fields_to_flag:
            self._assert_create_call_made_with_given_params(self.ngw_create_mock, 'arc-comments', params={
                'application_id': self.test_app_id,
                'endpoint_name': 'first-aid',
                'field_name': field,
                'comment': 'Flagged',
                'flagged': True,
            })

    def test_not_flagging_first_aid_details_sets_status_to_reviewed(self):
        self.client.post(reverse('nanny_first_aid_training_summary') + '?id=' + self.test_app_id,
                         data={
                             'id': self.test_app_id,
                         })

        self.assertEqual(Arc.objects.get(pk=self.test_app_id).first_aid_review, 'COMPLETED')

    def test_first_aid_details_redirects_to_the_childcare_training_page(self):
        """
        Test that a POST request to the first aid details page redirects to the childcare training details page.
        """
        response = self.client.post(reverse('nanny_first_aid_training_summary') + '?id=' + self.test_app_id)
        found = resolve(response.url)

        self.assertEqual(response.status_code, 302)
        utils.assertRedirectView(response, NannyChildcareTrainingSummary.as_view())


class ReviewChildcareTrainingTests(NannyReviewFuncTestsBase):

    def test_can_render_childcare_training_details_page(self):
        """
        Test to ensure that the page for flagging childcare training details can be rendered.
        """
        response = self.client.get(reverse('nanny_childcare_training_summary') + '?id=' + self.test_app_id)

        self.assertEqual(response.status_code, 200)
        utils.assertView(response, NannyChildcareTrainingSummary.as_view())

    def test_flagging_childcare_training_details_sets_status_to_flagged(self):
        self.skipTest('testNotImplemented')

    def test_flagging_childcare_training_details_creates_arc_comments(self):
        fields_to_flag = [
            'childcare_training',
        ]

        post_data = self._create_post_data(fields_to_flag)

        self.client.post(reverse('nanny_childcare_training_summary') + '?id=' + self.test_app_id, post_data)

        for field in fields_to_flag:
            self._assert_create_call_made_with_given_params(self.ngw_create_mock, 'arc-comments', params={
                'application_id': self.test_app_id,
                'endpoint_name': 'childcare-training',
                'field_name': field,
                'comment': 'Flagged',
                'flagged': True,
            })

    def test_not_flagging_childcare_training_details_sets_status_to_reviewed(self):
        self.client.post(reverse('nanny_childcare_training_summary') + '?id=' + self.test_app_id,
                         data={
                             'id': self.test_app_id,
                         })

        self.assertEqual(Arc.objects.get(pk=self.test_app_id).childcare_training_review, 'COMPLETED')

    def test_childcare_training_redirects_to_the_criminal_record_page(self):
        """
        Test that a POST request to the childcare training details page redirects to the criminal record details page.
        """
        response = self.client.post(reverse('nanny_childcare_training_summary') + '?id=' + self.test_app_id)
        found = resolve(response.url)

        self.assertEqual(response.status_code, 302)
        utils.assertRedirectView(response, NannyDbsCheckSummary.as_view())


class ReviewCriminalRecordTests(NannyReviewFuncTestsBase):

    def test_can_render_criminal_record_details_page(self):
        """
        Test to ensure that the page for flagging dbs certificate details can be rendered.
        """
        response = self.client.get(reverse('nanny_dbs_summary') + '?id=' + self.test_app_id)

        self.assertEqual(response.status_code, 200)
        utils.assertView(response, NannyDbsCheckSummary.as_view())

    def test_flagging_criminal_record_checks_details_sets_status_to_flagged(self):
        self.skipTest('testNotImplemented')

    def test_flagging_criminal_record_checks_details_creates_arc_comments(self):
        fields_to_flag = [
            'dbs_number',
            'on_dbs_update_service',
        ]

        post_data = self._create_post_data(fields_to_flag)

        self.client.post(reverse('nanny_dbs_summary') + '?id=' + self.test_app_id, post_data)

        for field in fields_to_flag:
            self._assert_create_call_made_with_given_params(self.ngw_create_mock, 'arc-comments', params={
                'application_id': self.test_app_id,
                'endpoint_name': 'dbs-check',
                'field_name': field,
                'comment': 'Flagged',
                'flagged': True,
            })

    def test_not_flagging_criminal_record_checks_details_sets_status_to_reviewed(self):
        self.client.post(reverse('nanny_dbs_summary') + '?id=' + self.test_app_id,
                         data={
                             'id': self.test_app_id,
                         })

        self.assertEqual(Arc.objects.get(pk=self.test_app_id).dbs_review, 'COMPLETED')

    def test_criminal_record_redirects_to_the_insurance_cover_page(self):
        """
        Test that a POST request to the criminal record page redirects to the insurance cover details page.
        """
        response = self.client.post(reverse('nanny_dbs_summary') + '?id=' + self.test_app_id)
        found = resolve(response.url)

        self.assertEqual(response.status_code, 302)
        utils.assertRedirectView(response, NannyInsuranceCoverSummary.as_view())


class ReviewInsuranceCoverTests(NannyReviewFuncTestsBase):

    def test_can_render_insurance_cover_details_page(self):
        """
        Test to ensure that the page for flagging insurance cover details can be rendered.
        """
        response = self.client.get(reverse('nanny_insurance_cover_summary') + '?id=' + self.test_app_id)

        self.assertEqual(response.status_code, 200)
        utils.assertView(response, NannyInsuranceCoverSummary.as_view())

    def test_flagging_insurance_cover_details_sets_status_to_flagged(self):
        self.skipTest('testNotImplemented')

    def test_flagging_insurance_cover_details_creates_arc_comments(self):
        fields_to_flag = [
            'public_liability',
        ]

        post_data = self._create_post_data(fields_to_flag)

        self.client.post(reverse('nanny_insurance_cover_summary') + '?id=' + self.test_app_id, post_data)

        for field in fields_to_flag:
            self._assert_create_call_made_with_given_params(self.ngw_create_mock, 'arc-comments', params={
                'application_id': self.test_app_id,
                'endpoint_name': 'insurance-cover',
                'field_name': field,
                'comment': 'Flagged',
                'flagged': True,
            })

    def test_not_flagging_insurance_cover_details_sets_status_to_reviewed(self):
        self.client.post(reverse('nanny_insurance_cover_summary') + '?id=' + self.test_app_id,
                         data={
                             'id': self.test_app_id,
                         })

        self.assertEqual(Arc.objects.get(pk=self.test_app_id).insurance_cover_review, 'COMPLETED')

    def test_insurance_cover_details_redirects_to_the_task_list_page(self):
        """
        Test that a POST request to the insurance cover page redirects to the task list page.
        """
        response = self.client.post(reverse('nanny_insurance_cover_summary') + '?id=' + self.test_app_id)
        found = resolve(response.url)

        self.assertEqual(response.status_code, 302)
        utils.assertRedirectView(response, NannyTaskList.as_view())


class ReviewSummaryAndConfirmationFunctionalTests(NannyReviewFuncTestsBase):

    def test_can_render_arc_summary_page(self):

        response = self.client.get(reverse('nanny_arc_summary') + '?id=' + self.test_app_id)

        self.assertEqual(response.status_code, 200)
        utils.assertView(response, NannyArcSummary.as_view())

    def test_submit_summary_sends_accepted_email_if_no_tasks_flagged(self):
        self.skipTest('testNotImplemented')

    def test_submit_summary_sends_rejected_email_if_there_are_tasks_flagged(self):
        self.skipTest('testNotImplemented')

    class MockDatetime(datetime):
        @staticmethod
        def now():
            return datetime(2019, 2, 27, 17, 30, 5)

    @patch('arc_application.messaging.application_exporter.ApplicationExporter.export_childminder_application')
    @patch('arc_application.messaging.application_exporter.ApplicationExporter.export_nanny_application')
    @patch('arc_application.views.base.datetime', new=MockDatetime)
    def test_submit_summary_releases_application_as_accepted_in_database_if_no_tasks_flagged(self, *_):

        # set up gateway mocks to record changes to application fields
        app_field_updates = {}
        ok_response = self.nanny_gateway.make_response(200)

        def record_field_updates(endpoint, params):
            if endpoint == 'application' and params['application_id'] == self.test_app_id:
                app_field_updates.update(params)
            return ok_response

        self.ngw_delete_mock.side_effect = lambda e, p: self.fail()
        self.ngw_put_mock.side_effect = record_field_updates
        self.ngw_patch_mock.side_effect = record_field_updates

        APP_TASKS_ALL = ['childcare_address', 'childcare_training', 'dbs', 'first_aid', 'insurance_cover',
                         'login_details', 'personal_details']
        ARC_TASKS_ALL = ['childcare_address', 'childcare_training', 'dbs', 'first_aid', 'insurance_cover',
                         'login_details', 'personal_details']

        for task in APP_TASKS_ALL:
            self.nanny_gateway.nanny_application['{}_status'.format(task)] = APP_STATUS_COMPLETED
            self.nanny_gateway.nanny_application['{}_arc_flagged'.format(task)] = False

        self.nanny_gateway.nanny_application['declarations_status'] = APP_STATUS_COMPLETED
        self.nanny_gateway.nanny_application['application_status'] = APP_STATUS_REVIEW

        arc = Arc.objects.get(application_id=self.test_app_id)

        for task in ARC_TASKS_ALL:
            setattr(arc, '{}_review'.format(task), ARC_STATUS_COMPLETED)

        arc.save()

        # id must be both GET and POST parameter
        self.client.post(reverse('nanny_arc_summary') + '?id=' + self.test_app_id, data={'id': self.test_app_id})

        # in accepted status
        self.assertTrue('date_accepted' in app_field_updates)
        self.assertEqual(datetime(2019, 2, 27, 17, 30, 5), app_field_updates['date_accepted'])
        self.assertTrue('application_status' in app_field_updates)
        self.assertEqual(APP_STATUS_ACCEPTED, app_field_updates['application_status'])
        # declaration unchanged
        self.assertTrue('declarations_status' not in app_field_updates
                        or app_field_updates['declarations_status'] == APP_STATUS_COMPLETED)

        # unassigned from arc user
        refetched_arc = Arc.objects.get(pk=arc.pk)
        self.assertTrue(refetched_arc.user_id in ('', None))

    @patch('arc_application.messaging.application_exporter.ApplicationExporter.export_childminder_application')
    @patch('arc_application.messaging.application_exporter.ApplicationExporter.export_nanny_application')
    @patch('datetime.datetime', new=MockDatetime)
    def test_submit_summary_releases_application_as_needing_info_in_database_if_tasks_have_been_flagged(self, *_):

        # set up gateway mocks to record changes to application fields
        app_field_updates = {}
        ok_response = self.nanny_gateway.make_response(200)

        def record_field_updates(endpoint, params):
            if endpoint == 'application' and params['application_id'] == self.test_app_id:
                app_field_updates.update(params)
            return ok_response

        self.ngw_delete_mock.side_effect = lambda e, p: self.fail()
        self.ngw_put_mock.side_effect = record_field_updates
        self.ngw_patch_mock.side_effect = record_field_updates

        ARC_TASKS_FLAGGED = ['childcare_address', 'childcare_training', 'dbs', 'insurance_cover', 'login_details']
        ARC_TASKS_UNFLAGGED = ['personal_details', 'first_aid']
        APP_TASKS_TO_BE_FLAGGED = ['childcare_address', 'childcare_training', 'dbs', 'insurance_cover', 'login_details']
        APP_TASKS_NOT_TO_BE_FLAGGED = ['personal_details', 'first_aid']
        APP_TASKS_ALL = APP_TASKS_TO_BE_FLAGGED + APP_TASKS_NOT_TO_BE_FLAGGED

        for task in APP_TASKS_ALL:
            self.nanny_gateway.nanny_application['{}_status'.format(task)] = APP_STATUS_COMPLETED
            self.nanny_gateway.nanny_application['{}_arc_flagged'.format(task)] = False

        self.nanny_gateway.nanny_application['declarations_status'] = APP_STATUS_COMPLETED
        self.nanny_gateway.nanny_application['application_status'] = APP_STATUS_REVIEW

        arc = Arc.objects.get(application_id=self.test_app_id)

        for task in ARC_TASKS_UNFLAGGED:
            setattr(arc, '{}_review'.format(task), ARC_STATUS_COMPLETED)
        for task in ARC_TASKS_FLAGGED:
            setattr(arc, '{}_review'.format(task), ARC_STATUS_FLAGGED)

        arc.save()

        # id must be both GET and POST parameter
        self.client.post(reverse('nanny_arc_summary') + '?id=' + self.test_app_id, data={'id': self.test_app_id})

        # not in accepted status
        self.assertTrue('date_accepted' not in app_field_updates
                        or app_field_updates['date_accepted'] is None)
        self.assertTrue('application_status' in app_field_updates)
        self.assertEqual(APP_STATUS_FURTHER_INFO, app_field_updates['application_status'])
        # declaration has been reset
        self.assertTrue('declarations_status' in app_field_updates)
        self.assertEqual(APP_STATUS_NOT_STARTED, app_field_updates['declarations_status'])

        # unassigned from arc user
        refetched_arc = Arc.objects.get(pk=arc.pk)
        self.assertTrue(refetched_arc.user_id in ('', None))

        # flagged tasks still recorded in arc record
        for task in ARC_TASKS_FLAGGED:
            self.assertEqual(ARC_STATUS_FLAGGED, getattr(refetched_arc, '{}_review'.format(task)))
        for task in ARC_TASKS_UNFLAGGED:
            self.assertEqual(ARC_STATUS_COMPLETED, getattr(refetched_arc, '{}_review'.format(task)))

    @patch('arc_application.messaging.application_exporter.ApplicationExporter.export_childminder_application')
    @patch('arc_application.messaging.application_exporter.ApplicationExporter.export_nanny_application')
    @patch('datetime.datetime', new=MockDatetime)
    def test_submit_releases_application_once_if_submitted_twice(self, mock_datetime, mock_export_nanny_application):
        self.skipTest("testNotImplemented")
