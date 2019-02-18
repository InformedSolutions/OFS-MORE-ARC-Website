from unittest import mock

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.http import HttpResponse
from django.test import tag, TestCase
from django.urls import reverse

from arc_application.models import Arc
from arc_application.views.arc_user_summary import ARCUserSummaryView


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

        self.skipTest('NotImplemented')

    def test_page_renders_without_table_if_user_has_no_assigned_apps(self):
        with mock.patch('arc_application.models.Arc.objects.filter') as arc_objects_filter:

            arc_objects_filter.return_value = Arc.objects.none()

            response = self.client.get(reverse('summary'))

            self.assertNotContains(response, '<table class="table table-hover" id="request-table">', html=True)

    def test_page_renders_with_error_if_no_nanny_apps_available(self):
        self.skipTest('Nannies temporarily removed from ARC.')
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
        self.skipTest('NotImplemented')

    def test_assigns_nanny_app_if_one_available(self):
        self.skipTest('Nannies temporarily removed from ARC.')
        with mock.patch('arc_application.services.db_gateways.NannyGatewayActions.list') as mock_nanny_list, \
                mock.patch('arc_application.services.db_gateways.NannyGatewayActions.read') as mock_nanny_read:

            mock_nanny_list.return_value.status_code = 200
            mock_nanny_list.return_value.record = [mock_nanny_application]
            mock_nanny_read.side_effect = side_effect

            self.client.post(reverse('summary'), data={'add_nanny_application': 'add_nanny_application'})

            arc_filter_query = Arc.objects.filter(user_id=self.user.id)

            self.assertTrue(arc_filter_query.exists())
            self.assertEqual(str(arc_filter_query[0].application_id), mock_nanny_application['application_id'])

    def test_cannot_assign_more_than_five_applications(self):
        self.skipTest('NotImplemented')

        # with mock.patch('django.db.models.query.QuerySet.count') as mock_count:
        #     mock_count.return_value = 5
        #
        #     response = self.client.post(reverse('summary'), data={'add_nanny_application': 'add_nanny_application'})
        #     self.assertContains(response, 'You have already reached the maximum (' + str(settings.APPLICATION_LIMIT) + ') applications', html=True)
        #
        #     response = self.client.post(
        #         reverse('summary'), data={'add_childminder_application': 'add_childminder_application'}
        #     )
        #     self.assertContains(response, 'You have already reached the maximum (' + str(settings.APPLICATION_LIMIT) + ') applications', html=True)


