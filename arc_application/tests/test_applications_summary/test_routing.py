from unittest import mock

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse
from django.test import tag

from ...views.applications_summary import ApplicationsSummaryView
from ...services.db_gateways import NannyGatewayActions
from .. import utils


@tag('http')
class ApplicationsSummaryFunctionalTests(TestCase):
    """
    Testing the applications summary page
    """
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='governor_tARCin',
            email='test@test.com',
            password='my_secret'
        )
        g = Group.objects.create(name=settings.ARC_GROUP)
        g.user_set.add(self.user1)
        self.user2 = User.objects.create_user(
            username='cc_user',
            email='test1@test.com',
            password='my_secret'
        )
        e = Group.objects.create(name=settings.CONTACT_CENTRE)
        e.user_set.add(self.user2)

        global arc_test_user
        global cc_test_user
        arc_test_user = self.user1
        cc_test_user = self.user2

        self.client.login(username='governor_tARCin', password='my_secret')

    def test_can_render_applications_summary_page(self):
        """
        Test to check if the applications summary page can be rendered
        """
        with mock.patch.object(NannyGatewayActions, 'list') as mock_list:
            mock_list.return_value.status_code = 404
            response = self.client.get(reverse('applications-summary'))

            self.assertEqual(response.status_code, 200)
            utils.assertView(response, ApplicationsSummaryView)

