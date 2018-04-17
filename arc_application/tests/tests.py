import datetime

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.test import RequestFactory, TestCase, Client
from django.urls import reverse

from arc_application.models import ApplicantName, ApplicantPersonalDetails, Application


class ContactCentreTest(TestCase):
    def setUp(self):
        self.request_factory = RequestFactory()
        self.app_id = None
        self.test_flow

    def test_flow(self):
        self.create_users
        self.create_applicaiton()
        # self.test_login_page()
        # self.test_login_redirect()
        # self.test_search_page()
        # self.test_empty_search()

    def create_users(self):
        self.cc_user = User.objects.create_user(
            username='cc_test', email='testing@test.com', password='my_secret')

        self.arc_user = User.objects.create_user(
            username='arc_test', email='testing@test.com', password='my_secret')
        g = Group.objects.create(name=settings.CONTACT_CENTRE)
        g.user_set.add(self.cc_user)
        g = Group.objects.create(name=settings.ARC_GROUP)
        g.user_set.add(self.arc_user)

    def create_applicaiton(self):
        application = Application.objects.create(
            application_type='CHILDMINDER',
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
        self.app = application

        details = ApplicantPersonalDetails.objects.create(
            personal_detail_id='da2265c2-2d65-4214-bfef-abcfe59b75aa',
            application_id=self.app,
            birth_day='01',
            birth_month='01',
            birth_year='2001'
        )
        self.personal_details = details

        name = ApplicantName.objects.create(
            name_id='da2265c2-2d65-4214-bfef-abcfe59b75aa',
            personal_detail_id=self.personal_details,
            application_id=self.app,
            current_name='True',
            first_name='Erik',
            middle_names='Tolstrup',
            last_name='Odense'
        )
        self.name = name




    # def test_login_page(self):
    #     resp = self.client.get('/arc/login/')
    #     self.assertEqual(resp.status_code, 200)
    #
    # def test_login_redirect(self):
    #     self.client.login(username='cc_test', password='my_secret')
    #     resp = self.client.get('/arc/login/')
    #     self.assertEqual(resp.url, '/arc/search')
    #     self.assertEqual(resp.status_code, 302)

    # def test_search_page(self):
    #     self.client.login(username='cc_test', password='my_secret')
    #     resp = self.client.get('/arc/search/')
    #     print("PATH: " +str(resp))
    #     self.assertEqual(resp.status_code, 200)
    #
    # def test_empty_search(self):
    #     self.client.login(username='cc_test', password='my_secret')
    #     r = self.client.post(reverse('search'), {
    #         'query': ''
    #     })
    #     self.assertEqual(r.status_code, 200)
    #
    # def test_partial_search_response(self):
    #     self.client.login(username='cc_test', password='my_secret')
    #     r = self.client.post(reverse('search'), {
    #         'query': 'ja'
    #     })
    #     self.assertEqual(r.status_code, 200)
    #
    # def test_search_summary(self):
    #     self.client.login(username='cc_test', password='my_secret')
    #     r = self.client.get("%s?application_id=da2265c2-2d65-4214-bfef-abcfe59b75aa" +reverse('search_summary'))
    #
    #     self.assertEqual(r.status_code, 200)


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

    # def test_summary_page(self):
    #     self.client.login(username='arc_test', password='my_secret')
    #     resp = self.client.get('/arc/summary/')
    #     self.assertEqual(resp.status_code, 200)

