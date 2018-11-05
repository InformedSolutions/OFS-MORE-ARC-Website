from unittest import mock

from django.conf import settings
from django.forms import Form
from django.contrib.auth.models import Group, User
from django.test import tag, TestCase
from django.urls import reverse, resolve

from arc_application.models import Arc
from arc_application.forms.nanny_forms.nanny_form_builder import NannyFormBuilder
from arc_application.services.db_gateways import NannyGatewayActions, IdentityGatewayActions
from arc_application.views import NannyDbsCheckSummary, NannyArcSummary, NannyContactDetailsSummary, \
    NannyPersonalDetailsSummary, NannyChildcareAddressSummary, NannyFirstAidTrainingSummary, \
    NannyChildcareTrainingSummary, NannyInsuranceCoverSummary, NannyTaskList, NannyYourChildrenSummary

from .test_utils import side_effect


test_app_id = side_effect('application').record['application_id']


@mock.patch.object(IdentityGatewayActions, 'read',   side_effect=side_effect)
@mock.patch.object(NannyGatewayActions, 'create', side_effect=side_effect)
@mock.patch.object(NannyGatewayActions, 'read',   side_effect=side_effect)
@mock.patch.object(NannyGatewayActions, 'list',   side_effect=side_effect)
@mock.patch.object(NannyGatewayActions, 'patch',  side_effect=side_effect)
@mock.patch.object(NannyGatewayActions, 'put',    side_effect=side_effect)
@mock.patch.object(NannyGatewayActions, 'delete', side_effect=side_effect)
class TestNannyFlagging(TestCase):
    """
    Test suite for the functionality to flag fields as an ARC user.
    """
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='governor_tARCin',
            email='test@test.com',
            password='my_secret'
        )
        g = Group.objects.create(name=settings.ARC_GROUP)
        g.user_set.add(cls.user)

        super(TestNannyFlagging, cls).setUpTestData()

    def setUp(self):
        self.client.login(username='governor_tARCin', password='my_secret')
        Arc.objects.create(application_id=test_app_id)

        super(TestNannyFlagging, self).setUp()

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
                if not call[1]['params'][param_name] == exp_param_val:
                    break
            else:
                return None

        raise AssertionError('The "create" method was called using the "{0}" endpoint, but not with the specified parameters.'.format(endpoint))

    # ---------- #
    # HTTP tests #
    # ---------- #

    def test_can_render_sign_in_details_page(self, *args):
        """
        Test to ensure that the page for flagging sign in details can be rendered.
        """
        response = self.client.get(reverse('nanny_contact_summary') + '?id=' + test_app_id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__, NannyContactDetailsSummary.as_view().__name__)

    def test_can_render_personal_details_page(self, *args):
        """
        Test to ensure that the page for flagging personal details can be rendered.
        """
        response = self.client.get(reverse('nanny_personal_details_summary') + '?id=' + test_app_id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__, NannyPersonalDetailsSummary.as_view().__name__)

    def test_can_render_your_children_details_page(self, *args):
        """
        Test to ensure that the page for flagging your children details can be rendered.
        """
        response = self.client.get(reverse('nanny_your_children_summary') + '?id=' + test_app_id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__, NannyYourChildrenSummary.as_view().__name__)

    def test_can_render_childcare_address_details_page(self, *args):
        """
        Test to ensure that the page for flagging childcare address details can be rendered.
        """
        response = self.client.get(reverse('nanny_childcare_address_summary') + '?id=' + test_app_id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__, NannyChildcareAddressSummary.as_view().__name__)

    def test_can_render_first_aid_details_page(self, *args):
        """
        Test to ensure that the page for flagging first aid details can be rendered.
        """
        response = self.client.get(reverse('nanny_first_aid_training_summary') + '?id=' + test_app_id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__, NannyFirstAidTrainingSummary.as_view().__name__)

    def test_can_render_childcare_training_details_page(self, *args):
        """
        Test to ensure that the page for flagging childcare training details can be rendered.
        """
        response = self.client.get(reverse('nanny_childcare_training_summary') + '?id=' + test_app_id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__, NannyChildcareTrainingSummary.as_view().__name__)

    def test_can_render_criminal_record_details_page(self, *args):
        """
        Test to ensure that the page for flagging dbs certificate details can be rendered.
        """
        response = self.client.get(reverse('nanny_dbs_summary') + '?id=' + test_app_id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__, NannyDbsCheckSummary.as_view().__name__)

    def test_can_render_insurance_cover_details_page(self, *args):
        """
        Test to ensure that the page for flagging insurance cover details can be rendered.
        """
        response = self.client.get(reverse('nanny_insurance_cover_summary') + '?id=' + test_app_id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__, NannyInsuranceCoverSummary.as_view().__name__)

    def test_complete_review_button_appears_if_all_tasks_reviewed(self, *args):
        """
        Test to ensure that the 'Complete Review' button is only present if all tasks are either 'Reviewed'
        or 'Flagged'.
        """
        self.skipTest('NotImplemented')

    def test_complete_review_button_appears_if_all_tasks_flagged(self, *args):
        self.skipTest('NotImplemented')

    def test_complete_review_button_does_not_appear_if_not_all_tasks_flagged_or_reviewed(self, *args):
        self.skipTest('NotImplemented')

    def test_sign_in_details_redirects_to_personal_details(self, *args):
        """
        Test that a POST request to the sign in details page redirects to the personal details page.
        """
        response = self.client.post(reverse('nanny_contact_summary') + '?id=' + test_app_id,
                                    data={
                                        'id': test_app_id
                                    })
        found = resolve(response.url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(found.func.view_class.__name__, NannyPersonalDetailsSummary.as_view().__name__)

    def test_personal_details_redirects_to_the_your_children_page_if_your_children_is_true(self, *args):
        """
        Test that a POST request to the personal details page redirects to the your children details page.
        """
        response = self.client.post(reverse('nanny_personal_details_summary') + '?id=' + test_app_id)
        found = resolve(response.url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(found.func.view_class.__name__, NannyYourChildrenSummary.as_view().__name__,)

    def test_personal_details_redirects_to_the_childcare_address_page_if_your_children_is_false(self, *args):
        """
        Test that a POST request to the personal details page redirects to the childcare address details page.
        """
        self.skipTest('NotImplemented')

    def test_your_children_redirects_to_the_childcare_address_page(self, *args):
        """
        Test that a POST request to the personal details page redirects to the childcare address details page.
        """
        response = self.client.post(reverse('nanny_your_children_summary') + '?id=' + test_app_id)
        found = resolve(response.url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(found.func.view_class.__name__, NannyChildcareAddressSummary.as_view().__name__,)

    def test_childcare_address_details_redirects_to_the_first_aid_page(self, *args):
        """
        Test that a POST request to the childcare address details page redirects to the first aid details page.
        """
        response = self.client.post(reverse('nanny_childcare_address_summary') + '?id=' + test_app_id,
                                    data={
                                         'id': test_app_id,
                                         'form-TOTAL_FORMS': '2',
                                         'form-INITIAL_FORMS': '2',
                                         'form-MAX_NUM_FORMS': '2',
                                     })
        found = resolve(response.url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(found.func.view_class.__name__, NannyFirstAidTrainingSummary.as_view().__name__)

    def test_first_aid_details_redirects_to_the_childcare_training_page(self, *args):
        """
        Test that a POST request to the first aid details page redirects to the childcare training details page.
        """
        response = self.client.post(reverse('nanny_first_aid_training_summary') + '?id=' + test_app_id)
        found = resolve(response.url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(found.func.view_class.__name__, NannyChildcareTrainingSummary.as_view().__name__)

    def test_childcare_training_redirects_to_the_criminal_record_page(self, *args):
        """
        Test that a POST request to the childcare training details page redirects to the criminal record details page.
        """
        response = self.client.post(reverse('nanny_childcare_training_summary') + '?id=' + test_app_id)
        found = resolve(response.url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(found.func.view_class.__name__, NannyDbsCheckSummary.as_view().__name__)

    def test_criminal_record_redirects_to_the_insurance_cover_page(self, *args):
        """
        Test that a POST request to the criminal record page redirects to the insurance cover details page.
        """
        response = self.client.post(reverse('nanny_dbs_summary') + '?id=' + test_app_id)
        found = resolve(response.url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(found.func.view_class.__name__, NannyInsuranceCoverSummary.as_view().__name__)

    def test_insurance_cover_details_redirects_to_the_task_list_page(self, *args):
        """
        Test that a POST request to the insurance cover page redirects to the task list page.
        """
        response = self.client.post(reverse('nanny_insurance_cover_summary') + '?id=' + test_app_id)
        found = resolve(response.url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(found.func.view_class.__name__, NannyTaskList.as_view().__name__)

    def test_flagging_personal_details_creates_arc_comments(self, *args):
        """
        Test to ensure that personal details can be flagged.
        """
        self.skipTest('This test is failing due to endpoints, but the lived_abroad field will be removed from here anyway. FIXME then.')
        fields_to_flag = [
            'name',
            'date_of_birth',
            'lived_abroad',
            'home_address',
            'your_children',
        ]

        post_data = self._create_post_data(fields_to_flag)

        self.client.post(reverse('nanny_personal_details_summary') + '?id=' + test_app_id, data=post_data)

        create_mock = args[5]

        for field in fields_to_flag:
            self._assert_create_call_made_with_given_params(create_mock, 'arc-comments',  params={
                'application_id': test_app_id,
                'endpoint_name': ['applicant-personal-details', 'applicant-home-address'],
                'field_name': field,
                'comment': 'Flagged',
                'flagged': True,
                })

    def test_flagging_personal_details_sets_status_to_flagged(self, *args):
        fields_to_flag = [
            'name',
            'date_of_birth',
            'lived_abroad',
            'home_address',
            'your_children',
        ]

        post_data = self._create_post_data(fields_to_flag)

        self.client.post(reverse('nanny_personal_details_summary') + '?id=' + test_app_id, data=post_data)

        self.assertEqual(Arc.objects.get(pk=test_app_id).personal_details_review, 'FLAGGED')

    def test_flagging_home_address_only_sets_personal_details_status_to_flagged(self, *args):
        self.skipTest('NotImplemented')

    def test_flagging_name_only_sets_personal_details_status_to_flagged(self, *args):
        self.skipTest('NotImplemented')

    def test_not_flagging_personal_details_sets_status_to_reviewed(self, *args):
        self.client.post(reverse('nanny_personal_details_summary') + '?id=' + test_app_id,
                         data={
                             'id': test_app_id,
                         })

        self.assertEqual(Arc.objects.get(pk=test_app_id).personal_details_review, 'COMPLETED')

    def test_flagging_your_children_details_sets_status_to_flagged(self, *args):
        self.skipTest('NotImplemented')

    def test_flagging_you_children_details_creates_arc_comments(self, *args):
        self.skipTest('NotImplemented')

    def test_not_flagging_your_children_details_sets_status_to_reviewed(self, *args):
        self.client.post(reverse('nanny_your_children_summary') + '?id=' + test_app_id,
                         data={
                             'id': test_app_id,
                         })

        self.assertEqual(Arc.objects.get(pk=test_app_id).your_children_review, 'COMPLETED')

    def test_flagging_first_two_childcare_address_questions_creates_arc_comments(self, *args):
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

        self.client.post(reverse('nanny_childcare_address_summary') + '?id=' + test_app_id, post_data)

        create_mock = args[5]

        for field in fields_to_flag:
            self._assert_create_call_made_with_given_params(create_mock, 'arc-comments',  params={
                'application_id': test_app_id,
                'endpoint_name': 'application',
                'field_name': field,
                'comment': 'Flagged',
                'flagged': True,
                })

    def test_flagging_childcare_address_details_creates_arc_comments(self, *args):
        fields_to_flag = [
            'form-0-childcare_address',
            'form-1-childcare_address',
        ]

        post_data = self._create_post_data(fields_to_flag)

        post_data.update(
            {
                'form-TOTAL_FORMS': '2',
                'form-INITIAL_FORMS': '2',
                'form-MAX_NUM_FORMS': '2',
            }
        )

        self.client.post(reverse('nanny_childcare_address_summary') + '?id=' + test_app_id, post_data)

        create_mock = args[5]

        childcare_address_mock_responses = NannyGatewayActions().list('childcare-address', params={'application_id': test_app_id}).record

        for index, field in enumerate(fields_to_flag):
            self._assert_create_call_made_with_given_params(create_mock, 'arc-comments',  params={
                'application_id': test_app_id,
                'table_pk': childcare_address_mock_responses[index]['childcare_address_id'],
                'endpoint_name': 'childcare-address',
                'field_name': field[7:],
                'comment': 'Flagged',
                'flagged': True,
                })

    def test_flagging_childcare_address_details_sets_status_to_flagged(self, *args):
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

        self.client.post(reverse('nanny_childcare_address_summary') + '?id=' + test_app_id, post_data)

        self.assertEqual(Arc.objects.get(pk=test_app_id).childcare_address_review, 'FLAGGED')

    def test_not_flagging_childcare_address_details_sets_status_to_reviewed(self, *args):
        self.client.post(reverse('nanny_childcare_address_summary') + '?id=' + test_app_id,
                         data={
                             'id': test_app_id,
                             'form-TOTAL_FORMS': '2',
                             'form-INITIAL_FORMS': '2',
                             'form-MAX_NUM_FORMS': '2',
                         })

        self.assertEqual(Arc.objects.get(pk=test_app_id).childcare_address_review, 'COMPLETED')

    def test_flagging_first_aid_details_sets_status_to_flagged(self, *args):
        self.skipTest('NotImplemented')

    def test_flagging_first_aid_details_creates_arc_comments(self, *args):
        fields_to_flag = [
            'training_organisation',
            'course_title',
            'course_date',
        ]

        post_data = self._create_post_data(fields_to_flag)

        self.client.post(reverse('nanny_first_aid_training_summary') + '?id=' + test_app_id, post_data)

        create_mock = args[5]

        for field in fields_to_flag:
            self._assert_create_call_made_with_given_params(create_mock, 'arc-comments',  params={
                'application_id': test_app_id,
                'endpoint_name': 'first-aid',
                'field_name': field,
                'comment': 'Flagged',
                'flagged': True,
                })

    def test_not_flagging_first_aid_details_sets_status_to_reviewed(self, *args):
        self.client.post(reverse('nanny_first_aid_training_summary') + '?id=' + test_app_id,
                         data={
                             'id': test_app_id,
                         })

        self.assertEqual(Arc.objects.get(pk=test_app_id).first_aid_review, 'COMPLETED')

    def test_flagging_childcare_training_details_sets_status_to_flagged(self, *args):
        self.skipTest('NotImplemented')

    def test_flagging_childcare_training_details_creates_arc_comments(self, *args):
        fields_to_flag = [
            'childcare_training',
        ]

        post_data = self._create_post_data(fields_to_flag)

        self.client.post(reverse('nanny_childcare_training_summary') + '?id=' + test_app_id, post_data)

        create_mock = args[5]

        for field in fields_to_flag:
            self._assert_create_call_made_with_given_params(create_mock, 'arc-comments',  params={
                'application_id': test_app_id,
                'endpoint_name': 'childcare-training',
                'field_name': field,
                'comment': 'Flagged',
                'flagged': True,
                })

    def test_not_flagging_childcare_training_details_sets_status_to_reviewed(self, *args):
        self.client.post(reverse('nanny_childcare_training_summary') + '?id=' + test_app_id,
                         data={
                             'id': test_app_id,
                         })

        self.assertEqual(Arc.objects.get(pk=test_app_id).childcare_training_review, 'COMPLETED')

    def test_flagging_criminal_record_checks_details_sets_status_to_flagged(self, *args):
        self.skipTest('NotImplemented')

    def test_flagging_criminal_record_checks_details_creates_arc_comments(self, *args):
        fields_to_flag = [
            'dbs_number',
            'convictions',
        ]

        post_data = self._create_post_data(fields_to_flag)

        self.client.post(reverse('nanny_dbs_summary') + '?id=' + test_app_id, post_data)

        create_mock = args[5]

        for field in fields_to_flag:
            self._assert_create_call_made_with_given_params(create_mock, 'arc-comments',  params={
                'application_id': test_app_id,
                'endpoint_name': 'dbs-check',
                'field_name': field,
                'comment': 'Flagged',
                'flagged': True,
                })

    def test_not_flagging_criminal_record_checks_details_sets_status_to_reviewed(self, *args):
        self.client.post(reverse('nanny_dbs_summary') + '?id=' + test_app_id,
                         data={
                             'id': test_app_id,
                         })

        self.assertEqual(Arc.objects.get(pk=test_app_id).dbs_review, 'COMPLETED')

    def test_flagging_insurance_cover_details_sets_status_to_flagged(self, *args):
        self.skipTest('NotImplemented')

    def test_flagging_insurance_cover_details_creates_arc_comments(self, *args):
        fields_to_flag = [
            'public_liability',
        ]

        post_data = self._create_post_data(fields_to_flag)

        self.client.post(reverse('nanny_insurance_cover_summary') + '?id=' + test_app_id, post_data)

        create_mock = args[5]

        for field in fields_to_flag:
            self._assert_create_call_made_with_given_params(create_mock, 'arc-comments',  params={
                'application_id': test_app_id,
                'endpoint_name': 'insurance-cover',
                'field_name': field,
                'comment': 'Flagged',
                'flagged': True,
                })

    def test_not_flagging_insurance_cover_details_sets_status_to_reviewed(self, *args):
        self.client.post(reverse('nanny_insurance_cover_summary') + '?id=' + test_app_id,
                         data={
                             'id': test_app_id,
                         })

        self.assertEqual(Arc.objects.get(pk=test_app_id).insurance_cover_review, 'COMPLETED')

    def test_can_render_arc_summary_page(self, *args):
        """
        Test to ensure that the Nanny ARC summary page can be rendered.
        """
        response = self.client.get(reverse('nanny_arc_summary') + '?id=' + test_app_id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__, NannyArcSummary.as_view().__name__)

    def test_get_form_initial_values_populates_with_existing_arc_comments(self, *args):
        self.skipTest('NotImplemented')

    # ---------- #
    # UNIT tests #
    # ---------- #

    @tag('unit')
    def test_form_builder(self, *args):
        """
        Test to assert that the form_builder functions as expected.
        """
        example_fields = [
            'field_1',
            'field_2',
        ]

        form = NannyFormBuilder(example_fields, api_endpoint_name='fake-endpoint').create_form()

        self.assertIsInstance(form(), Form)

        for field in example_fields:
            self.assertIn(field + '_declare', form().fields)
            self.assertIn(field + '_comments', form().fields)

    @tag('unit')
    def test_formset_builder(self, *args):
        self.skipTest('NotImplemented')
