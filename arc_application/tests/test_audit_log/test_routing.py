from unittest import mock, TestCase
import uuid

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.test import Client
from django.urls import reverse

from arc_application.tests.utils import side_effect

from arc_application.views.audit_log import audit_log_dispatcher


@mock.patch('arc_application.services.db_gateways.NannyGatewayActions.list', side_effect=side_effect)
@mock.patch('arc_application.services.db_gateways.NannyGatewayActions.create', side_effect=side_effect)
@mock.patch('arc_application.services.db_gateways.NannyGatewayActions.read', side_effect=side_effect)
class NannyAuditLogRoutingTests(TestCase):

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

    # def test_can_render_audit_log_page_as_arc_user(self, mock_create, mock_list, mock_read):
    #     response = self.client.get(reverse('auditlog') + '?id=' + self.application_id  + '&app_type=Nanny')
    #
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.resolver_match.func.__name__, audit_log_dispatcher.__name__)
    #
    # def test_can_render_audit_log_page_as_cc_user(self, mock_create, mock_list, mock_read):
    #     self.client.logout()
    #     self.client.login(username='cc_test', password='my_secret')
    #
    #     response = self.client.get(reverse('auditlog') + '?id=' + self.application_id + '&app_type=Nanny')
    #
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.resolver_match.func.__name__, audit_log_dispatcher.__name__)
    #
    #     self.client.logout()

    def test_get_request_to_audit_log_page_as_cc_user_creates_timeline_log(self, mock_create, mock_list, mock_read):
        self.client.logout()
        self.client.login(username='cc_test', password='my_secret')

        self.client.get(reverse('auditlog') + '?id=' + self.application_id + '&app_type=Nanny')

        # self.assertTrue(mock_create.called)
        # self.assertTrue(mock_create.call_args_list, [])
        self.skipTest('NotImplemented')

    def test_returning_application_creates_timeline_log(self, mock_create, mock_list, mock_read):
        self.skipTest('NotImplemented')

    def test_accepting_application_creates_timeline_log(self, mock_create, mock_list, mock_read):
        self.skipTest('NotImplemented')

    def test_assigning_application_creates_timeline_log(self, mock_create, mock_list, mock_read):
        self.skipTest('NotImplemented')

    def test_releasing_application_creates_timeline_log(self, mock_create, mock_list, mock_read):
        self.skipTest('NotImplemented')

    def test_adding_arc_comment_to_personal_details_creates_timeline_log(self, mock_create, mock_list, mock_read):
        # self.client.post(reverse('nanny_personal_details_summary') + '?id=' + self.application_id,
        #                  data={
        #                      'name_declare': 'on',
        #                      'name_comments': 'Flag name',
        #                      'date_of_birth_declare': 'on',
        #                      'date_of_birth_comments': 'Flag DoB',
        #                      'lived_abroad_declare': 'on',
        #                      'lived_abroad_comments': 'Flag lived abroad',
        #                  })
        #
        # self.assertTrue(mock_create.called_with('timeline-log', params={}))
        self.skipTest('NotImplemented')

    def test_adding_arc_comment_to_first_aid_training_creates_timeline_log(self, mock_create, mock_list, mock_read):
        # self.client.post(reverse('nanny_first_aid_training_summary') + '?id=' + self.application_id,
        #                  data={
        #                      'training_organisation_declare':'on',
        #                      'training_organisation_comments': 'Flag training organisation',
        #                      'course_title_declare': 'on',
        #                      'course_title_comments': 'Flag course title',
        #                      'course_date_declare': 'on',
        #                      'course_date_comments': 'Flag course date'
        #                  })
        #
        # self.assertTrue(mock_create.called_with('timeline-log', params={}))
        self.skipTest('NotImplemented')

    def test_adding_arc_comment_to_childcare_training_creates_timeline_log(self, mock_create, mock_list, mock_read):
        # self.client.post(reverse('nanny_childcare_training_summary') + '?id=' + self.application_id,
        #                  data={
        #                      'childcare_training_declare': 'on',
        #                      'childcare_training_comments': 'Flag childcare training'
        #                  })
        #
        # self.assertTrue(mock_create.called_with('timeline-log', params={}))
        self.skipTest('NotImplemented')

    def test_adding_arc_comment_to_dbs_checks_creates_timeline_log(self, mock_create, mock_list, mock_read):
        # self.client.post(reverse('nanny_dbs_summary') + '?id=' + self.application_id,
        #                  data={
        #                     'dbs_number_declare': 'on',
        #                     'dbs_number_comments': 'Flag DBS number',
        #                     'convictions_declare': 'on',
        #                     'convictions_comments': 'Flag convictions'
        #                  })
        #
        # self.assertTrue(mock_create.called_with('timeline-log', params={}))
        self.skipTest('NotImplemented')

    def test_adding_arc_comment_to_insurance_cover_creates_timeline_log(self, mock_create, mock_list, mock_read):
        # self.client.post(reverse('nanny_insurance_cover_summary') + '?id=' + self.application_id,
        #                  data={
        #                     'public_liability_declare': 'on',
        #                     'public_liability_comments': 'Flag public liability insurance'
        #                  })
        #
        # self.assertTrue(mock_create.called_with('timeline-log', params={}))
        self.skipTest('NotImplemented')

    def test_duplicate_log_not_added_if_preexisting_arc_comment(self, mock_create, mock_list, mock_read):
        self.skipTest('NotImplemented')
