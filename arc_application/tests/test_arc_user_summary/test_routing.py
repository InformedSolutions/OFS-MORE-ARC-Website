from unittest import mock, skipUnless

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.http import HttpResponse
from django.test import tag, TestCase
from django.urls import reverse

from ...models import Arc
from ...views.arc_user_summary import ARCUserSummaryView
from ...services.db_gateways import NannyGatewayActions
from ...services.application_handler import NannyApplicationHandler


mock_nanny_application = {
    'application_status': 'SUBMITTED',
    'application_id': '998fd8ec-b96b-4a71-a1a1-a7a3ae186729',
    'date_submitted': '2018-07-31 17:20:46.011717+00',
    'date_updated': '2018-07-31 17:20:46.011717+00',
}

mock_personal_details_record = {
    'first_name': 'The Dark Lord',
    'last_name': 'Selenium',
}


nanny_application_response = HttpResponse()
nanny_application_response.status_code = 200
nanny_application_response.record = mock_nanny_application

personal_details_response = HttpResponse()
personal_details_response.status_code = 200
personal_details_response.record = mock_personal_details_record


mock_endpoint_return_values = {
    'application': nanny_application_response,
    'applicant-personal-details': personal_details_response,
}


def side_effect(endpoint_name, *args, **kwargs):
    return mock_endpoint_return_values[endpoint_name]


@tag('http')
class ArcUserSummaryPageFunctionalTests(TestCase):
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
    @skipUnless(settings.ENABLE_NANNIES, 'Skipping test as Nanny feature toggle equated to False')
    def test_list_nanny_tasks_to_review(self):
        """
        Test that the _list_tasks_for_review() method returns a complete list of tasks for review.

        If we were to mock the Gateway response, this test will continue to pass even if the models are updated.
        Must therefore be an integration test.
        """
        test_uuid = '395a2e0c-0d19-4998-95b9-ce6c3539c2be'
        NannyGatewayActions().create('application', params={'application_id': test_uuid})
        tasks_list = NannyApplicationHandler(arc_user=self.user)._list_tasks_for_review()

        expected_list = [
            'login_details',
            'personal_details',
            'childcare_address',
            'first_aid_training',
            'childcare_training',
            'criminal_record_check',
            'dbs',
            'first_aid',
            'insurance_cover',
        ]

        for task in tasks_list:
            self.assertIn(task, expected_list)

        NannyGatewayActions().delete('application', params={'application_id': test_uuid})

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

    def test_page_renders_with_table_if_user_has_assigned_apps(self):
        # response = self.client.get(reverse('summary'))
        #
        # # TODO: Add an assigned app to user.
        #
        # self.assertContains(response, '<table class="table table-hover" id="request-table">', html=True)

        self.skipTest('testNotImplemented')

    def test_page_renders_without_table_if_user_has_no_assigned_apps(self):
        with mock.patch('arc_application.models.Arc.objects.filter') as arc_objects_filter:

            arc_objects_filter.return_value = Arc.objects.none()

            response = self.client.get(reverse('summary'))

            self.assertNotContains(response, '<table class="table table-hover" id="request-table">', html=True)

    @skipUnless(settings.ENABLE_NANNIES, 'Skipping test as Nanny feature toggle equated to False')
    def test_page_renders_with_error_if_no_nanny_apps_available(self):
        with mock.patch('arc_application.services.db_gateways.NannyGatewayActions.list') as mock_nanny_list:

            mock_nanny_list.return_value.status_code = 404

            response = self.client.post(reverse('summary'), data={'add_nanny_application': 'add_nanny_application'})

            self.assertEqual(200, response.status_code)
            self.assertEqual(response.resolver_match.func.__name__, ARCUserSummaryView.as_view().__name__)
            self.assertContains(response, '<li class="non-field-error">There are currently no more applications ready for a review</li>', html=True)

    def test_page_renders_with_error_if_no_childminder_apps_available(self):
        with mock.patch('arc_application.models.Arc.objects.filter') as arc_objects_filter:

            arc_objects_filter.return_value = Arc.objects.none()

            response = self.client.post(
                reverse('summary'), data={'add_childminder_application': 'add_childminder_application'}
            )

            self.assertEqual(200, response.status_code)
            self.assertEqual(response.resolver_match.func.__name__, ARCUserSummaryView.as_view().__name__)
            self.assertContains(response, '<li class="non-field-error">There are currently no more applications ready for a review</li>', html=True)

    def test_assigns_childminder_app_if_one_available(self):
        self.skipTest('testNotImplemented')

    @skipUnless(settings.ENABLE_NANNIES, 'Skipping test as Nanny feature toggle equated to False')
    def test_assigns_nanny_app_if_one_available(self):
        with mock.patch('arc_application.services.db_gateways.NannyGatewayActions.list') as mock_nanny_list, \
                mock.patch('arc_application.services.db_gateways.NannyGatewayActions.read') as mock_nanny_read:

            mock_nanny_list.return_value.status_code = 200
            mock_nanny_list.return_value.record = [mock_nanny_application]
            mock_nanny_read.side_effect = side_effect

            self.client.post(reverse('summary'), data={'add_nanny_application': 'add_nanny_application'})

            arc_filter_query = Arc.objects.filter(user_id=self.user.id)

            self.assertTrue(arc_filter_query.exists())
            self.assertEqual(str(arc_filter_query[0].application_id), mock_nanny_application['application_id'])

    @skipUnless(settings.ENABLE_NANNIES, 'Skipping test as Nanny feature toggle equated to False')
    def test_assigns_resubmitted_nanny_app_first(self):
        """
        Test to check resubmitted nanny app is assigned first
        """
        with mock.patch('arc_application.services.db_gateways.NannyGatewayActions.list') as mock_nanny_list, \
                mock.patch('arc_application.services.db_gateways.NannyGatewayActions.read') as mock_nanny_read:

            mock_nanny_app_2 = {
                'application_status': 'SUBMITTED',
                'application_id': '998fd8ec-b96b-4a71-a1a1-a7a3ae186728',
                'date_submitted': '2018-07-31 17:20:46.011717+00',
                'date_updated': '2018-10-31 17:20:46.011717+00',
            }

            mock_nanny_list.return_value.status_code = 200
            mock_nanny_list.return_value.record = [mock_nanny_application, mock_nanny_app_2]
            mock_nanny_read.side_effect = side_effect

            self.client.post(reverse('summary'), data={'add_nanny_application': 'add_nanny_application'})

            arc_filter_query = Arc.objects.filter(user_id=self.user.id)

            self.assertTrue(arc_filter_query.exists())
            self.assertEqual(str(arc_filter_query[0].application_id), mock_nanny_app_2['application_id'])

    @skipUnless(settings.ENABLE_NANNIES, 'Skipping test as Nanny feature toggle equated to False')
    def test_assigns_oldest_submitted_nanny_app_first(self):
        """
        Test to check oldest submitted nanny app is assigned first if no resubmitted apps
        """
        with mock.patch('arc_application.services.db_gateways.NannyGatewayActions.list') as mock_nanny_list, \
                mock.patch('arc_application.services.db_gateways.NannyGatewayActions.read') as mock_nanny_read:
            mock_nanny_app_2 = {
                'application_status': 'SUBMITTED',
                'application_id': '998fd8ec-b96b-4a71-a1a1-a7a3ae186728',
                'date_submitted': '2018-06-31 17:20:46.011717+00',
                'date_updated': '2018-06-31 17:20:46.011717+00',
            }

            mock_nanny_list.return_value.status_code = 200
            mock_nanny_list.return_value.record = [mock_nanny_application, mock_nanny_app_2]
            mock_nanny_read.side_effect = side_effect

            self.client.post(reverse('summary'), data={'add_nanny_application': 'add_nanny_application'})

            arc_filter_query = Arc.objects.filter(user_id=self.user.id)

            self.assertTrue(arc_filter_query.exists())
            self.assertEqual(str(arc_filter_query[0].application_id), mock_nanny_app_2['application_id'])

    @skipUnless(settings.ENABLE_NANNIES, 'Skipping test as Nanny feature toggle equated to False')
    def test_assigns_oldest_resubmitted_nanny_app_first(self):
        """
        Test to check oldest submitted nanny app is assigned first if no resubmitted apps
        """
        with mock.patch('arc_application.services.db_gateways.NannyGatewayActions.list') as mock_nanny_list, \
                mock.patch('arc_application.services.db_gateways.NannyGatewayActions.read') as mock_nanny_read:
            mock_nanny_app = {
                'application_status': 'SUBMITTED',
                'application_id': '998fd8ec-b96b-4a71-a1a1-a7a3ae186728',
                'date_submitted': '2018-06-31 17:20:46.011717+00',
                'date_updated': '2018-07-31 17:20:46.011717+00',
            }
            mock_nanny_app_2 = {
                'application_status': 'SUBMITTED',
                'application_id': '998fd8ec-b96b-4a71-a1a1-a7a3ae186729',
                'date_submitted': '2018-06-31 17:20:46.011717+00',
                'date_updated': '2018-08-31 17:20:46.011717+00',
            }

            mock_nanny_list.return_value.status_code = 200
            mock_nanny_list.return_value.record = [mock_nanny_application, mock_nanny_app, mock_nanny_app_2]
            mock_nanny_read.side_effect = side_effect

            self.client.post(reverse('summary'), data={'add_nanny_application': 'add_nanny_application'})

            arc_filter_query = Arc.objects.filter(user_id=self.user.id)

            self.assertTrue(arc_filter_query.exists())
            self.assertEqual(str(arc_filter_query[0].application_id), mock_nanny_app['application_id'])
