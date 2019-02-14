import datetime

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.test import TestCase, RequestFactory
from django.urls import reverse

from arc_application.childminder_task_util import get_number_of_tasks
from arc_application.models import (ApplicantHomeAddress,
                                    ApplicantName,
                                    ApplicantPersonalDetails,
                                    Application,
                                    Arc,
                                    ArcComments,
                                    ChildInHome,
                                    CriminalRecordCheck,
                                    FirstAidTraining,
                                    Reference,
                                    UserDetails,
                                    ChildcareType)
from ..views.childminder_views.type_of_childcare import get_register_name

application = None
personal_details = None
name = None
user_details = None
arc_records = None
flagged_status = 'FLAGGED'
arc_test_user = None
cc_test_user = None


def create_application():
    global application
    global personal_details
    global name
    global user_details
    global arc_records
    global childcare_type

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
        childcare_training_status='COMPLETED',
        childcare_training_arc_flagged=False,
        criminal_record_check_status='NOT_STARTED',
        criminal_record_check_arc_flagged=False,
        health_status='NOT_STARTED',
        health_arc_flagged=False,
        references_status='NOT_STARTED',
        references_arc_flagged=False,
        people_in_home_status='NOT_STARTED',
        people_in_home_arc_flagged=False,
        declarations_status='NOT_STARTED',
        adults_in_home=False,
        children_in_home=False,
        date_created=datetime.datetime.today(),
        date_updated=datetime.datetime.today(),
        date_accepted=None,
        reasons_known_to_social_services=None,
        known_to_social_services_pith=None,
        reasons_known_to_social_services_pith=None
    )

    details = ApplicantPersonalDetails.objects.create(
        personal_detail_id='da2265c2-2d65-4214-bfef-abcfe59b75aa',
        application_id=application,
        birth_day='01',
        birth_month='01',
        birth_year='2001'
    )

    childcare_type = ChildcareType.objects.create(
        application_id=application,
        zero_to_five=True,
        five_to_eight=True,
        eight_plus=True,
        overnight_care=True
    )

    personal_details = details

    home_address = ApplicantHomeAddress.objects.create(
        home_address_id='da2265c2-2d65-4214-bfef-abcfe59b75aa',
        personal_detail_id=personal_details,
        application_id=application,
        street_line1='1 Test Street',
        street_line2='',
        town='Testville',
        county='Testshire',
        country='Testland',
        postcode='WA14 4PX',
        current_address=True,
        childcare_address=True,
        move_in_month=0,
        move_in_year=0
    )

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

    first_aid_training = FirstAidTraining.objects.create(
        first_aid_id='da2265c2-2d65-4214-bfef-abcfe59b75aa',
        application_id=application,
        training_organisation='Test First Aid',
        course_title='Test First Aid',
        course_day='01',
        course_month='01',
        course_year='2018',
        show_certificate=True,
        renew_certificate=True
    )

    criminal_record_check = CriminalRecordCheck.objects.create(
        criminal_record_id='da2265c2-2d65-4214-bfef-abcfe59b75aa',
        application_id=application,
        dbs_certificate_number='123456654321',
        cautions_convictions=True
    )

    child_in_home = ChildInHome.objects.create(
        child_id='da2265c2-2d65-4214-bfef-abcfe59b75aa',
        application_id=application,
        child='1',
        first_name='Test',
        middle_names='Test',
        last_name='Test',
        birth_day='01',
        birth_month='01',
        birth_year='1995',
        relationship='Test'
    )

    reference1 = Reference.objects.create(
        reference_id='da2265c2-2d65-4214-bfef-abcfe59b75aa',
        application_id=application,
        reference='1',
        first_name='Test',
        last_name='Test',
        relationship='Test',
        years_known='1',
        months_known='1',
        street_line1='1 Test Street',
        street_line2='',
        town='Testville',
        county='Testshire',
        country='Testland',
        postcode='WA14 4PX',
        phone_number='07783446526',
        email='test@informed.com'
    )

    reference2 = Reference.objects.create(
        reference_id='da2265c2-2d65-4214-bfef-abcfe59b75ab',
        application_id=application,
        reference='2',
        first_name='Test',
        last_name='Test',
        relationship='Test',
        years_known='1',
        months_known='1',
        street_line1='1 Test Street',
        street_line2='',
        town='Testville',
        county='Testshire',
        country='Testland',
        postcode='WA14 4PX',
        phone_number='07783446526',
        email='test@informed.com'
    )

    global arc_test_user

    Arc.objects.create(
        application_id=application.application_id,
        user_id=arc_test_user.id
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

        global arc_test_user
        arc_test_user = self.user

        self.user = User.objects.create_user(
            username='cc_test', email='testing@test.com', password='my_secret')
        g2 = Group.objects.create(name=settings.CONTACT_CENTRE)
        g2.user_set.add(self.user)

        global cc_test_user
        cc_test_user = self.user

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

    def test_task_login_details(self):
        # Assemble
        create_application()

        post_dictionary = {
            'id': application.application_id,
        }

        # Act
        self.client.login(username='arc_test', password='my_secret')

        response = self.client.post(reverse('contact_summary'), post_dictionary)

        # Assert

        # 1. Check HTTP status code correct
        self.assertEqual(response.status_code, 302)

        # 2. Ensure overall task status marked as FLAGGED in ARC view
        reloaded_arc_record = Arc.objects.get(pk=application.application_id)
        self.assertEqual(reloaded_arc_record.login_details_review, 'COMPLETED')

        # 2. Check flagged boolean indicator is set on the application record
        reloaded_application = Application.objects.get(pk=application.application_id)
        self.assertTrue(not reloaded_application.login_details_arc_flagged)

    def test_task_flagged_with_comment_personal_details(self):
        # Assemble
        create_application()

        post_dictionary = {
            'id': application.application_id,
            'name_declare': True,
            'name_comments': 'There was a test issue with this field'
        }

        # Act
        self.client.login(username='arc_test', password='my_secret')
        response = self.client.post(reverse('personal_details_summary') + '?id=' + application.application_id,
                                    post_dictionary)

        # Assert

        # 1. Check HTTP status code correct
        self.assertEqual(response.status_code, 302)

        # 2. Ensure overall task status marked as FLAGGED in ARC view
        reloaded_arc_record = Arc.objects.get(pk=application.application_id)
        self.assertEqual(reloaded_arc_record.personal_details_review, flagged_status)

        # 3. Check that comment has been correctly appended to application
        try:
            arc_comments = ArcComments.objects.get(
                table_pk='da2265c2-2d65-4214-bfef-abcfe59b75aa',
                table_name='APPLICANT_NAME',
                field_name='name',
                comment='There was a test issue with this field',
                flagged=True,
            )
        except:
            self.fail('ARC comment could not be retrieved for flagged field')

        self.assertIsNotNone(arc_comments)

        # 4. Check flagged boolean indicator is set on the application record
        reloaded_application = Application.objects.get(pk=application.application_id)
        self.assertTrue(reloaded_application.personal_details_arc_flagged)

    def test_task_flagged_with_comment_first_aid_training(self):
        # Assemble
        create_application()

        post_dictionary = {
            'id': application.application_id,
            'first_aid_training_organisation_declare': True,
            'first_aid_training_organisation_comments': 'There was a test issue with this field'
        }

        # Act
        self.client.login(username='arc_test', password='my_secret')
        response = self.client.post(reverse('first_aid_training_summary') + '?id=' + application.application_id,
                                    post_dictionary)

        # Assert

        # 1. Check HTTP status code correct
        self.assertEqual(response.status_code, 302)

        # 2. Ensure overall task status marked as FLAGGED in ARC view
        reloaded_arc_record = Arc.objects.get(pk=application.application_id)
        self.assertEqual(reloaded_arc_record.first_aid_review, flagged_status)

        # 3. Check that comment has been correctly appended to application
        try:
            arc_comments = ArcComments.objects.get(
                table_pk='da2265c2-2d65-4214-bfef-abcfe59b75aa',
                table_name='FIRST_AID_TRAINING',
                field_name='first_aid_training_organisation',
                comment='There was a test issue with this field',
                flagged=True,
            )
        except:
            self.fail('ARC comment could not be retrieved for flagged field')

        self.assertIsNotNone(arc_comments)

        # 4. Check flagged boolean indicator is set on the application record
        reloaded_application = Application.objects.get(pk=application.application_id)
        self.assertTrue(reloaded_application.first_aid_training_arc_flagged)

    def test_task_flagged_with_comment_criminal_record_check(self):
        # Assemble
        create_application()

        post_dictionary = {
            'id': application.application_id,
            'dbs_certificate_number_declare': True,
            'dbs_certificate_number_comments': 'There was a test issue with this field'
        }

        # Act
        self.client.login(username='arc_test', password='my_secret')

        response = self.client.post(reverse('dbs_check_summary') + '?id=' + application.application_id,
                                    post_dictionary)

        # Assert

        # 1. Check HTTP status code correct
        self.assertEqual(response.status_code, 302)

        # 2. Ensure overall task status marked as FLAGGED in ARC view
        reloaded_arc_record = Arc.objects.get(pk=application.application_id)
        self.assertEqual(reloaded_arc_record.dbs_review, flagged_status)

        # 3. Check that comment has been correctly appended to application
        try:
            arc_comments = ArcComments.objects.get(
                table_pk='da2265c2-2d65-4214-bfef-abcfe59b75aa',
                table_name='CRIMINAL_RECORD_CHECK',
                field_name='dbs_certificate_number',
                comment='There was a test issue with this field',
                flagged=True,
            )
        except:
            self.fail('ARC comment could not be retrieved for flagged field')

        self.assertIsNotNone(arc_comments)

        # 4. Check flagged boolean indicator is set on the application record
        reloaded_application = Application.objects.get(pk=application.application_id)
        self.assertTrue(reloaded_application.criminal_record_check_arc_flagged)

    def test_task_flagged_with_comment_references(self):
        # Assemble
        create_application()

        post_dictionary = {
            'id': application.application_id,
            'form-relationship_declare': True,
            'form-relationship_comments': 'There was a test issue with this field'
        }

        # Act
        self.client.login(username='arc_test', password='my_secret')
        response = self.client.post(reverse('references_summary') + '?id=' + application.application_id,
                                    post_dictionary)

        # Assert

        # 1. Check HTTP status code correct
        self.assertEqual(response.status_code, 302)

        # 2. Ensure overall task status marked as FLAGGED in ARC view
        reloaded_arc_record = Arc.objects.get(pk=application.application_id)
        self.assertEqual(reloaded_arc_record.references_review, flagged_status)

        # 3. Check that comment has been correctly appended to application
        try:
            arc_comments = ArcComments.objects.get(
                table_pk='da2265c2-2d65-4214-bfef-abcfe59b75aa',
                table_name='REFERENCE',
                field_name='relationship',
                comment='There was a test issue with this field',
                flagged=True,
            )
        except:
            self.fail('ARC comment could not be retrieved for flagged field')

        self.assertIsNotNone(arc_comments)

        # 4. Check flagged boolean indicator is set on the application record
        reloaded_application = Application.objects.get(pk=application.application_id)
        self.assertTrue(reloaded_application.references_arc_flagged)

    def test_get_number_of_tasks(self):
        """
        Tests the get_number_of_tasks function
        """
        create_application()

        childcare_type.zero_to_five = True
        childcare_type.save()
        application.own_children = False
        application.working_in_other_childminder_home = True
        application.save()

        number_of_tasks = get_number_of_tasks(application, childcare_type)
        self.assertEqual(8, number_of_tasks)

        childcare_type.zero_to_five = True
        childcare_type.save()
        application.own_children = True
        application.working_in_other_childminder_home = True
        application.save()

        number_of_tasks = get_number_of_tasks(application, childcare_type)
        self.assertEqual(8, number_of_tasks)

        childcare_type.zero_to_five = True
        childcare_type.save()
        application.own_children = True
        application.working_in_other_childminder_home = False
        application.save()

        number_of_tasks = get_number_of_tasks(application, childcare_type)
        self.assertEqual(9, number_of_tasks)

        childcare_type.zero_to_five = False
        childcare_type.save()
        application.own_children = False
        application.working_in_other_childminder_home = True
        application.save()

        number_of_tasks = get_number_of_tasks(application, childcare_type)
        self.assertEqual(6, number_of_tasks)

        childcare_type.zero_to_five = False
        childcare_type.save()
        application.own_children = False
        application.working_in_other_childminder_home = False
        application.save()

        number_of_tasks = get_number_of_tasks(application, childcare_type)
        self.assertEqual(7, number_of_tasks)

        childcare_type.zero_to_five = False
        childcare_type.save()
        application.own_children = True
        application.working_in_other_childminder_home = False
        application.save()

        number_of_tasks = get_number_of_tasks(application, childcare_type)
        self.assertEqual(7, number_of_tasks)

        childcare_type.zero_to_five = True
        childcare_type.save()
        application.own_children = False
        application.working_in_other_childminder_home = False
        application.save()

        number_of_tasks = get_number_of_tasks(application, childcare_type)
        self.assertEqual(9, number_of_tasks)

        childcare_type.zero_to_five = False
        childcare_type.save()
        application.own_children = True
        application.working_in_other_childminder_home = True
        application.save()

        number_of_tasks = get_number_of_tasks(application, childcare_type)
        self.assertEqual(6, number_of_tasks)

    def test_get_register_name(self):
        """
        Tests the get_register_name function
        """
        create_application()

        childcare_type.zero_to_five = True
        childcare_type.five_to_eight = True
        childcare_type.eight_plus = True
        childcare_type.save()

        register = get_register_name(childcare_type)
        self.assertEqual('Early Years Register and Childcare Register (both parts)', register)

        childcare_type.zero_to_five = False
        childcare_type.five_to_eight = True
        childcare_type.eight_plus = True
        childcare_type.save()

        register = get_register_name(childcare_type)
        self.assertEqual('Childcare Register (both parts)', register)

        childcare_type.zero_to_five = True
        childcare_type.five_to_eight = False
        childcare_type.eight_plus = False
        childcare_type.save()

        register = get_register_name(childcare_type)
        self.assertEqual('Early Years Register', register)

        childcare_type.zero_to_five = True
        childcare_type.five_to_eight = True
        childcare_type.eight_plus = False
        childcare_type.save()

        register = get_register_name(childcare_type)
        self.assertEqual('Early Years Register and Childcare Register (compulsory part)', register)

        childcare_type.zero_to_five = True
        childcare_type.five_to_eight = False
        childcare_type.eight_plus = True
        childcare_type.save()

        register = get_register_name(childcare_type)
        self.assertEqual('Early Years Register and Childcare Register (voluntary part)', register)

        childcare_type.zero_to_five = False
        childcare_type.five_to_eight = True
        childcare_type.eight_plus = False
        childcare_type.save()

        register = get_register_name(childcare_type)
        self.assertEqual('Childcare Register (compulsory part)', register)

        childcare_type.zero_to_five = False
        childcare_type.five_to_eight = False
        childcare_type.eight_plus = True
        childcare_type.save()

        register = get_register_name(childcare_type)
        self.assertEqual('Childcare Register (voluntary part)', register)
