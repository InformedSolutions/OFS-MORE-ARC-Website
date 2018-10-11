from unittest import mock, TestCase
import uuid

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.test import Client
from django.urls import reverse

from .test_utils import side_effect

from arc_application.views.audit_log import AuditlogListView


@mock.patch('arc_application.services.db_gateways.NannyGatewayActions.list', side_effect=side_effect)
@mock.patch('arc_application.services.db_gateways.NannyGatewayActions.create', side_effect=side_effect)
class NannyAuditLogTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = Client()
        cls.user = User.objects.create_user(
            username='governor_tARCin',
            email='test@test.com',
            password='my_secret'
        )
        g = Group.objects.create(name=settings.ARC_GROUP)
        g.user_set.add(cls.user)

        global arc_test_user
        arc_test_user = cls.user

        cls.user = User.objects.create_user(
            username='cc_test', email='cc_as_sunday@morning.com', password='my_secret')
        g2 = Group.objects.create(name=settings.CONTACT_CENTRE)
        g2.user_set.add(cls.user)

        global cc_test_user
        cc_test_user = cls.user

        cls.application_id = str(uuid.uuid4())

    def setUp(self):
        self.client.login(username='governor_tARCin', password='my_secret')

    def test_can_render_audit_log_page_as_arc_user(self, mock_create, mock_list):
        response = self.client.get(reverse('auditlog') + '?id=' + self.application_id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__, NannyAuditlogListView.__name__)

    def test_can_render_audit_log_page_as_cc_user(self, mock_create, mock_list):
        self.client.logout()
        self.client.login(username='cc_test', password='my_secret')

        response = self.client.get(reverse('auditlog') + '?id=' + self.application_id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__, NannyAuditlogListView.__name__)

        self.client.logout()

    def test_get_request_to_audit_log_page_as_cc_user_creates_timeline_log(self, mock_create, mock_list):
        self.client.logout()
        self.client.login(username='cc_test', password='my_secret')

        self.client.get(reverse('auditlog') + '?id=' + self.application_id)

        self.assertTrue(mock_create.called)
        self.assertTrue(mock_create.call_args_list, [])

    def test_returning_application_creates_timeline_log(self, mock_create, mock_list):
        self.skipTest('NotImplemented')

    def test_accepting_application_creates_timeline_log(self, mock_create, mock_list):
        self.skipTest('NotImplemented')

    def test_assigning_application_creates_timeline_log(self, mock_create, mock_list):
        self.skipTest('NotImplemented')

    def test_releasing_application_creates_timeline_log(self, mock_create, mock_list):
        self.skipTest('NotImplemented')

    def test_adding_arc_comment_creates_timeline_log(self, mock_create, mock_list):
        self.skipTest('NotImplemented')
