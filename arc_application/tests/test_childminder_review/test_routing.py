import logging

from datetime import datetime, timezone
from unittest import skip
from unittest.mock import patch

from django.test import TestCase, tag
from django.urls import reverse

from ...tests import utils
from ...tests.utils import create_childminder_application, create_arc_user
from ...models import *


log = logging.getLogger('')

ARC_STATUS_FLAGGED = 'FLAGGED'
ARC_STATUS_COMPLETED = 'COMPLETED'

APP_STATUS_FLAGGED = 'FLAGGED'
APP_STATUS_NOT_STARTED = 'NOT_STARTED'
APP_STATUS_COMPLETED = 'COMPLETED'
APP_STATUS_FURTHER_INFO = 'FURTHER_INFORMATION'
APP_STATUS_REVIEW = 'ARC_REVIEW'
APP_STATUS_ACCEPTED = 'ACCEPTED'


@tag('http')
class SignInDetailsPageFunctionalTests(TestCase):

    def setUp(self):
        self.arc_user = create_arc_user()
        self.application = create_childminder_application(self.arc_user.pk)
        self.client.login(username='arc_test', password='my_secret')

    def test_can_render_page(self):

        response = self.client.get(reverse('contact_summary'), data={'id': self.application.pk})

        self.assertEqual(200, response.status_code)
        utils.assertView(response, 'contact_summary')

    def test_submit_redirects_to_type_of_childcare_page_if_valid(self):
        self.skipTest('testNotImplemented')


@tag('http')
class TypeOfChildcarePageFunctionalTests(TestCase):

    def setUp(self):
        self.arc_user = create_arc_user()
        self.application = create_childminder_application(self.arc_user.pk)
        self.client.login(username='arc_test', password='my_secret')

    def test_can_render_page(self):

        response = self.client.get(reverse('type_of_childcare_age_groups'), data={'id': self.application.pk})

        self.assertEqual(200, response.status_code)
        utils.assertView(response, 'type_of_childcare_age_groups')

    def test_submit_redirects_to_personal_details_page_if_valid(self):
        self.skipTest('testNotImplemented')


@tag('http')
class PersonalDetailsPageFunctionalTests(TestCase):

    def setUp(self):
        self.arc_user = create_arc_user()
        self.application = create_childminder_application(self.arc_user.pk)
        self.client.login(username='arc_test', password='my_secret')

    def test_can_render_page(self):

        response = self.client.get(reverse('personal_details_summary'), data={'id': self.application.pk})

        self.assertEqual(200, response.status_code)
        utils.assertView(response, 'personal_details_summary')

    def test_submitting_comment_for_field_on_personal_details_page_adds_flag_in_database(self):

        # Assemble
        post_dictionary = {
            'id': self.application.application_id,
            'name_declare': True,
            'name_comments': 'There was a test issue with this field'
        }

        # Act
        response = self.client.post(reverse('personal_details_summary') + '?id=' + self.application.application_id,
                                    post_dictionary)

        # Assert

        # 1. Check HTTP status code correct
        self.assertEqual(response.status_code, 302)

        # 2. Ensure overall task status marked as FLAGGED in ARC view
        reloaded_arc_record = Arc.objects.get(pk=self.application.application_id)
        self.assertEqual(reloaded_arc_record.personal_details_review, ARC_STATUS_FLAGGED)

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
        reloaded_application = Application.objects.get(pk=self.application.application_id)
        self.assertTrue(reloaded_application.personal_details_arc_flagged)

    def test_submit_redirects_to_first_aid_page_if_valid(self):
        self.skipTest('testNotImplemented')


@tag('http')
class FirstAidPageFunctionalTests(TestCase):

    def setUp(self):
        self.arc_user = create_arc_user()
        self.application = create_childminder_application(self.arc_user.pk)
        self.client.login(username='arc_test', password='my_secret')

    def test_can_render_page(self):

        response = self.client.get(reverse('first_aid_training_summary'), data={'id': self.application.pk})

        self.assertEqual(200, response.status_code)
        utils.assertView(response, 'first_aid_training_summary')

    def test_submitting_comment_for_field_on_first_aid_page_adds_flag_in_database(self):
        # Assemble
        post_dictionary = {
            'id': self.application.application_id,
            'first_aid_training_organisation_declare': True,
            'first_aid_training_organisation_comments': 'There was a test issue with this field'
        }

        # Act
        response = self.client.post(reverse('first_aid_training_summary') + '?id=' + self.application.application_id,
                                    post_dictionary)

        # Assert

        # 1. Check HTTP status code correct
        self.assertEqual(response.status_code, 302)

        # 2. Ensure overall task status marked as FLAGGED in ARC view
        reloaded_arc_record = Arc.objects.get(pk=self.application.application_id)
        self.assertEqual(reloaded_arc_record.first_aid_review, ARC_STATUS_FLAGGED)

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
        reloaded_application = Application.objects.get(pk=self.application.application_id)
        self.assertTrue(reloaded_application.first_aid_training_arc_flagged)

    def test_submit_redirects_to_childcare_training_page_if_valid(self):
        self.skipTest('testNotImplemented')


@tag('http')
class ChildcareTrainingPageFunctionalTests(TestCase):

    def setUp(self):
        self.arc_user = create_arc_user()
        self.application = create_childminder_application(self.arc_user.pk)
        self.client.login(username='arc_test', password='my_secret')

    def test_can_render_page(self):

        response = self.client.get(reverse('childcare_training_check_summary'), data={'id': self.application.pk})

        self.assertEqual(200, response.status_code)
        utils.assertView(response, 'ChildcareTrainingCheckSummaryView')

    def test_submit_redirects_to_health_declaration_page_if_valid(self):
        self.skipTest('testNotImplemented')


@tag('http')
class HealthDeclarationPageFunctionalTests(TestCase):

    def setUp(self):
        self.arc_user = create_arc_user()
        self.application = create_childminder_application(self.arc_user.pk)
        self.client.login(username='arc_test', password='my_secret')

    def test_can_render_page(self):

        response = self.client.get(reverse('health_check_answers'), data={'id': self.application.pk})

        self.assertEqual(200, response.status_code)
        utils.assertView(response, 'health_check_answers')

    def test_submit_redirects_to_criminal_record_page_if_valid(self):
        self.skipTest('testNotImplemented')


@tag('http')
class CriminalRecordCheckPageFunctionalTests(TestCase):

    def setUp(self):
        self.arc_user = create_arc_user()
        self.application = create_childminder_application(self.arc_user.pk)
        self.client.login(username='arc_test', password='my_secret')

    def test_can_render_page(self):

        response = self.client.get(reverse('dbs_check_summary'), data={'id': self.application.pk})

        self.assertEqual(200, response.status_code)
        utils.assertView(response, 'dbs_check_summary')

    def test_submitting_comment_for_field_on_criminal_record_check_page_adds_flag_in_database(self):
        # Assemble
        post_dictionary = {
            'id': self.application.application_id,
            'dbs_certificate_number_declare': True,
            'dbs_certificate_number_comments': 'There was a test issue with this field'
        }

        # Act
        response = self.client.post(reverse('dbs_check_summary') + '?id=' + self.application.application_id,
                                    post_dictionary)

        # Assert

        # 1. Check HTTP status code correct
        self.assertEqual(response.status_code, 302)

        # 2. Ensure overall task status marked as FLAGGED in ARC view
        reloaded_arc_record = Arc.objects.get(pk=self.application.application_id)
        self.assertEqual(reloaded_arc_record.dbs_review, ARC_STATUS_FLAGGED)

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
        reloaded_application = Application.objects.get(pk=self.application.application_id)
        self.assertTrue(reloaded_application.criminal_record_check_arc_flagged)

    def test_submit_redirects_to_people_in_home_page_if_valid(self):
        self.skipTest('testNotImplemented')


@tag('http')
class PeopleInTheHomeFunctionalTests(TestCase):

    def setUp(self):

        self.arc_user = create_arc_user()
        self.application = create_childminder_application(self.arc_user.pk)

        self.client.login(username='arc_test', password='my_secret')

    def test_can_render_page(self):

        response = self.client.get(reverse('other_people_summary'), data={'id': self.application.pk})

        self.assertEqual(200, response.status_code)
        utils.assertView(response, 'other_people_summary')

    def test_displays_adults_main_info_that_is_always_shown(self):

        self.application.adults_in_home = True
        self.application.working_in_other_childminder_home = False
        self.application.save()

        adult = AdultInHome.objects.get(application_id=self.application.pk)
        adult.first_name = 'Joe'
        adult.middle_names = 'Anthony'
        adult.last_name = 'Bloggs'
        adult.birth_day = 28
        adult.birth_month = 2
        adult.birth_year = 1972
        adult.relationship = 'Uncle'
        adult.email = 'foo@example.com'
        adult.lived_abroad = False
        adult.dbs_certificate_number = '123456789012'
        adult.capita = True
        adult.save()

        response = self.client.get(reverse('other_people_summary'), data={'id': self.application.pk})

        utils.assertSummaryField(response, 'Does anyone aged 16 or over live or work in the home?', 'Yes',
                                 heading='Adults in the home')

        utils.assertSummaryField(response, 'Name', 'Joe Anthony Bloggs', heading='Joe Anthony Bloggs')
        # TODO: display of months on this page are inconsistent with other pages
        utils.assertSummaryField(response, 'Date of birth', '28 February 1972', heading='Joe Anthony Bloggs')
        utils.assertSummaryField(response, 'Relationship', 'Uncle', heading='Joe Anthony Bloggs')
        utils.assertSummaryField(response, 'Email', 'foo@example.com', heading='Joe Anthony Bloggs')
        utils.assertSummaryField(response, 'Lived abroad in the last 5 years?', 'No', heading='Joe Anthony Bloggs')
        # military base field is conditional
        utils.assertSummaryField(response, 'Did they get their DBS check from the Ofsted DBS application website?',
                                 'Yes', heading='Joe Anthony Bloggs')
        # last three months field is conditional
        utils.assertSummaryField(response, 'DBS certificate number', '123456789012', heading='Joe Anthony Bloggs')
        # enhanced-check and on-update fields are conditional

    def test_displays_adult_military_base_field_if_caring_for_zero_to_five_year_olds(self):

        self.application.adults_in_home = True
        self.application.working_in_other_childminder_home = False
        self.application.save()

        adult = AdultInHome.objects.get(application_id=self.application.pk)
        adult.military_base = True
        adult.save()

        care_type = ChildcareType.objects.get(application_id=self.application.pk)
        care_type.zero_to_five = True
        care_type.save()

        response = self.client.get(reverse('other_people_summary'), data={'id': self.application.pk})

        utils.assertSummaryField(response, 'Lived or worked on British military base in the last 5 years?', 'Yes')

    def test_doesnt_display_adult_military_base_field_if_not_caring_for_zero_to_five_year_olds(self):

        self.application.adults_in_home = True
        self.application.working_in_other_childminder_home = False
        self.application.save()

        care_type = ChildcareType.objects.get(application_id=self.application.pk)
        care_type.zero_to_five = False
        care_type.save()

        response = self.client.get(reverse('other_people_summary'), data={'id': self.application.pk})

        utils.assertNotSummaryField(response, 'Lived or worked on British military base in the last 5 years?')

    def test_displays_adult_dbs_recent_field_only_for_adults_on_capita_list(self):

        self.application.adults_in_home = True
        self.application.working_in_other_childminder_home = False
        self.application.save()

        adult1 = AdultInHome.objects.get(application_id=self.application.pk)
        adult1.first_name = 'Joe'
        adult1.middle_names = 'Anthony'
        adult1.last_name = 'Bloggs'
        adult1.dbs_certificate_number = '123456789012'
        adult1.capita = False
        adult1.save()

        AdultInHome.objects.create(
            application_id=self.application,
            first_name='Freda', middle_names='Annabel', last_name='Smith',
            birth_day=1, birth_month=2, birth_year=1983,
            dbs_certificate_number='123456789013',
            capita=True,
            within_three_months=False,
            certificate_information='',
        )

        response = self.client.get(reverse('other_people_summary'), data={'id': self.application.pk})

        utils.assertNotSummaryField(response, 'Is it dated within the last 3 months?', heading='Joe Anthony Bloggs')
        utils.assertSummaryField(response, 'Is it dated within the last 3 months?', 'No', heading='Freda Annabel Smith')

    def test_displays_adult_dbs_enhanced_check_field_only_for_adults_not_on_capita_list(self):

        self.application.adults_in_home = True
        self.application.working_in_other_childminder_home = False
        self.application.save()

        adult1 = AdultInHome.objects.get(application_id=self.application.pk)
        adult1.first_name = 'Joe'
        adult1.middle_names = 'Anthony'
        adult1.last_name = 'Bloggs'
        adult1.dbs_certificate_number = '123456789012'
        adult1.capita = False
        adult1.enhanced_check = True
        adult1.on_update = True
        adult1.save()

        AdultInHome.objects.create(
            application_id=self.application,
            first_name='Freda', middle_names='Annabel', last_name='Smith',
            birth_day=1, birth_month=2, birth_year=1983,
            dbs_certificate_number='123456789013',
            capita=True,
            within_three_months=False,
            certificate_information='',
            enhanced_check=None,
            on_update=True,
        )

        response = self.client.get(reverse('other_people_summary'), data={'id': self.application.pk})

        utils.assertSummaryField(response, 'Enhanced DBS check for home-based childcare?', 'Yes',
                                 heading='Joe Anthony Bloggs')
        utils.assertNotSummaryField(response, 'Enhanced DBS check for home-based childcare?',
                                    heading='Freda Annabel Smith')

    def test_displays_adult_dbs_on_update_field_only_for_adults_with_enhanced_check_dbs_not_on_list_or_not_recent_enough(
            self):

        self.application.adults_in_home = True
        self.application.working_in_other_childminder_home = False
        self.application.save()

        adult1 = AdultInHome.objects.get(application_id=self.application.pk)
        adult1.first_name = 'Joe'
        adult1.middle_names = 'Anthony'
        adult1.last_name = 'Bloggs'
        adult1.dbs_certificate_number = '123456789012'
        adult1.capita = False
        adult1.enhanced_check = True
        adult1.on_update = True
        adult1.save()

        AdultInHome.objects.create(
            application_id=self.application,
            first_name='Freda', middle_names='Annabel', last_name='Smith',
            birth_day=1, birth_month=2, birth_year=1983,
            dbs_certificate_number='123456789013',
            capita=True,
            within_three_months=False,
            certificate_information='',
            enhanced_check=None,
            on_update=False,
        )

        AdultInHome.objects.create(
            application_id=self.application,
            first_name='Jim', middle_names='Bob', last_name='Robertson',
            birth_day=1, birth_month=3, birth_year=1985,
            dbs_certificate_number='123456789014',
            capita=True,
            within_three_months=True,
            certificate_information='',
            enhanced_check=None,
            on_update=None,
        )

        response = self.client.get(reverse('other_people_summary'), data={'id': self.application.pk})

        utils.assertSummaryField(response, 'On the update service?', 'Yes', heading='Joe Anthony Bloggs')
        utils.assertSummaryField(response, 'On the update service?', 'No', heading='Freda Annabel Smith')
        utils.assertNotSummaryField(response, 'On the update service?', heading='Jim Bob Robertson')

    # TODO: adult known-to-council-services-field

    # TODO: own child known-to-council-services field

    def test_submitting_comment_on_field_adds_flag_in_database(self):

        data = self._make_post_data(adults=1)

        data.update({
            'static-adults_in_home_declare': 'on',
            'static-adults_in_home_comments': 'There was a test issue with this field',
            'adult-0-cygnum_relationship': 'Brother'
        })

        response = self.client.post(reverse('other_people_summary'), data)

        self.assertEqual(response.status_code, 302)

        # Ensure overall task status marked as FLAGGED in ARC record
        reloaded_arc_record = Arc.objects.get(pk=self.application.application_id)
        self.assertEqual(reloaded_arc_record.people_in_home_review, ARC_STATUS_FLAGGED)

        # Check that comment has been correctly appended to application
        arc_comments = ArcComments.objects.get(
            table_pk='da2265c2-2d65-4214-bfef-abcfe59b75aa',
            table_name='APPLICATION',
            field_name='adults_in_home',
            comment='There was a test issue with this field',
            flagged=True,
        )
        self.assertIsNotNone(arc_comments)

        # Check flagged boolean indicator is set on the application record
        reloaded_application = Application.objects.get(pk=self.application.application_id)
        self.assertTrue(reloaded_application.people_in_home_arc_flagged)

    def test_submit_redirects_to_references_page_if_valid(self):
        self.skipTest('testNotImplemented')

    def _make_post_data(self, adults=0, children=0, own_children=0, own_child_addresses=0):
        """Prepares dictionary of post data with necessary form-management fields"""

        data = {'id': self.application.application_id}

        for form_type, quantity in [('adult', adults),
                                    ('child', children),
                                    ('own_child_not_in_home', own_children),
                                    ('own_child_not_in_home_address', own_child_addresses)]:
            data['{}-TOTAL_FORMS'.format(form_type)] = str(quantity)
            data['{}-INITIAL_FORMS'.format(form_type)] = str(quantity)
            data['{}-MIN_NUM_FORMS'.format(form_type)] = '0'
            data['{}-MAX_NUM_FORMS'.format(form_type)] = '1000'

        return data


@tag('http')
class ReferencesPageFunctionalTests(TestCase):

    def setUp(self):
        self.arc_user = create_arc_user()
        self.application = create_childminder_application(self.arc_user.pk)
        self.client.login(username='arc_test', password='my_secret')

    def test_can_render_page(self):

        response = self.client.get(reverse('references_summary'), data={'id': self.application.pk})

        self.assertEqual(200, response.status_code)
        utils.assertView(response, 'references_summary')

    def test_submitting_comment_on_field_on_references_page_adds_flag_in_database(self):
        # Assemble
        post_dictionary = {
            'id': self.application.application_id,
            'form-relationship_declare': True,
            'form-relationship_comments': 'There was a test issue with this field'
        }

        # Act
        response = self.client.post(reverse('references_summary') + '?id=' + self.application.application_id,
                                    post_dictionary)

        # Assert

        # 1. Check HTTP status code correct
        self.assertEqual(response.status_code, 302)

        # 2. Ensure overall task status marked as FLAGGED in ARC view
        reloaded_arc_record = Arc.objects.get(pk=self.application.application_id)
        self.assertEqual(reloaded_arc_record.references_review, ARC_STATUS_FLAGGED)

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
        reloaded_application = Application.objects.get(pk=self.application.application_id)
        self.assertTrue(reloaded_application.references_arc_flagged)

    def test_submit_redirects_to_task_list_page_if_valid(self):
        self.skipTest('testNotImplemented')


@tag('http')
class ReviewSummaryAndConfirmationFunctionalTests(TestCase):

    def setUp(self):
        self.arc_user = create_arc_user()
        self.application = create_childminder_application(self.arc_user.pk)
        self.client.login(username='arc_test', password='my_secret')

    def test_can_render_page(self):

        response = self.client.get(reverse('arc-summary'), data={'id': self.application.pk})

        self.assertEqual(200, response.status_code)
        utils.assertView(response, 'arc_summary')

    def test_displays_adults_main_info_that_is_always_shown(self):

        self.application.adults_in_home = True
        self.application.working_in_other_childminder_home = False
        self.application.save()

        adult = AdultInHome.objects.get(application_id=self.application.pk)
        adult.first_name = 'Joe'
        adult.middle_names = 'Anthony'
        adult.last_name = 'Bloggs'
        adult.birth_day = 28
        adult.birth_month = 2
        adult.birth_year = 1972
        adult.relationship = 'Uncle'
        adult.email = 'foo@example.com'
        adult.lived_abroad = False
        adult.dbs_certificate_number = '123456789012'
        adult.capita = True
        adult.save()

        response = self.client.get(reverse('arc-summary'), data={'id': self.application.pk})

        utils.assertSummaryField(response, 'Does anyone aged 16 or over live or work in your home?', 'Yes',
                                 heading='Adults in the home')

        utils.assertSummaryField(response, 'Name', 'Joe Anthony Bloggs', heading='Joe Anthony Bloggs')
        # TODO: display of months on this page are inconsistent with other pages
        utils.assertSummaryField(response, 'Date of birth', '28 02 1972', heading='Joe Anthony Bloggs')
        utils.assertSummaryField(response, 'Relationship', 'Uncle', heading='Joe Anthony Bloggs')
        utils.assertSummaryField(response, 'Email', 'foo@example.com', heading='Joe Anthony Bloggs')
        utils.assertSummaryField(response, 'Lived abroad in the last 5 years?', 'No', heading='Joe Anthony Bloggs')
        # military base field is conditional
        utils.assertSummaryField(response, 'Did they get their DBS check from the Ofsted DBS application website?',
                                 'Yes', heading='Joe Anthony Bloggs')
        # last three months field is conditional
        utils.assertSummaryField(response, 'DBS certificate number', '123456789012', heading='Joe Anthony Bloggs')
        # enhanced-check and on-update fields are conditional

    def test_displays_adult_military_base_field_if_caring_for_zero_to_five_year_olds(self):

        self.application.adults_in_home = True
        self.application.working_in_other_childminder_home = False
        self.application.save()

        adult = AdultInHome.objects.get(application_id=self.application.pk)
        adult.military_base = True
        adult.save()

        care_type = ChildcareType.objects.get(application_id=self.application.pk)
        care_type.zero_to_five = True
        care_type.save()

        response = self.client.get(reverse('arc-summary'), data={'id': self.application.pk})

        utils.assertSummaryField(response, 'Lived or worked on British military base in the last 5 years?', 'Yes')

    def test_doesnt_display_adult_military_base_field_if_not_caring_for_zero_to_five_year_olds(self):

        self.application.adults_in_home = True
        self.application.working_in_other_childminder_home = False
        self.application.save()

        care_type = ChildcareType.objects.get(application_id=self.application.pk)
        care_type.zero_to_five = False
        care_type.save()

        response = self.client.get(reverse('arc-summary'), data={'id': self.application.pk})

        utils.assertNotSummaryField(response, 'Lived or worked on British military base in the last 5 years?')

    def test_displays_adult_dbs_recent_field_only_for_adults_on_capita_list(self):

        self.application.adults_in_home = True
        self.application.working_in_other_childminder_home = False
        self.application.save()

        adult1 = AdultInHome.objects.get(application_id=self.application.pk)
        adult1.first_name = 'Joe'
        adult1.middle_names = 'Anthony'
        adult1.last_name = 'Bloggs'
        adult1.dbs_certificate_number = '123456789012'
        adult1.capita = False
        adult1.save()

        AdultInHome.objects.create(
            application_id=self.application,
            first_name='Freda', middle_names='Annabel', last_name='Smith',
            birth_day=1, birth_month=2, birth_year=1983,
            dbs_certificate_number='123456789013',
            capita=True,
            within_three_months=False,
            certificate_information='',
        )

        response = self.client.get(reverse('arc-summary'), data={'id': self.application.pk})

        utils.assertNotSummaryField(response, 'Is it dated within the last 3 months?', heading='Joe Anthony Bloggs')
        utils.assertSummaryField(response, 'Is it dated within the last 3 months?', 'No', heading='Freda Annabel Smith')

    def test_displays_adult_dbs_enhanced_check_field_only_for_adults_not_on_capita_list(self):

        self.application.adults_in_home = True
        self.application.working_in_other_childminder_home = False
        self.application.save()

        adult1 = AdultInHome.objects.get(application_id=self.application.pk)
        adult1.first_name = 'Joe'
        adult1.middle_names = 'Anthony'
        adult1.last_name = 'Bloggs'
        adult1.dbs_certificate_number = '123456789012'
        adult1.capita = False
        adult1.enhanced_check = True
        adult1.on_update = True
        adult1.save()

        AdultInHome.objects.create(
            application_id=self.application,
            first_name='Freda', middle_names='Annabel', last_name='Smith',
            birth_day=1, birth_month=2, birth_year=1983,
            dbs_certificate_number='123456789013',
            capita=True,
            within_three_months=False,
            certificate_information='',
            enhanced_check=None,
            on_update=True,
        )

        response = self.client.get(reverse('arc-summary'), data={'id': self.application.pk})

        utils.assertSummaryField(response, 'Enhanced DBS check for home-based childcare?', 'Yes',
                                 heading='Joe Anthony Bloggs')
        utils.assertNotSummaryField(response, 'Enhanced DBS check for home-based childcare?',
                                    heading='Freda Annabel Smith')

    def test_displays_adult_dbs_on_update_field_only_for_adults_with_enhanced_check_dbs_not_on_list_or_not_recent_enough(
            self):

        self.application.adults_in_home = True
        self.application.working_in_other_childminder_home = False
        self.application.save()

        adult1 = AdultInHome.objects.get(application_id=self.application.pk)
        adult1.first_name = 'Joe'
        adult1.middle_names = 'Anthony'
        adult1.last_name = 'Bloggs'
        adult1.dbs_certificate_number = '123456789012'
        adult1.capita = False
        adult1.enhanced_check = True
        adult1.on_update = True
        adult1.save()

        AdultInHome.objects.create(
            application_id=self.application,
            first_name='Freda', middle_names='Annabel', last_name='Smith',
            birth_day=1, birth_month=2, birth_year=1983,
            dbs_certificate_number='123456789013',
            capita=True,
            within_three_months=False,
            certificate_information='',
            enhanced_check=None,
            on_update=False,
        )

        AdultInHome.objects.create(
            application_id=self.application,
            first_name='Jim', middle_names='Bob', last_name='Robertson',
            birth_day=1, birth_month=3, birth_year=1985,
            dbs_certificate_number='123456789014',
            capita=True,
            within_three_months=True,
            certificate_information='',
            enhanced_check=None,
            on_update=None,
        )

        response = self.client.get(reverse('arc-summary'), data={'id': self.application.pk})

        utils.assertSummaryField(response, 'On the update service?', 'Yes', heading='Joe Anthony Bloggs')
        utils.assertSummaryField(response, 'On the update service?', 'No', heading='Freda Annabel Smith')
        utils.assertNotSummaryField(response, 'On the update service?', heading='Jim Bob Robertson')

    class MockDatetime(datetime.datetime):

        @classmethod
        def now(cls):
            return datetime.datetime(2019, 2, 27, 17, 30, 5)

    @patch('datetime.datetime', new=MockDatetime)
    def test_submit_summary_releases_application_as_accepted_in_database_if_no_tasks_flagged(self):

        APP_TASKS_ALL = ['login_details', 'personal_details', 'your_children', 'childcare_type', 'first_aid_training',
                         'childcare_training', 'criminal_record_check', 'health', 'references', 'people_in_home']
        ARC_TASKS_ALL = ['login_details', 'childcare_type', 'personal_details', 'your_children', 'first_aid',
                         'childcare_training', 'dbs', 'health', 'references', 'people_in_home']

        for task in APP_TASKS_ALL:
            setattr(self.application, '{}_status'.format(task), APP_STATUS_COMPLETED)
            setattr(self.application, '{}_arc_flagged'.format(task), False)

        self.application.declarations_status = APP_STATUS_COMPLETED
        self.application.declaration_confirmation = True
        self.application.application_status = APP_STATUS_REVIEW
        self.application.save()

        arc = Arc.objects.get(application_id=self.application.pk)

        for task in ARC_TASKS_ALL:
            setattr(arc, '{}_review'.format(task), ARC_STATUS_COMPLETED)

        arc.save()

        # id must be both GET and POST parameter
        self.client.post(reverse('arc-summary')+'?id='+self.application.pk, data={'id': self.application.pk})

        refetched_application = Application.objects.get(pk=self.application.pk)
        # in accepted status
        self.assertEqual(datetime.datetime(2019, 2, 27, 17, 30, 5, tzinfo=timezone.utc), refetched_application.date_accepted)
        self.assertEqual(APP_STATUS_ACCEPTED, refetched_application.application_status)
        # declaration unchanged
        self.assertEqual(APP_STATUS_COMPLETED, refetched_application.declarations_status)
        self.assertTrue(refetched_application.declaration_confirmation)

        # unassigned from arc user
        refetched_arc = Arc.objects.get(pk=arc.pk)
        self.assertTrue(refetched_arc.user_id in ('', None))

    @skip
    @patch('datetime.datetime', new=MockDatetime)
    def test_submit_summary_releases_application_as_needing_info_in_database_if_tasks_have_been_flagged(self):

        ARC_TASKS_FLAGGED = ['childcare_type', 'personal_details']
        ARC_TASKS_UNFLAGGED = ['login_details', 'your_children', 'first_aid', 'childcare_training', 'dbs', 'health',
                               'references', 'people_in_home']
        APP_TASKS_TO_BE_FLAGGED = ['personal_details', 'childcare_type']
        APP_TASKS_NOT_TO_BE_FLAGGED = ['login_details',  'your_children',  'first_aid_training', 'childcare_training',
                                       'criminal_record_check', 'health', 'references', 'people_in_home']
        APP_TASKS_ALL = APP_TASKS_TO_BE_FLAGGED + APP_TASKS_NOT_TO_BE_FLAGGED

        for task in APP_TASKS_ALL:
            setattr(self.application, '{}_status'.format(task), APP_STATUS_COMPLETED)
            setattr(self.application, '{}_arc_flagged'.format(task), False)

        self.application.declarations_status = APP_STATUS_COMPLETED
        self.application.declaration_confirmation = True
        self.application.application_status = APP_STATUS_REVIEW
        self.application.save()

        arc = Arc.objects.get(application_id=self.application.pk)

        for task in ARC_TASKS_UNFLAGGED:
            setattr(arc, '{}_review'.format(task), ARC_STATUS_COMPLETED)

        for task in ARC_TASKS_FLAGGED:
            setattr(arc, '{}_review'.format(task), ARC_STATUS_FLAGGED)

        arc.save()

        # id must be both GET and POST parameter
        self.client.post(reverse('arc-summary')+'?id='+self.application.pk, data={'id': self.application.pk})

        refetched_application = Application.objects.get(pk=self.application.pk)
        # not in accepted status
        self.assertIsNone(refetched_application.date_accepted)
        self.assertEqual(APP_STATUS_FURTHER_INFO, refetched_application.application_status)
        # declaration has been reset
        self.assertEqual(APP_STATUS_NOT_STARTED, refetched_application.declarations_status)
        self.assertFalse(refetched_application.declaration_confirmation)

        # flagged tasks recorded in application
        for task in APP_TASKS_NOT_TO_BE_FLAGGED:
            self.assertEqual(APP_STATUS_COMPLETED, getattr(refetched_application, '{}_status'.format(task)))
        for task in APP_TASKS_TO_BE_FLAGGED:
            self.assertEqual(APP_STATUS_FLAGGED, getattr(refetched_application, '{}_status'.format(task)))

        # unassigned from arc user
        refetched_arc = Arc.objects.get(pk=arc.pk)
        self.assertTrue(refetched_arc.user_id in ('', None))

        # flagged tasks still recorded in arc record
        for task in ARC_TASKS_FLAGGED:
            self.assertEqual(ARC_STATUS_FLAGGED, getattr(refetched_arc, '{}_review'.format(task)))
        for task in ARC_TASKS_UNFLAGGED:
            self.assertEqual(ARC_STATUS_COMPLETED, getattr(refetched_arc, '{}_review'.format(task)))
