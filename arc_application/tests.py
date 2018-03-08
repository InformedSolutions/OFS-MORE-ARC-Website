from django.contrib.auth.models import Group, User
from django.test import Client, RequestFactory, TestCase

from .models import Arc


class ArcSummaryTest(TestCase):

    def setUp(self):
        # Every test needs access to the request factory.
        fixtures = ['arc_application/fixtures/initial_arc_user.json']
        self.request_factory = RequestFactory()
        self.user = User.objects.create_user(
            username='arc_test', email='test@test.com', password='my_secret')
        g = Group.objects.create(name='arc')
        g.user_set.add(self.user)
        self.user = User.objects.create_user(
            username='cc_test', email='testing@test.com', password='my_secret')
        g2 = Group.objects.create(name='contact-centre')
        g2.user_set.add(self.user)

    def test_user_group(self):
        self.assertEqual(Group.objects.filter(name='contact-centre').count(), 1)
        self.assertEqual(Group.objects.filter(name='arc').count(), 1)

    def test_user(self):
        self.assertEqual(User.objects.filter(username='arc_test').count(), 1)
        self.assertEqual(User.objects.filter(username='cc_test').count(), 1)

    def test_login_page(self):
        resp = self.client.get('/arc/login/')
        self.assertEqual(resp.status_code, 200)

    def test_summary_page(self):
        self.client.login(username='arc_test', password='my_secret')
        resp = self.client.get('/arc/summary/')
        self.assertEqual(resp.status_code, 200)

    def test_summary_page(self):
        self.client.login(username='cc_test', password='my_secret')
        resp = self.client.get('/arc/search/')
        self.assertEqual(resp.status_code, 200)
"""
    def test_assign_application(self):
        # This test is currently incomplete, and not that different than 'test_summary_page'
        self.client = Client()
        self.factory = RequestFactory()
        self.client.login(username='arc_test', password='my_secret')
        Arc.objects.create(user_id=self.user.id)
        request = self.client.get('arc/summary/')
        request.user = self.user

        # The line below is failing because the childminder models and table do not exist in the test db
        # response = assign_new_application(request)
        self.assertEqual(request.status_code, 200)
"""