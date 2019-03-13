import logging
from datetime import datetime, timezone, date
from unittest.mock import patch

from django.test import TestCase, tag
from django.urls import reverse

from ... import models
from ...tests import utils
from ...tests.utils import create_childminder_application, create_arc_user

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

    def test_shows_previous_names(self):

        models.PreviousName.objects.create(
            person_id=self.application.pk,
            other_person_type='APPLICANT',
            first_name='The', middle_names='Lone', last_name='Ranger',
            start_day=5, start_month=4, start_year=1999,
            end_day=10, end_month=12, end_year=2001,
        )
        models.PreviousName.objects.create(
            person_id=self.application.pk,
            other_person_type='APPLICANT',
            first_name='Billy', middle_names='Bob', last_name='Billington-Bobbington',
            start_day=25, start_month=12, start_year=1988,
            end_day=13, end_month=8, end_year=1999,
        )

        response = self.client.get(reverse('personal_details_summary'), data={'id': self.application.pk})

        self.assertEqual(200, response.status_code)

        utils.assertSummaryField(response, 'Your previous name 1', 'The Lone Ranger', heading="Previous names")
        utils.assertSummaryField(response, 'Start date 1', '5 April 1999', heading="Previous names")
        utils.assertSummaryField(response, 'End date 1', '10 December 2001', heading="Previous names")
        utils.assertSummaryField(response, 'Your previous name 2', 'Billy Bob Billington-Bobbington',
                                 heading="Previous names")
        utils.assertSummaryField(response, 'Start date 2', '25 December 1988', heading="Previous names")
        utils.assertSummaryField(response, 'End date 2', '13 August 1999', heading="Previous names")

    def test_shows_Add_Previous_Names_button(self):

        # GET request to personal details summary
        response = self.client.get(reverse('personal_details_summary') + '?id=' + self.application.application_id)

        # Assert that the 'Add previous names' button is on the page.
        utils.assertXPath(response, '//a[@href="{url}?id={app_id}&person_id={app_id}&type=APPLICANT"]'.format(
            url=reverse('personal_details_previous_names'), app_id=self.application.pk))

    def test_shows_previous_addresses(self):
        self.skipTest('testNotImplemented')

    def test_show_Add_Previous_Addresses_button(self):
        self.skipTest('testNotImplemented')

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
        reloaded_arc_record = models.Arc.objects.get(pk=self.application.application_id)
        self.assertEqual(reloaded_arc_record.personal_details_review, ARC_STATUS_FLAGGED)

        # 3. Check that comment has been correctly appended to application
        try:
            arc_comments = models.ArcComments.objects.get(
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
        reloaded_application = models.Application.objects.get(pk=self.application.application_id)
        self.assertTrue(reloaded_application.personal_details_arc_flagged)

    class MockDate(date):
        @classmethod
        def today(cls):
            return date(2019, 2, 24)

    @patch('datetime.date', new=MockDate)
    def test_submit_stores_current_name_end_date_as_today_and_start_date_as_latest_previous_name_end_date(self):

        models.PreviousName.objects.create(
            person_id=self.application.pk,
            other_person_type='APPLICANT',
            first_name='Jack', middle_names='O', last_name='Spades',
            start_day=14, start_month=2, start_year=2016,
            end_day=23, end_month=6, end_year=2017,
        )
        models.PreviousName.objects.create(
            person_id=self.application.pk,
            other_person_type='APPLICANT',
            first_name='Ace', middle_names='', last_name="O'Hearts",
            start_day=16, start_month=1, start_year=2015,
            end_day=12, end_month=4, end_year=2016,
        )

        url = reverse('personal_details_summary') + '?id=' + self.application.application_id
        data = {'id': self.application.application_id}

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)

        fetched_details = models.ApplicantName.objects.get(application_id=self.application.pk)
        self.assertEqual(23, fetched_details.start_day)
        self.assertEqual(6, fetched_details.start_month)
        self.assertEqual(2017, fetched_details.start_year)
        self.assertEqual(24, fetched_details.end_day)
        self.assertEqual(2, fetched_details.end_month)
        self.assertEqual(2019, fetched_details.end_year)

    @patch('datetime.date', new=MockDate)
    def test_submit_stores_current_name_end_date_as_today_and_start_date_as_dob_if_no_previous_names(self):

        details = models.ApplicantPersonalDetails.objects.get(application_id=self.application.pk)
        details.birth_day = 20
        details.birth_month = 8
        details.birth_month = 1979
        details.save()

        url = reverse('personal_details_summary') + '?id=' + self.application.application_id
        data = {'id': self.application.application_id}

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)

        fetched_details = models.ApplicantName.objects.get(application_id=self.application.pk)
        self.assertEqual(20, fetched_details.start_day)
        self.assertEqual(8, fetched_details.start_month)
        self.assertEqual(1979, fetched_details.start_year)
        self.assertEqual(24, fetched_details.end_day)
        self.assertEqual(2, fetched_details.end_month)
        self.assertEqual(2019, fetched_details.end_year)

    def test_submit_redirects_to_first_aid_page_if_valid(self):

        url = reverse('personal_details_summary') + '?id=' + self.application.application_id
        data = {'id': self.application.application_id}

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)
        utils.assertRedirectView(response, 'first_aid_training_summary')


@tag('http')
class ApplicantPreviousNamesFunctionalTests(TestCase):

    def setUp(self):
        self.arc_user = create_arc_user()
        self.application = create_childminder_application(self.arc_user.pk)
        self.client.login(username='arc_test', password='my_secret')
        self.valid_previous_name_data = [
            {
                'form-0-previous_name_id': '888888884444AAAA4444121212121212',
                'initial-form-0-previous_name_id': '888888884444AAAA4444121212121212',
                'form-0-person_id': self.application.pk,
                'form-0-other_person_type': 'APPLICANT',
                'form-0-first_name': 'David',
                'form-0-middle_names': 'Anty',
                'form-0-last_name': 'Goliath',
                'form-0-start_date_0': '10',  # Day
                'form-0-start_date_1': '03',  # Month
                'form-0-start_date_2': '1996',  # Year
                'form-0-end_date_0': '15',  # Day
                'form-0-end_date_1': '08',  # Month
                'form-0-end_date_2': '1996',  # Year
            },
            {
                'form-1-previous_name_id': 'BBBBBBBB4444AAAA4444121212121212',
                'initial-form-1-previous_name_id': 'BBBBBBBB4444AAAA4444121212121212',
                'form-1-person_id': self.application.pk,
                'form-1-other_person_type': 'APPLICANT',
                'form-1-first_name': 'James',
                'form-1-middle_names': 'Rather-Large',
                'form-1-last_name': 'Peach',
                'form-1-start_date_0': '12',  # Day
                'form-1-start_date_1': '08',  # Month
                'form-1-start_date_2': '1996',  # Year
                'form-1-end_date_0': '4',  # Day
                'form-1-end_date_1': '12',  # Month
                'form-1-end_date_2': '2002',  # Year
            }
        ]

    def test_can_render_page(self):

        application_id = self.application.application_id
        url = '{0}?id={1}&person_id={1}&type=APPLICANT'.format(
            reverse('personal_details_previous_names'), application_id)

        response = self.client.get(url)

        self.assertEqual(200, response.status_code)
        utils.assertView(response, 'add_applicant_previous_name')

    def test_shows_fields_for_existing_stored_names(self):

        application_id = self.application.application_id

        models.PreviousName.objects.create(
            person_id=application_id,
            other_person_type='APPLICANT',
            first_name='Clark', middle_names='S', last_name='Kent',
            start_day=1, start_month=1, start_year=2018,
            end_day=1, end_month=1, end_year=2019
        )
        models.PreviousName.objects.create(
            person_id=application_id,
            other_person_type='APPLICANT',
            first_name='Super', middle_names='', last_name='Man',
            start_day=2, start_month=2, start_year=2015,
            end_day=1, end_month=1, end_year=2017
        )

        url = '{0}?id={1}&person_id={1}&type=APPLICANT'.format(
            reverse('personal_details_previous_names'), application_id)

        response = self.client.get(url)

        self.assertEqual(200, response.status_code)

        for names in [
            ('Clark', 'S', 'Kent', '1', '1', '2018', '1', '1', '2019'),
            ('Super', '', 'Man', '2', '2', '2015', '1', '1', '2017')]:
            for field, name in [('first_name', names[0]), ('middle_names', names[1]), ('last_name', names[2]),
                                ('start_date_0', names[3]), ('start_date_1', names[4]), ('start_date_2', names[5]),
                                ('end_date_0', names[6]), ('end_date_1', names[7]), ('end_date_2', names[8])]:
                utils.assertXPath(
                    response,
                    ('//input[normalize-space(@type)="text" and contains(normalize-space(@name), "{field}") '
                     'and normalize-space(@value)="{name}"]').format(field=field, name=name)
                )

    def test_submit_confirm_returns_to_page_with_error_if_any_not_valid(self):

        application_id = self.application.application_id

        data = self._make_post_data(2, 'Confirm and continue')
        data.update(self.valid_previous_name_data[0])
        data.update(self.valid_previous_name_data[1])

        # make second one invalid
        data['form-1-start_date_0'] = 32

        url = '{0}?id={1}&person_id={1}&type=APPLICANT'.format(
            reverse('personal_details_previous_names'), application_id)

        response = self.client.post(url, data)

        self.assertEqual(200, response.status_code)
        utils.assertView(response, 'add_applicant_previous_name')
        utils.assertXPath(response, '//*[normalize-space(@class)="field-error"]')

    def test_submit_confirm_redirects_to_personal_details_summary_if_all_valid(self):

        application_id = self.application.application_id
        data = self._make_post_data(2, 'Confirm and continue')
        data.update(self.valid_previous_name_data[0])
        data.update(self.valid_previous_name_data[1])

        url = '{0}?id={1}&person_id={1}&type=APPLICANT'.format(reverse('personal_details_previous_names'),
                                                               application_id)
        response = self.client.post(url, data)

        # Assert response redirected to personal_details_summary
        self.assertEqual(302, response.status_code)
        utils.assertRedirectView(response, 'personal_details_summary')

    def test_submit_confirm_stores_info_in_db_if_all_valid(self):

        application_id = self.application.application_id

        data = self._make_post_data(2, 'Confirm and continue')
        data.update(self.valid_previous_name_data[0])

        url = '{0}?id={1}&person_id={1}&type=APPLICANT'.format(reverse('personal_details_previous_names'),
                                                               application_id)
        response = self.client.post(url, data)

        self.assertEqual(302, response.status_code)

        # Assert application was updated
        if not models.PreviousName.objects.filter(person_id=application_id).exists():
            raise AssertionError('No previous name record was found')

        previous_name_record = models.PreviousName.objects.get(person_id=application_id)

        self.assertEqual(previous_name_record.other_person_type, data['form-0-other_person_type'])
        self.assertEqual(previous_name_record.first_name, data['form-0-first_name'])
        self.assertEqual(previous_name_record.middle_names, data['form-0-middle_names'])
        self.assertEqual(previous_name_record.last_name, data['form-0-last_name'])
        self.assertEqual(previous_name_record.start_day, int(data['form-0-start_date_0']))
        self.assertEqual(previous_name_record.start_month, int(data['form-0-start_date_1']))
        self.assertEqual(previous_name_record.start_year, int(data['form-0-start_date_2']))
        self.assertEqual(previous_name_record.end_day, int(data['form-0-end_date_0']))
        self.assertEqual(previous_name_record.end_month, int(data['form-0-end_date_1']))
        self.assertEqual(previous_name_record.end_year, int(data['form-0-end_date_2']))

    def test_submit_add_returns_to_page_with_second_name_fields(self):

        application_id = self.application.application_id

        # Send a post request with an 'action':'Add another name'.
        data = self._make_post_data(1, 'Add another name')
        data.update(self.valid_previous_name_data[0])

        url = '{0}?id={1}&person_id={1}&type=APPLICANT'.format(
            reverse('personal_details_previous_names'), application_id)
        response = self.client.post(url, data)

        # Assert that the page returned was the same page.
        self.assertEqual(302, response.status_code)
        utils.assertRedirectView(response, 'add_applicant_previous_name')

        # exactly one of each
        for field, value in [('first_name', ''), ('first_name', 'David'),
                             ('middle_names', ''), ('middle_names', 'Anty'),
                             ('last_name', ''), ('last_name', 'Goliath'),
                             ('start_date_0', ''), ('start_date_0', '10'),
                             ('start_date_1', ''), ('start_date_1', '3'),
                             ('start_date_2', ''), ('start_date_2', '1996'),
                             ('end_date_0', ''), ('end_date_0', '15'),
                             ('end_date_1', ''), ('end_date_1', '8'),
                             ('end_date_2', ''), ('end_date_2', '1996')]:
            utils.assertXPathCount(
                response,
                ('//input[normalize-space(@type)="text" and normalize-space(@value)="{value}" '
                 'and contains(normalize-space(@name), "{field}")]').format(field=field, value=value),
                1
            )

    def test_submit_add_saves_original_name_to_database(self):
        application_id = self.application.application_id

        # Send a post request with an 'action':'Add another name'.
        data = self._make_post_data(1, 'Add another name')
        data.update(self.valid_previous_name_data[0])

        url = '{0}?id={1}&person_id={1}&type=APPLICANT'.format(
            reverse('personal_details_previous_names'), application_id)
        response = self.client.post(url, data)

        # Assert that the page returned was the same page.
        self.assertEqual(302, response.status_code)
        utils.assertRedirectView(response, 'add_applicant_previous_name')

        # Get Applicant's previous name data
        previous_names = models.PreviousName.objects.filter(
            person_id=application_id,
            other_person_type='APPLICANT')

        # Assert only one PreviousName was returned
        self.assertEqual(len(list(previous_names)), 1)

        # Assert that returned PreviousName is equal to the submitted data
        prev_name = previous_names[1]

        posted_start_date = date(int(data['start_date_2']), int(data['start_date_1']), int(data['start_date_0']))
        posted_end_date = date(int(data['start_date_2']), int(data['start_date_1']), int(data['start_date_0']))

        self.assertEqual(data['first_name'], prev_name['first_name'])
        self.assertEqual(data['middle_names'], prev_name['middle_names'])
        self.assertEqual(data['last_name'], prev_name['last_name'])
        self.assertEqual(posted_start_date, prev_name['start_date'])
        self.assertEqual(posted_end_date, prev_name['end_date'])

    def test_submit_remove_returns_to_page_with_name_fields_removed(self):

        application_id = self.application.application_id

        data = self._make_post_data(2, 'delete')
        data.update(self.valid_previous_name_data[0])
        data.update(self.valid_previous_name_data[1])
        data[data['form-0-previous_name_id']] = 'Remove this name'

        # Make a post request to the previous names page
        url = '{0}?id={1}&person_id={1}&type=APPLICANT'.format(reverse('personal_details_previous_names'),
                                                               application_id)
        response = self.client.post(url, data)

        # Assert that the page returned was the same page.
        self.assertEqual(302, response.status_code)
        utils.assertRedirectView(response, 'add_applicant_previous_name')

        # exactly one of each
        for field, value in [('first_name', 'James'),
                             ('middle_names', 'Rather-Large'),
                             ('last_name', 'Peach'),
                             ('start_date_0', '12'),
                             ('start_date_1', '8'),
                             ('start_date_2', '1996'),
                             ('end_date_0', '4'),
                             ('end_date_1', '12'),
                             ('end_date_2', '2002')]:
            utils.assertXPathCount(
                response,
                ('//input[normalize-space(@type)="text" and normalize-space(@value)="{value}" '
                 'and contains(normalize-space(@name), "{field}")]').format(field=field, value=value),
                1
            )

    def test_submit_remove_deletes_removed_name_from_database(self):

        application_id = self.application.application_id

        # create existing database records which match the posted data
        models.PreviousName.objects.create(
            previous_name_id=self.valid_previous_name_data[0]['form-0-previous_name_id'],
            person_id=application_id,
            other_person_type='APPLICANT',
            first_name=self.valid_previous_name_data[0]['form-0-first_name'],
            middle_names=self.valid_previous_name_data[0]['form-0-middle_names'],
            last_name=self.valid_previous_name_data[0]['form-0-last_name'],
            start_day=int(self.valid_previous_name_data[0]['form-0-start_date_0']),
            start_month=int(self.valid_previous_name_data[0]['form-0-start_date_1']),
            start_year=int(self.valid_previous_name_data[0]['form-0-start_date_2']),
            end_day=int(self.valid_previous_name_data[0]['form-0-end_date_0']),
            end_month=int(self.valid_previous_name_data[0]['form-0-end_date_1']),
            end_year=int(self.valid_previous_name_data[0]['form-0-end_date_2']),
        )
        models.PreviousName.objects.create(
            previous_name_id=self.valid_previous_name_data[1]['form-1-previous_name_id'],
            person_id=application_id,
            other_person_type='APPLICANT',
            first_name=self.valid_previous_name_data[1]['form-1-first_name'],
            middle_names=self.valid_previous_name_data[1]['form-1-middle_names'],
            last_name=self.valid_previous_name_data[1]['form-1-last_name'],
            start_day=int(self.valid_previous_name_data[1]['form-1-start_date_0']),
            start_month=int(self.valid_previous_name_data[1]['form-1-start_date_1']),
            start_year=int(self.valid_previous_name_data[1]['form-1-start_date_2']),
            end_day=int(self.valid_previous_name_data[1]['form-1-end_date_0']),
            end_month=int(self.valid_previous_name_data[1]['form-1-end_date_1']),
            end_year=int(self.valid_previous_name_data[1]['form-1-end_date_2']),
        )

        data = self._make_post_data(2, 'delete')
        data.update(self.valid_previous_name_data[0])
        data.update(self.valid_previous_name_data[1])
        data[data['form-0-previous_name_id']] = 'Remove this name'

        # Make a post request to the previous names page
        url = '{0}?id={1}&person_id={1}&type=APPLICANT'.format(reverse('personal_details_previous_names'),
                                                               application_id)
        response = self.client.post(url, data)

        self.assertEqual(302, response.status_code)

        fetched_names = models.PreviousName.objects.filter(
            person_id=application_id,
            other_person_type='APPLICANT')

        # assert only one name remaining now
        self.assertEqual(1, len(list(fetched_names)))
        self.assertEqual('James', fetched_names[0].first_name)
        self.assertEqual('Rather-Large', fetched_names[0].middle_names)
        self.assertEqual('Peach', fetched_names[0].last_name)
        self.assertEqual(12, fetched_names[0].start_day)
        self.assertEqual(8, fetched_names[0].start_month)
        self.assertEqual(96, fetched_names[0].start_year)
        self.assertEqual(4, fetched_names[0].end_day)
        self.assertEqual(12, fetched_names[0].end_month)
        self.assertEqual(2, fetched_names[0].end_year)

    def _make_post_data(self, num_forms, action):
        return {
            'id': self.application.pk,
            'person_id': self.application.pk,
            'type': 'APPLICANT',
            'extra': 1,
            'action': action,
            'form-TOTAL_FORMS': num_forms,
            'form-INITIAL_FORMS': 0,
            'form-MIN_NUM_FORMS': 0,
            'form-MAX_NUM_FORMS': 1000,
        }


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
        reloaded_arc_record = models.Arc.objects.get(pk=self.application.application_id)
        self.assertEqual(reloaded_arc_record.first_aid_review, ARC_STATUS_FLAGGED)

        # 3. Check that comment has been correctly appended to application
        try:
            arc_comments = models.ArcComments.objects.get(
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
        reloaded_application = models.Application.objects.get(pk=self.application.application_id)
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
        reloaded_arc_record = models.Arc.objects.get(pk=self.application.application_id)
        self.assertEqual(reloaded_arc_record.dbs_review, ARC_STATUS_FLAGGED)

        # 3. Check that comment has been correctly appended to application
        try:
            arc_comments = models.ArcComments.objects.get(
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
        reloaded_application = models.Application.objects.get(pk=self.application.application_id)
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

        adult = models.AdultInHome.objects.get(application_id=self.application.pk)
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

        adult = models.AdultInHome.objects.get(application_id=self.application.pk)
        adult.military_base = True
        adult.save()

        care_type = models.ChildcareType.objects.get(application_id=self.application.pk)
        care_type.zero_to_five = True
        care_type.save()

        response = self.client.get(reverse('other_people_summary'), data={'id': self.application.pk})

        utils.assertSummaryField(response, 'Lived or worked on British military base in the last 5 years?', 'Yes')

    def test_doesnt_display_adult_military_base_field_if_not_caring_for_zero_to_five_year_olds(self):
        self.application.adults_in_home = True
        self.application.working_in_other_childminder_home = False
        self.application.save()

        care_type = models.ChildcareType.objects.get(application_id=self.application.pk)
        care_type.zero_to_five = False
        care_type.save()

        response = self.client.get(reverse('other_people_summary'), data={'id': self.application.pk})

        utils.assertNotSummaryField(response, 'Lived or worked on British military base in the last 5 years?')

    def test_displays_adult_dbs_recent_field_only_for_adults_on_capita_list(self):
        self.application.adults_in_home = True
        self.application.working_in_other_childminder_home = False
        self.application.save()

        adult1 = models.AdultInHome.objects.get(application_id=self.application.pk)
        adult1.first_name = 'Joe'
        adult1.middle_names = 'Anthony'
        adult1.last_name = 'Bloggs'
        adult1.dbs_certificate_number = '123456789012'
        adult1.capita = False
        adult1.save()

        models.AdultInHome.objects.create(
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

        adult1 = models.AdultInHome.objects.get(application_id=self.application.pk)
        adult1.first_name = 'Joe'
        adult1.middle_names = 'Anthony'
        adult1.last_name = 'Bloggs'
        adult1.dbs_certificate_number = '123456789012'
        adult1.capita = False
        adult1.enhanced_check = True
        adult1.on_update = True
        adult1.save()

        models.AdultInHome.objects.create(
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

        adult1 = models.AdultInHome.objects.get(application_id=self.application.pk)
        adult1.first_name = 'Joe'
        adult1.middle_names = 'Anthony'
        adult1.last_name = 'Bloggs'
        adult1.dbs_certificate_number = '123456789012'
        adult1.capita = False
        adult1.enhanced_check = True
        adult1.on_update = True
        adult1.save()

        models.AdultInHome.objects.create(
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

        models.AdultInHome.objects.create(
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

    def test_shows_previous_names_for_each_adult(self):

        self.application.adults_in_home = True
        self.application.save()

        adult1 = models.AdultInHome.objects.get(application_id=self.application.pk)
        adult1.first_name = 'John'
        adult1.middle_names = 'Jimbo'
        adult1.last_name = 'Johnnington'
        adult1.save()
        models.PreviousName.objects.create(
            person_id=adult1.pk,
            other_person_type='ADULT',
            first_name='Bilbo', middle_names='B', last_name='Baggins',
            start_day=1, start_month=3, start_year=1985,
            end_day=10, end_month=12, end_year=2001,
        )
        models.PreviousName.objects.create(
            person_id=adult1.pk,
            other_person_type='ADULT',
            first_name='George', middle_names='', last_name='Lucas',
            start_day=9, start_month=10, start_year=2011,
            end_day=1, end_month=1, end_year=2012,
        )

        adult2 = models.AdultInHome.objects.create(
            application_id=self.application,
            first_name='Freda', middle_names='Annabel', last_name='Smith',
            birth_day=1, birth_month=2, birth_year=1983,
        )
        models.PreviousName.objects.create(
            person_id=adult2.pk,
            other_person_type='ADULT',
            first_name='Gertrude', middle_names='Geraldine', last_name='Gorton',
            start_day=1, start_month=8, start_year=1972,
            end_day=2, end_month=8, end_year=1972,
        )

        response = self.client.get(reverse('other_people_summary'), data={'id': self.application.pk})
        self.assertEqual(200, response.status_code)

        head1 = "John Jimbo Johnnington's eBulk details"
        utils.assertSummaryField(response, 'Previous name 1', 'Bilbo B Baggins', heading=head1)
        utils.assertSummaryField(response, 'Start date 1', '1 March 1985', heading=head1)
        utils.assertSummaryField(response, 'End date 1', '10 December 2001', heading=head1)
        utils.assertSummaryField(response, 'Previous name 2', 'George Lucas', heading=head1)
        utils.assertSummaryField(response, 'Start date 2', '9 October 2011', heading=head1)
        utils.assertSummaryField(response, 'End date 2', '1 January 2012', heading=head1)

        head2 = "Freda Annabel Smith's eBulk details"
        utils.assertSummaryField(response, 'Previous name 1', 'Gertrude Geraldine Gorton', heading=head1)
        utils.assertSummaryField(response, 'Start date 1', '1 August 1972', heading=head2)
        utils.assertSummaryField(response, 'End date 1', '2 August 1972', heading=head2)

    def test_shows_Add_Previous_Names_button_for_each_adult(self):

        self.application.adults_in_home = True
        self.application.save()

        adult1 = models.AdultInHome.objects.get(application_id=self.application.pk)

        adult2 = models.AdultInHome.objects.create(
            application_id=self.application,
            first_name='Freda', middle_names='Annabel', last_name='Smith',
            birth_day=1, birth_month=2, birth_year=1983,
        )

        response = self.client.get(reverse('other_people_summary'), data={'id': self.application.pk})

        for adult_id in (adult1.pk, adult2.pk):
            utils.assertXPath(
                response,
                '//a[@href="{url}?id={app_id}&person_id={adult_id}&type=ADULT"]'.format(
                    url=reverse('other-people-previous-names'), app_id=self.application.pk, adult_id=adult_id)
            )

    def test_shows_previous_addresses_for_each_adult(self):
        self.skipTest('testNotImplemented')

    def test_shows_Add_Previous_Addresses_button_for_each_adult(self):

        self.application.adults_in_home = True
        self.application.save()

        adult1 = models.AdultInHome.objects.get(application_id=self.application.pk)

        adult2 = models.AdultInHome.objects.create(
            application_id=self.application,
            first_name='Freda', middle_names='Annabel', last_name='Smith',
            birth_day=1, birth_month=2, birth_year=1983,
        )

        response = self.client.get(reverse('other_people_summary'), data={'id': self.application.pk})

        for adult_id in (adult1.pk, adult2.pk):
            utils.assertXPath(
                response,
                '//a[@href="{url}?id={app_id}&state=entry&person_id={adult_id}&person_type=ADULT"]'.format(
                    url=reverse('other-people-previous-addresses'), app_id=self.application.pk, adult_id=adult_id)
            )

    def test_submitting_comment_on_field_adds_flag_in_database(self):
        data = self._make_post_data(adults=1)

        data.update({
            'static-adults_in_home_declare': 'on',
            'static-adults_in_home_comments': 'There was a test issue with this field',
            'adult-0-cygnum_relationship': 'Brother',
        })

        response = self.client.post(reverse('other_people_summary'), data)

        self.assertEqual(response.status_code, 302)

        # Ensure overall task status marked as FLAGGED in ARC record
        reloaded_arc_record = models.Arc.objects.get(pk=self.application.application_id)
        self.assertEqual(reloaded_arc_record.people_in_home_review, ARC_STATUS_FLAGGED)

        # Check that comment has been correctly appended to application
        arc_comments = models.ArcComments.objects.get(
            table_pk='da2265c2-2d65-4214-bfef-abcfe59b75aa',
            table_name='APPLICATION',
            field_name='adults_in_home',
            comment='There was a test issue with this field',
            flagged=True,
        )
        self.assertIsNotNone(arc_comments)

        # Check flagged boolean indicator is set on the application record
        reloaded_application = models.Application.objects.get(pk=self.application.application_id)
        self.assertTrue(reloaded_application.people_in_home_arc_flagged)

    def test_submit_returns_to_page_with_error_if_not_valid(self):

        data = self._make_post_data(adults=1)

        data.update({
            'static-adults_in_home_declare': 'on',
            'static-adults_in_home_comments': '',  # comments left blank
            'adult-0-cygnum_relationship': 'Brother',
        })

        response = self.client.post(reverse('other_people_summary'), data)

        self.assertEqual(200, response.status_code)
        utils.assertView(response, 'other_people_summary')
        utils.assertXPath(response, '//*[normalize-space(@class)="field-error"]')

    class MockDate(date):
        @classmethod
        def today(cls):
            return date(2019, 3, 2)

    @patch('datetime.date', new=MockDate)
    def test_submit_stores_each_adult_name_end_date_as_today_and_start_date_as_latest_previous_name_end_date(self):

        adult1 = models.AdultInHome.objects.get(application_id=self.application.pk)
        adult1.last_name = 'Anderson'
        adult1.save()
        models.PreviousName.objects.create(
            person_id=adult1.pk,
            other_person_type='ADULT',
            first_name='Bob', middle_names='B', last_name='Bobobob',
            start_day=4, start_month=5, start_year=1964,
            end_day=10, end_month=10, end_year=1992,
        )
        models.PreviousName.objects.create(
            person_id=adult1.pk,
            other_person_type='ADULT',
            first_name='Rob', middle_names='R', last_name='Rororob',
            start_day=9, start_month=8, start_year=1972,
            end_day=12, end_month=6, end_year=2001,
        )

        adult2 = models.AdultInHome.objects.create(
            application_id=self.application,
            first_name='Jim', middle_names='Jimmy', last_name='Jimson',
            birth_day=23, birth_month=9, birth_year=1982,
        )
        models.PreviousName.objects.create(
            person_id=adult2.pk,
            other_person_type='ADULT',
            first_name='Jon', middle_names='J', last_name='Jononon',
            start_day=15, start_month=9, start_year=1989,
            end_day=16, end_month=9, end_year=1989,
        )

        data = self._make_post_data(adults=2)
        data.update({
            'adult-0-cygnum_relationship': 'Brother',
            'adult-1-cygnum_relationship': 'Brother',
        })

        response = self.client.post(reverse('other_people_summary'), data)

        self.assertEqual(302, response.status_code)

        fetched_adults = models.AdultInHome.objects.filter(application_id=self.application.pk).order_by('last_name')

        fetched0 = fetched_adults[0]
        self.assertEqual(12, fetched0.name_start_day)
        self.assertEqual(6, fetched0.name_start_month)
        self.assertEqual(2001, fetched0.name_start_year)
        self.assertEqual(2, fetched0.name_end_day)
        self.assertEqual(3, fetched0.name_end_month)
        self.assertEqual(2019, fetched0.name_end_year)

        fetched1 = fetched_adults[1]
        self.assertEqual(16, fetched1.name_start_day)
        self.assertEqual(9, fetched1.name_start_month)
        self.assertEqual(1989, fetched1.name_start_year)
        self.assertEqual(2, fetched1.name_end_day)
        self.assertEqual(3, fetched1.name_end_month)
        self.assertEqual(2019, fetched1.name_end_year)

    @patch('datetime.date', new=MockDate)
    def test_submit_stores_each_adult_name_end_date_as_today_and_start_date_as_dob_if_no_previous_names(self):

        adult1 = models.AdultInHome.objects.get(application_id=self.application.pk)
        adult1.birth_day = 5
        adult1.birth_month = 11
        adult1.birth_year = 1977
        adult1.save()

        data = self._make_post_data(adults=1)
        data.update({
            'adult-0-cygnum_relationship': 'Brother',
        })

        response = self.client.post(reverse('other_people_summary'), data)

        self.assertEqual(302, response.status_code)

        fetched = models.AdultInHome.objects.get(application_id=self.application.pk)

        self.assertEqual(5, fetched.name_start_day)
        self.assertEqual(11, fetched.name_start_month)
        self.assertEqual(1977, fetched.name_start_year)
        self.assertEqual(2, fetched.name_end_day)
        self.assertEqual(3, fetched.name_end_month)
        self.assertEqual(2019, fetched.name_end_year)

    def test_submit_redirects_to_references_page_if_valid(self):

        data = self._make_post_data(adults=1)

        data.update({
            'static-adults_in_home_declare': 'on',
            'static-adults_in_home_comments': 'There was a test issue with this field',
            'adult-0-cygnum_relationship': 'Brother',
        })

        response = self.client.post(reverse('other_people_summary'), data)

        self.assertEqual(302, response.status_code)
        utils.assertRedirectView(response, 'references_summary')
        self.assertTrue(response.url.endswith('?id=' + self.application.application_id))

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
class AdultPreviousNamesFunctionalTests(TestCase):

    def setUp(self):
        self.arc_user = create_arc_user()
        self.application = create_childminder_application(self.arc_user.pk)
        self.adult = models.AdultInHome.objects.get(application_id=self.application.pk)
        self.client.login(username='arc_test', password='my_secret')
        self.valid_names_post_data = [
            {
                'form-0-previous_name_id': '888888884444AAAA4444121212121212',
                'initial-form-0-previous_name_id': '888888884444AAAA4444121212121212',
                'form-0-person_id': self.adult.pk,
                'form-0-other_person_type': 'ADULT',
                'form-0-first_name': 'Joe',
                'form-0-middle_names': 'P',
                'form-0-last_name': 'Smith',
                'form-0-start_date_0': 1,
                'form-0-start_date_1': 10,
                'form-0-start_date_2': 2010,
                'form-0-end_date_0': 15,
                'form-0-end_date_1': 9,
                'form-0-end_date_2': 2016,
            },
            {
                'form-1-previous_name_id': 'BBBBBBBB4444AAAA4444121212121212',
                'initial-form-1-previous_name_id': 'BBBBBBBB4444AAAA4444121212121212',
                'form-1-person_id': self.adult.pk,
                'form-1-other_person_type': 'ADULT',
                'form-1-first_name': 'Bill',
                'form-1-middle_names': 'N',
                'form-1-last_name': 'Ted',
                'form-1-start_date_0': 15,
                'form-1-start_date_1': 2,
                'form-1-start_date_2': 2009,
                'form-1-end_date_0': 23,
                'form-1-end_date_1': 12,
                'form-1-end_date_2': 2017,
            }
        ]

    def test_can_render_page(self):

        url = reverse('other-people-previous-names') \
              + '?id={}&person_id={}&type={}'.format(self.application.pk, self.adult.pk, 'ADULT')

        response = self.client.get(url)

        self.assertEqual(200, response.status_code)
        utils.assertView(response, 'add_previous_name')

    def test_shows_fields_for_existing_stored_names(self):

        models.PreviousName.objects.create(
            person_id=self.adult.pk,
            other_person_type='ADULT',
            first_name='Fresh', middle_names='Prince', last_name='Belair',
            start_day=1, start_month=10, start_year=1999,
            end_day=10, end_month=11, end_year=2007,
        )
        models.PreviousName.objects.create(
            person_id=self.adult.pk,
            other_person_type='ADULT',
            first_name='Will', middle_names='', last_name='Smith',
            start_day=9, start_month=4, start_year=2015,
            end_day=3, end_month=12, end_year=2016,
        )

        url = reverse('other-people-previous-names') \
              + '?id={}&person_id={}&type={}'.format(self.application.pk, self.adult.pk, 'ADULT')

        response = self.client.get(url)

        self.assertEqual(200, response.status_code)

        for field, value in [('first_name', 'Fresh'), ('first_name', 'Will'),
                             ('middle_names', 'Prince'), ('middle_names', ''),
                             ('last_name', 'Belair'), ('last_name', 'Smith'),
                             ('start_date_0', '1'), ('start_date_0', '9'),
                             ('start_date_1', '10'), ('start_date_1', '4'),
                             ('start_date_2', '1999'), ('start_date_2', '2015'),
                             ('end_date_0', '10'), ('end_date_0', '3'),
                             ('end_date_1', '11'), ('end_date_1', '12'),
                             ('end_date_2', '2007'), ('end_date_2', '2016')]:
            utils.assertXPath(
                response,
                ('//input[normalize-space(@type)="text" and contains(normalize-space(@name), "{field}") '
                 'and normalize-space(@value)="{value}"]').format(field=field, value=value)
            )

    def test_submit_confirm_returns_to_page_with_error_if_any_not_valid(self):

        url = reverse('other-people-previous-names') \
            + '?id={}&person_id={}&type={}'.format(self.application.pk, self.adult.pk, 'ADULT')

        data = self._make_post_data(2, 'Confirm and continue')
        data.update(self.valid_names_post_data[0])
        data.update(self.valid_names_post_data[1])

        # make first of the submitted names invalid
        data['form-0-last_name'] = ''

        response = self.client.post(url, data)

        self.assertEqual(200, response.status_code)
        utils.assertView(response, 'add_previous_name')
        utils.assertXPath(response, '//*[normalize-space(@class)="field-error"]')

    def test_submit_confirm_redirects_to_people_in_home_summary_if_all_valid(self):

        url = reverse('other-people-previous-names') \
            + '?id={}&person_id={}&type={}'.format(self.application.pk, self.adult.pk, 'ADULT')

        data = self._make_post_data(2, 'Confirm and continue')
        data.update(self.valid_names_post_data[0])
        data.update(self.valid_names_post_data[1])

        response = self.client.post(url, data)

        self.assertEqual(302, response.status_code)
        utils.assertRedirectView(response, 'other_people_summary')

    def test_submit_confirm_stores_info_in_db_if_all_valid(self):

        url = reverse('other-people-previous-names') \
            + '?id={}&person_id={}&type={}'.format(self.application.pk, self.adult.pk, 'ADULT')

        data = self._make_post_data(2, 'Confirm and continue')
        data.update(self.valid_names_post_data[0])
        data.update(self.valid_names_post_data[1])

        response = self.client.post(url, data)

        self.assertEqual(302, response.status_code)

        check_set = {('Joe', 'P', 'Smith', 1, 10, 2010, 15, 9, 2016),
                     ('Bill', 'N', 'Ted', 15, 2, 2009, 23, 12, 2017)}
        fetched_names = models.PreviousName.objects.filter(person_id=self.adult.pk)
        self.assertEqual(2, len(fetched_names))

        name0 = (fetched_names[0].first_name, fetched_names[0].middle_names, fetched_names[0].last_name,
                 fetched_names[0].start_day, fetched_names[0].start_month, fetched_names[0].start_year,
                 fetched_names[0].end_day, fetched_names[0].end_month, fetched_names[0].end_year)
        self.assertTrue(name0 in check_set)
        check_set.remove(name0)

        name1 = (fetched_names[1].first_name, fetched_names[1].middle_names, fetched_names[1].last_name,
                 fetched_names[1].start_day, fetched_names[1].start_month, fetched_names[1].start_year,
                 fetched_names[1].end_day, fetched_names[1].end_month, fetched_names[1].end_year)
        self.assertTrue(name1 in check_set)
        check_set.remove(name1)

        self.assertEqual(0, len(check_set))

    def test_submit_add_returns_to_page_with_second_name_fields(self):

        url = reverse('other-people-previous-names') \
            + '?id={}&person_id={}&type={}'.format(self.application.pk, self.adult.pk, 'ADULT')
        data = self._make_post_data(1, 'Add another name')
        data.update(self.valid_names_post_data[0])

        response = self.client.post(url, data)

        self.assertEqual(302, response.status_code)
        utils.assertRedirectView(response, 'add_previous_name')

        # exactly one of each
        for field, value in [('first_name', ''), ('first_name', 'Joe'),
                             ('middle_names', ''), ('middle_names', 'P'),
                             ('last_name', ''), ('last_name', 'Smith'),
                             ('start_date_0', ''), ('start_date_0', '1'),
                             ('start_date_1', ''), ('start_date_1', '10'),
                             ('start_date_2', ''), ('start_date_2', '2010'),
                             ('end_date_0', ''), ('end_date_0', '15'),
                             ('end_date_1', ''), ('end_date_1', '9'),
                             ('end_date_2', ''), ('end_date_2', '2016')]:
            utils.assertXPathCount(
                response,
                ('//input[normalize-space(@type)="text" and normalize-space(@value)="{value}" '
                 'and contains(normalize-space(@name), "{field}")]').format(field=field, value=value),
                1
            )

    def test_submit_add_saves_original_name_to_database(self):

        url = reverse('other-people-previous-names') \
              + '?id={}&person_id={}&type={}'.format(self.application.pk, self.adult.pk, 'ADULT')

        data = self._make_post_data(1, 'Add another name')
        data.update(self.valid_names_post_data[0])

        response = self.client.post(url, data)

        self.assertEqual(302, response.status_code)

        fetched_names = models.PreviousName.objects.filter(
            application_id=self.application.pk,
            person_id=self.adult.pk,
            other_person_type='ADULT')

        self.assertEqual(1, len(fetched_names))

        name = fetched_names[0]

        self.assertEqual('Joe', name.first_name)
        self.assertEqual('P', name.middle_names)
        self.assertEqual('Smith', name.last_name)
        self.assertEqual(1, name.start_day)
        self.assertEqual(10, name.start_month)
        self.assertEqual(2010, name.start_year)
        self.assertEqual(15, name.end_day)
        self.assertEqual(9, name.end_month)
        self.assertEqual(2016, name.end_year)

    def test_submit_remove_returns_to_page_with_name_fields_removed(self):

        url = reverse('other-people-previous-names') \
            + '?id={}&person_id={}&type={}'.format(self.application.pk, self.adult.pk, 'ADULT')

        data = self._make_post_data(2, 'delete')
        data.update(self.valid_names_post_data[0])
        data.update(self.valid_names_post_data[1])
        data[data['form-0-previous_name_id']] = 'Remove this name'

        response = self.client.post(url, data)

        self.assertEqual(302, response.status_code)
        utils.assertRedirectView(response, 'add_previous_name')

        for field, value in [('first_name', 'Bill'), ('middle_names', 'N'), ('last_name', 'Ted'),
                             ('start_date_0', '15'), ('start_date_1', '2'), ('start_date_2', '2009'),
                             ('end_date_0', '23'), ('end_date_1', '12'), ('end_date_2', '2017')]:
            # exactly one of each field name regardless of value
            utils.assertXPathCount(
                response,
                '//input[normalize-space(@type)="text" and contains(normalize-space(@name), "{field}")]'
                    .format(field=field),
                1
            )
            # each field should have the correct value
            utils.assertXPathValue(
                response,
                ('normalize-space(//input[normalize-space(@type)="text" '
                 'and contains(normalize-space(@name), "{field}")]/@value)').format(field=field),
                value
            )

    def test_submit_remove_deletes_removed_name_from_database(self):

        # create existing database records which match the posted data
        models.PreviousName.objects.create(
            previous_name_id=self.valid_names_post_data[0]['form-0-previous_name_id'],
            person_id=self.adult.pk,
            other_person_type='ADULT',
            first_name=self.valid_names_post_data[0]['form-0-first_name'],
            middle_names=self.valid_names_post_data[0]['form-0-middle_names'],
            last_name=self.valid_names_post_data[0]['form-0-last_name'],
            start_day=int(self.valid_names_post_data[0]['form-0-start_date_0']),
            start_month=int(self.valid_names_post_data[0]['form-0-start_date_1']),
            start_year=int(self.valid_names_post_data[0]['form-0-start_date_2']),
            end_day=int(self.valid_names_post_data[0]['form-0-end_date_0']),
            end_month=int(self.valid_names_post_data[0]['form-0-end_date_1']),
            end_year=int(self.valid_names_post_data[0]['form-0-end_date_2']),
        )
        models.PreviousName.objects.create(
            previous_name_id=self.valid_names_post_data[1]['form-1-previous_name_id'],
            person_id=self.adult.pk,
            other_person_type='ADULT',
            first_name=self.valid_names_post_data[1]['form-1-first_name'],
            middle_names=self.valid_names_post_data[1]['form-1-middle_names'],
            last_name=self.valid_names_post_data[1]['form-1-last_name'],
            start_day=int(self.valid_names_post_data[1]['form-1-start_date_0']),
            start_month=int(self.valid_names_post_data[1]['form-1-start_date_1']),
            start_year=int(self.valid_names_post_data[1]['form-1-start_date_2']),
            end_day=int(self.valid_names_post_data[1]['form-1-end_date_0']),
            end_month=int(self.valid_names_post_data[1]['form-1-end_date_1']),
            end_year=int(self.valid_names_post_data[1]['form-1-end_date_2']),
        )

        data = self._make_post_data(2, 'delete')
        data.update(self.valid_names_post_data[0])
        data.update(self.valid_names_post_data[1])
        data[data['form-0-previous_name_id']] = 'Remove this name'

        url = reverse('other-people-previous-names') \
              + '?id={}&person_id={}&type={}'.format(self.application.pk, self.adult.pk, 'ADULT')

        response = self.client.post(url, data)

        self.assertEqual(302, response.status_code)

        fetched_names = models.PreviousName.objects.filter(
            application_id=self.application.pk,
            person_id=self.adult.pk,
            other_person_type='ADULT')

        # assert only one name remaining now
        self.assertEqual(1, len(fetched_names))
        name = fetched_names[0]
        self.assertEqual('Bill', name.first_name)
        self.assertEqual('N', name.middle_names)
        self.assertEqual('Ted', name.last_name)
        self.assertEqual(15, name.start_day)
        self.assertEqual(2, name.start_month)
        self.assertEqual(2009, name.start_year)
        self.assertEqual(23, name.end_day)
        self.assertEqual(12, name.end_month)
        self.assertEqual(2017, name.end_year)

    def _make_post_data(self, num_names, action):
        return {
            'id': self.application.pk,
            'person_id': self.adult.pk,
            'type': 'ADULT',
            'extra': 1,
            'action': action,
            'form-TOTAL_FORMS': num_names,
            'form-INITIAL_FORMS': num_names,
            'form-MIN_NUM_FORMS': 0,
            'form-MAX_NUM_FORMS': 1000,
        }


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
        reloaded_arc_record = models.Arc.objects.get(pk=self.application.application_id)
        self.assertEqual(reloaded_arc_record.references_review, ARC_STATUS_FLAGGED)

        # 3. Check that comment has been correctly appended to application
        try:
            arc_comments = models.ArcComments.objects.get(
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
        reloaded_application = models.Application.objects.get(pk=self.application.application_id)
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

        adult = models.AdultInHome.objects.get(application_id=self.application.pk)
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

        adult = models.AdultInHome.objects.get(application_id=self.application.pk)
        adult.military_base = True
        adult.save()

        care_type = models.ChildcareType.objects.get(application_id=self.application.pk)
        care_type.zero_to_five = True
        care_type.save()

        response = self.client.get(reverse('arc-summary'), data={'id': self.application.pk})

        utils.assertSummaryField(response, 'Lived or worked on British military base in the last 5 years?', 'Yes')

    def test_doesnt_display_adult_military_base_field_if_not_caring_for_zero_to_five_year_olds(self):

        self.application.adults_in_home = True
        self.application.working_in_other_childminder_home = False
        self.application.save()

        care_type = models.ChildcareType.objects.get(application_id=self.application.pk)
        care_type.zero_to_five = False
        care_type.save()

        response = self.client.get(reverse('arc-summary'), data={'id': self.application.pk})

        utils.assertNotSummaryField(response, 'Lived or worked on British military base in the last 5 years?')

    def test_displays_adult_dbs_recent_field_only_for_adults_on_capita_list(self):

        self.application.adults_in_home = True
        self.application.working_in_other_childminder_home = False
        self.application.save()

        adult1 = models.AdultInHome.objects.get(application_id=self.application.pk)
        adult1.first_name = 'Joe'
        adult1.middle_names = 'Anthony'
        adult1.last_name = 'Bloggs'
        adult1.dbs_certificate_number = '123456789012'
        adult1.capita = False
        adult1.save()

        models.AdultInHome.objects.create(
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

        adult1 = models.AdultInHome.objects.get(application_id=self.application.pk)
        adult1.first_name = 'Joe'
        adult1.middle_names = 'Anthony'
        adult1.last_name = 'Bloggs'
        adult1.dbs_certificate_number = '123456789012'
        adult1.capita = False
        adult1.enhanced_check = True
        adult1.on_update = True
        adult1.save()

        models.AdultInHome.objects.create(
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

        adult1 = models.AdultInHome.objects.get(application_id=self.application.pk)
        adult1.first_name = 'Joe'
        adult1.middle_names = 'Anthony'
        adult1.last_name = 'Bloggs'
        adult1.dbs_certificate_number = '123456789012'
        adult1.capita = False
        adult1.enhanced_check = True
        adult1.on_update = True
        adult1.save()

        models.AdultInHome.objects.create(
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

        models.AdultInHome.objects.create(
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

    def test_shows_applicants_previous_names(self):
        self.skipTest('testNotImplemented')

    def test_shows_applicants_previous_addresses(self):
        self.skipTest('testNotImplemented')

    class MockDatetime(datetime):
        @classmethod
        def now(cls):
            return datetime(2019, 2, 27, 17, 30, 5)

    @patch('arc_application.views.base.datetime', new=MockDatetime)
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

        arc = models.Arc.objects.get(application_id=self.application.pk)

        for task in ARC_TASKS_ALL:
            setattr(arc, '{}_review'.format(task), ARC_STATUS_COMPLETED)

        arc.save()

        # id must be both GET and POST parameter.
        # Follow redirects because release is done at redirect target url
        response = self.client.post(reverse('arc-summary') + '?id=' + self.application.pk,
                                    data={'id': self.application.pk},
                                    follow=True)

        refetched_application = models.Application.objects.get(pk=self.application.pk)
        # in accepted status
        self.assertEqual(datetime(2019, 2, 27, 17, 30, 5, tzinfo=timezone.utc),
                         refetched_application.date_accepted)
        self.assertEqual(APP_STATUS_ACCEPTED, refetched_application.application_status)
        # declaration unchanged
        self.assertEqual(APP_STATUS_COMPLETED, refetched_application.declarations_status)
        self.assertTrue(refetched_application.declaration_confirmation)

        # unassigned from arc user
        refetched_arc = models.Arc.objects.get(pk=arc.pk)
        self.assertTrue(refetched_arc.user_id in ('', None))

    @patch('arc_application.views.base.datetime', new=MockDatetime)
    def test_submit_summary_releases_application_as_needing_info_in_database_if_tasks_have_been_flagged(self):

        ARC_TASKS_FLAGGED = ['childcare_type', 'personal_details']
        ARC_TASKS_UNFLAGGED = ['login_details', 'your_children', 'first_aid', 'childcare_training', 'dbs', 'health',
                               'references', 'people_in_home']
        APP_TASKS_TO_BE_FLAGGED = ['personal_details', 'childcare_type']
        APP_TASKS_NOT_TO_BE_FLAGGED = ['login_details', 'your_children', 'first_aid_training', 'childcare_training',
                                       'criminal_record_check', 'health', 'references', 'people_in_home']
        APP_TASKS_ALL = APP_TASKS_TO_BE_FLAGGED + APP_TASKS_NOT_TO_BE_FLAGGED

        for task in APP_TASKS_ALL:
            setattr(self.application, '{}_status'.format(task), APP_STATUS_COMPLETED)
            setattr(self.application, '{}_arc_flagged'.format(task), False)

        self.application.declarations_status = APP_STATUS_COMPLETED
        self.application.declaration_confirmation = True
        self.application.application_status = APP_STATUS_REVIEW
        self.application.save()

        arc = models.Arc.objects.get(application_id=self.application.pk)

        for task in ARC_TASKS_UNFLAGGED:
            setattr(arc, '{}_review'.format(task), ARC_STATUS_COMPLETED)

        for task in ARC_TASKS_FLAGGED:
            setattr(arc, '{}_review'.format(task), ARC_STATUS_FLAGGED)

        arc.save()

        # id must be both GET and POST parameter
        # Follow redirects because release is done at redirect target url
        response = self.client.post(reverse('arc-summary') + '?id=' + self.application.pk,
                                    data={'id': self.application.pk},
                                    follow=True)

        refetched_application = models.Application.objects.get(pk=self.application.pk)
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
        refetched_arc = models.Arc.objects.get(pk=arc.pk)
        self.assertTrue(refetched_arc.user_id in ('', None))

        # flagged tasks still recorded in arc record
        for task in ARC_TASKS_FLAGGED:
            self.assertEqual(ARC_STATUS_FLAGGED, getattr(refetched_arc, '{}_review'.format(task)))
        for task in ARC_TASKS_UNFLAGGED:
            self.assertEqual(ARC_STATUS_COMPLETED, getattr(refetched_arc, '{}_review'.format(task)))
