from unittest import mock

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.test import tag, TestCase
from django.urls import reverse

from arc_application.models import Arc
from arc_application.views.arc_user_summary import ARCUserSummaryView, NannyApplicationHandler


mock_nanny_application = {
    'application_status': 'SUBMITTED',
    'application_id': '998fd8ec-b96b-4a71-a1a1-a7a3ae186729',
    'date_submitted': '2018-07-31',
    'date_updated': '2018-07-31',
}

mock_personal_details_record = {
    'first_name': 'The Dark Lord',
    'last_name': 'Selenium',
}

mock_endpoint_return_values = {
    'application': mock_nanny_application,
    'applicant-personal-details': mock_personal_details_record
}


def side_effect(endpoint_name, *args, **kwargs):
    return mock_endpoint_return_values[endpoint_name]


class ARCMock(mock.MagicMock):
    pass


class ArcUserSummaryPageTests(TestCase):
    """
    Test suite for the functionality within the ARC summary page.
    """
    def setUp(self):
        self.user = User.objects.create_user(
            username='governor_tARCin',
            email='test@test.com',
            password='my_secret'
        )
        g = Group.objects.create(name=settings.ARC_GROUP)
        g.user_set.add(self.user)

        global arc_test_user
        arc_test_user = self.user

        self.client.login(username='governor_tARCin', password='my_secret')

    # ----------------------- #
    # Integration level tests #
    # ----------------------- #

    @tag('integration')
    def test_list_nanny_tasks_to_review(self):
        """
        Test that the _list_tasks_for_review() method returns a complete list of tasks for review.

        If we were to mock the Gateway response, this test will continue to pass even if the models are updated.
        Must therefore be an integration test.
        """
        tasks_list = NannyApplicationHandler(arc_user=self.user)._list_tasks_for_review()

        expected_list = [
            'login_details',
            'personal_details',
            'childcare_address',
            'first_aid_training',
            'childcare_training',
            'criminal_record_check',
            'insurance_cover'
        ]

        self.assertEqual(tasks_list, expected_list)

    # ---------------- #
    # HTTP level tests #
    # ---------------- #

    @tag('http')
    def test_can_render_arc_user_summary_page(self):
        """
        Test that the ARC user summary page can be rendered.
        """
        response = self.client.get(reverse('summary'))

        self.assertEqual(200, response.status_code)
        self.assertEqual(response.resolver_match.func.__name__, ARCUserSummaryView.as_view().__name__)

    @tag('http')
    def test_page_renders_with_table_if_user_has_assigned_apps(self):
        # response = self.client.get(reverse('summary'))
        #
        # # TODO: Add an assigned app to user.
        #
        # self.assertContains(response, '<table class="table table-hover" id="request-table">', html=True)

        pass

    @tag('http')
    def test_page_renders_without_table_if_user_has_no_assigned_apps(self):
        # response = self.client.get(reverse('summary'))
        #
        # self.assertNotContains(response, '<table class="table table-hover" id="request-table">', html=True)

        pass

    @tag('http')
    def test_page_renders_with_error_if_no_nanny_apps_available(self):

        # TODO: Ensure no nanny apps available.

        # response = self.client.post(
        #     reverse('summary'),
        #     data={
        #         'add_nanny_application': 'add_nanny_application'
        #     }
        # )
        #
        # self.assertEqual(200, response.status_code)
        # self.assertEqual(response.resolver_match.func.__name__, ARCUserSummaryView.as_view().__name__)
        # self.assertContains(response, '<li class="non-field-error">There are currently no more applications ready for a review</li>', html=True)

        pass

    @tag('http')
    def test_page_renders_with_error_if_no_childminder_apps_available(self):

        # TODO: Ensure no childminder apps available.

        # response = self.client.post(
        #     reverse('summary'),
        #     data={'add_childminder_application': 'add_childminder_application'}
        # )
        #
        # self.assertEqual(200, response.status_code)
        # self.assertEqual(response.resolver_match.func.__name__, ARCUserSummaryView.as_view().__name__)
        # self.assertContains(response, '<li class="non-field-error">There are currently no more applications ready for a review</li>', html=True)

        pass

    @tag('http')
    def test_assigns_childminder_app_if_one_available(self):
        pass

    @tag('http')
    def test_assigns_nanny_app_if_one_available(self):
        """with mock.patch('arc_application.db_gateways.NannyGatewayActions.list') as mock_nanny_list, \
                mock.patch('arc_application.db_gateways.NannyGatewayActions.read') as mock_nanny_read:

            mock_nanny_list.return_value.record = [mock_nanny_application]
            mock_nanny_list.return_value.status_code = 200
            # mock_nanny_read.return_value.record = mock_nanny_application
            # mock_identity_read.return_value.record = mock_personal_details_record
            mock_nanny_read.side_effect = side_effect

            # mock_nanny_read.mock_add_spec(mock_nanny_read.spec.append('record'))

            mock_nanny_read.return_value.record = mock.PropertyMock(side_effect=side_effect)

            self.client.post(reverse('summary'), data={'add_nanny_application': 'add_nanny_application'})

            arc_filter_query = Arc.objects.filter(user_id=self.user.id)

            self.assertTrue(arc_filter_query.exists())
            self.assertEqual(arc_filter_query[0].application_id, mock_nanny_application['application_id'])"""

        pass

    @tag('http')
    def test_cannot_assign_more_than_five_applications(self):
        pass

    # ---------- #
    # UNIT tests #
    # ---------- #

    @tag('unit')
    def test_count_assigned_apps(self):
        pass

    @tag('unit')
    def test_get_oldest_nanny_app_id(self):
        pass

    @tag('unit')
    def test_get_oldest_childminder_app_id(self):
        pass

    @tag('unit')
    def test_sort_applications_by_date_submitted(self):
        pass

    @tag('unit')
    def test_assign_nanny_app_to_user(self):
        pass

    @tag('unit')
    def test_assign_childminder_app_to_user(self):
        pass

    @tag('unit')
    def test_list_childminder_tasks_to_review(self):
        pass

    @tag('unit')
    def test_release_nanny_app_to_pool(self):
        pass

    @tag('unit')
    def test_release_childminder_app_to_pool(self):
        pass

    @tag('unit')
    def test_get_all_table_data(self):
        pass

    @tag('unit')
    def test_get_nanny_row_data(self):
        pass

    @tag('unit')
    def test_get_childminder_row_data(self):
        pass
