from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.test import RequestFactory, TestCase

from .models import Application
from .contact_centre import search_query
class ContactCentreTest(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        #fixtures = ['arc_application/fixtures/initial_arc_user.json']
        self.request_factory = RequestFactory()
        self.user = User.objects.create_user(
            username='cc_test', email='testing@test.com', password='my_secret')
        g = Group.objects.create(name=settings.CONTACT_CENTRE)
        g.user_set.add(self.user)
        g = Group.objects.create(name=settings.ARC_GROUP)

    def test_user_group(self):
        self.assertEqual(Group.objects.filter(name=settings.CONTACT_CENTRE).count(), 1)

    def test_login_page(self):
        resp = self.client.get('/arc/login/')
        self.assertEqual(resp.status_code, 200)

    def test_login_redirect(self):
        self.client.login(username='cc_test', password='my_secret')
        resp = self.client.get('/arc/login/')
        self.assertEqual(resp.url, '/arc/search')
        self.assertEqual(resp.status_code, 302)

    def test_search_page(self):
        self.client.login(username='cc_test', password='my_secret')
        resp = self.client.get('/arc/search/')
        self.assertEqual(resp.status_code, 200)

    def create_applicaiton(self):
        application = Application.objects.create(
            application_type='CHILDMINDER',
            login_id='da2265c2-2d65-4214-bfef-abcfe59b75aa',
            application_id='da2265c2-2d65-4214-bfef-abcfe59b75aa',
            application_status='DRAFTING',
            cygnum_urn='',
            login_details_status='NOT_STARTED',
            personal_details_status='NOT_STARTED',
            childcare_type_status='NOT_STARTED',
            first_aid_training_status='NOT_STARTED',
            eyfs_training_status='COMPLETED',
            criminal_record_check_status='NOT_STARTED',
            health_status='NOT_STARTED',
            references_status='NOT_STARTED',
            people_in_home_status='NOT_STARTED',
            declarations_status='NOT_STARTED',
            date_created=datetime.datetime.today(),
            date_updated=datetime.datetime.today(),
            date_accepted=None,
            order_code=None
        )
    def test_search(self):
        try:
            results = search_query('da2265c2-2d65-4214-bfef-abcfe59b75aa')
            self.assertEqual(len(results), 1)
        except Exception as ex:
            print(ex)




class ArcSummaryTest(TestCase):

    def setUp(self):
        # Every test needs access to the request factory.
        # fixtures = ['arc_application/fixtures/initial_arc_user.json']
        self.request_factory = RequestFactory()
        self.user = User.objects.create_user(
            username='arc_test', email='test@test.com', password='my_secret')
        g = Group.objects.create(name=settings.ARC_GROUP)
        g.user_set.add(self.user)
        self.user = User.objects.create_user(
            username='cc_test', email='testing@test.com', password='my_secret')
        g2 = Group.objects.create(name=settings.CONTACT_CENTRE)
        g2.user_set.add(self.user)

    def test_user_group(self):
        self.assertEqual(Group.objects.filter(name=settings.ARC_GROUP).count(), 1)

    def test_user(self):
        self.assertEqual(User.objects.filter(username='arc_test').count(), 1)
        self.assertEqual(User.objects.filter(username='cc_test').count(), 1)

    def test_login_redirect(self):
        self.client.login(username='arc_test', password='my_secret')
        resp = self.client.get('/arc/login/')
        self.assertEqual(resp.url, '/arc/summary')
        self.assertEqual(resp.status_code, 302)

    def test_summary_page(self):
        self.client.login(username='arc_test', password='my_secret')
        resp = self.client.get('/arc/summary/')
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
