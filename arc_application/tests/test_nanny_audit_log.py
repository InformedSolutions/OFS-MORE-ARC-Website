from unittest import TestCase

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.test import Client


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

        cls.client.login(username='governor_tARCin', password='my_secret')

        cls.user = User.objects.create_user(
            username='cc_test', email='cc_as_sunday@morning.com', password='my_secret')
        g2 = Group.objects.create(name=settings.CONTACT_CENTRE)
        g2.user_set.add(cls.user)

        global cc_test_user
        cc_test_user = cls.user

    def test_can_render_audit_log_page_as_arc_user(self):
        self.skipTest('NotImplemented')

    def test_can_render_audit_log_page_as_cc_user(self):
        self.skipTest('NotImplemented')

    def test_get_request_to_audit_log_page_as_cc_user_creates_timeline_log(self):
        self.skipTest('NotImplemented')

    def test_returning_application_creates_timeline_log(self):
        self.skipTest('NotImplemented')

    def test_accepting_application_creates_timeline_log(self):
        self.skipTest('NotImplemented')

    def test_assigning_application_creates_timeline_log(self):
        self.skipTest('NotImplemented')

    def test_releasing_application_creates_timeline_log(self):
        self.skipTest('NotImplemented')

    def test_adding_arc_comment_creates_timeline_log(self):
        self.skipTest('NotImplemented')
