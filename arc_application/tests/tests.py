import datetime

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.test import TestCase, RequestFactory
from django.urls import reverse

from ..models import (ApplicantName,
                      ApplicantPersonalDetails,
                      Application, UserDetails, Arc, ArcComments)


application = None
personal_details = None
name = None
user_details = None
arc_records = None
flagged_status = 'FLAGGED'


def create_application():
    global application
    global personal_details
    global name
    global user_details
    global arc_records

    application = Application.objects.create(
        application_type='CHILDMINDER',
        application_id='da2265c2-2d65-4214-bfef-abcfe59b75aa',
        application_status='DRAFTING',
        cygnum_urn='',
        login_details_status='NOT_STARTED',
        login_details_arc_flagged=False,
        personal_details_status='NOT_STARTED',
        personal_details_arc_flagged=False,
        childcare_type_status='NOT_STARTED',
        childcare_type_arc_flagged=False,
        first_aid_training_status='NOT_STARTED',
        first_aid_training_arc_flagged=False,
        eyfs_training_status='COMPLETED',
        eyfs_training_arc_flagged=False,
        criminal_record_check_status='NOT_STARTED',
        criminal_record_check_arc_flagged=False,
        health_status='NOT_STARTED',
        health_arc_flagged=False,
        references_status='NOT_STARTED',
        references_arc_flagged=False,
        people_in_home_status='NOT_STARTED',
        people_in_home_arc_flagged=False,
        declarations_status='NOT_STARTED',
        date_created=datetime.datetime.today(),
        date_updated=datetime.datetime.today(),
        date_accepted=None,
        order_code=None
    )

    details = ApplicantPersonalDetails.objects.create(
        personal_detail_id='da2265c2-2d65-4214-bfef-abcfe59b75aa',
        application_id=application,
        birth_day='01',
        birth_month='01',
        birth_year='2001'
    )

    personal_details = details

    name = ApplicantName.objects.create(
        name_id='da2265c2-2d65-4214-bfef-abcfe59b75aa',
        personal_detail_id=personal_details,
        application_id=application,
        current_name='True',
        first_name='Erik',
        middle_names='Tolstrup',
        last_name='Odense'
    )

    user_details = UserDetails.objects.create(
        login_id='8362d470-ecc9-4069-876b-9b3ddc2cae07',
        application_id=application,
        email='test@test.com',
    )

    arc_records = Arc.objects.create(
        application_id=application.application_id,
    )


class ContactCentreTest(TestCase):

    def setUp(self):
        self.request_factory = RequestFactory()
        self.app_id = None
        self.test_flow

    def test_flow(self):
        self.create_users
        create_application()

    def create_users(self):
        self.cc_user = User.objects.create_user(
            username='cc_test', email='testing@test.com', password='my_secret')

        self.arc_user = User.objects.create_user(
            username='arc_test', email='testing@test.com', password='my_secret')
        g = Group.objects.create(name=settings.CONTACT_CENTRE)
        g.user_set.add(self.cc_user)
        g = Group.objects.create(name=settings.ARC_GROUP)
        g.user_set.add(self.arc_user)


class ArcSummaryTest(TestCase):

    def setUp(self):
        # Every test needs access to the request factory.
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

    def test_task_flagged_with_comment_login_details(self):
        # Assemble
        create_application()

        post_dictionary = {
            'id': application.application_id,
            'mobile_number_declare': True,
            'mobile_number_comments': 'There was a test issue with this field'
        }

        # Act
        response = self.client.post(reverse('contact_summary'), post_dictionary)

        # Assert

        # 1. Check HTTP status code correct
        self.assertEqual(response.status_code, 302)

        # 2. Ensure overall task status marked as FLAGGED in ARC view
        reloaded_arc_record = Arc.objects.get(pk=application.application_id)
        self.assertEqual(reloaded_arc_record.login_details_review, flagged_status)

        # 3. Check that comment has been correctly appended to application
        try:
            arc_comments = ArcComments.objects.get(
                table_pk='8362d470-ecc9-4069-876b-9b3ddc2cae07',
                table_name='USER_DETAILS',
                field_name='mobile_number',
                comment='There was a test issue with this field',
                flagged=True,
            )
        except:
            self.fail('ARC comment could not be retrieved for flagged field')

        self.assertIsNotNone(arc_comments)

        # 4. Check flagged boolean indicator is set on the application record
        reloaded_application = Application.objects.get(pk=application.application_id)
        self.assertTrue(reloaded_application.login_details_arc_flagged)
