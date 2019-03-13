import datetime
from unittest.mock import patch

from django.test import TestCase, tag

from ..utils import create_childminder_application, create_arc_user
from ...forms.previous_names import PersonPreviousNameForm


ERROR_MESSAGE_FIRST_NAME_BLANK = 'You must enter a first name'
ERROR_MESSAGE_LAST_NAME_BLANK = 'You must enter a last name'

ERROR_MESSAGE_DATE_BLANK = 'Enter the date, including the month and year'
ERROR_MESSAGE_DAY_OUT_OF_RANGE = 'Day must be between 1 and 31'
ERROR_MESSAGE_MONTH_OUT_OF_RANGE = 'Month must be between 1 and 12'
ERROR_MESSAGE_START_YEAR_BEFORE_1900 = 'Start date must be after 1900'
ERROR_MESSAGE_END_YEAR_BEFORE_1900 = 'End date must be after 1900'
ERROR_MESSAGE_YEAR_LESS_THAN_4_DIGITS = 'Enter the whole year (4 digits)'
ERROR_MESSAGE_INVALID_DATE = 'Enter a real date'
ERROR_MESSAGE_NON_NUMERIC = 'Use numbers for the date'

ERROR_MESSAGE_START_DATE_AFTER_CURRENT_DATE = 'Start date must be today or in the past'
ERROR_MESSAGE_START_DATE_AFTER_END_DATE = 'Start date must be before the end date'

ERROR_MESSAGE_END_DATE_AFTER_CURRENT_DATE = 'End date must be before today or in the past'
ERROR_MESSAGE_END_DATE_BEFORE_START_DATE = 'End date must be after the start date'


@tag('unit')
class ReviewPersonalDetailsPreviousNamesFormValidationTests(TestCase):

    form = PersonPreviousNameForm

    def setUp(self):
        self.arc_user = create_arc_user()
        self.application = create_childminder_application(self.arc_user.pk)
        self.client.login(username='arc_test', password='my_secret')

    def test_invalid_when_all_data_is_blank(self):
        data = {
            'first_name': '',
            'middle_names': '',
            'last_name': '',
            'start_date_0': '',
            'start_date_1': '',
            'start_date_2': '',
            'end_date_0': '',
            'end_date_1': '',
            'end_date_2': '',
        }
        form = self.form(data)

        self.assertFalse(form.is_valid())

        # Check error messages
        self.assertEqual(form.errors, {
            'first_name': [ERROR_MESSAGE_FIRST_NAME_BLANK],
            'last_name': [ERROR_MESSAGE_LAST_NAME_BLANK],
            'start_date': [ERROR_MESSAGE_DATE_BLANK],
            'end_date': [ERROR_MESSAGE_DATE_BLANK],
        })

    def test_invalid_when_start_or_end_day_too_large(self):

        data = {
            'first_name': 'Fred',
            'middle_names': '',
            'last_name': 'Bloggs',
            'start_date_0': '32',
            'start_date_1': '12',
            'start_date_2': '2018',
            'end_date_0': '33',
            'end_date_1': '11',
            'end_date_2': '2018',
        }
        form = self.form(data)

        self.assertFalse(form.is_valid())

        # Check error messages
        self.assertEqual(form.errors, {
            'start_date': [ERROR_MESSAGE_DAY_OUT_OF_RANGE],
            'end_date': [ERROR_MESSAGE_DAY_OUT_OF_RANGE]
        })

    def test_invalid_when_start_or_end_day_too_small(self):

        data = {
            'first_name': 'Fred',
            'middle_names': '',
            'last_name': 'Bloggs',
            'start_date_0': '0',
            'start_date_1': '9',
            'start_date_2': '2018',
            'end_date_0': '0',
            'end_date_1': '11',
            'end_date_2': '2018',
        }
        form = self.form(data)

        self.assertFalse(form.is_valid())

        # Check error messages
        self.assertEqual(form.errors, {
            'start_date': [ERROR_MESSAGE_DAY_OUT_OF_RANGE],
            'end_date': [ERROR_MESSAGE_DAY_OUT_OF_RANGE]
        })

    def test_invalid_if_start_or_end_month_too_large(self):
        data = {
            'first_name': 'Fred',
            'middle_names': '',
            'last_name': 'Bloggs',
            'start_date_0': '1',
            'start_date_1': '13',
            'start_date_2': '2018',
            'end_date_0': '2',
            'end_date_1': '14',
            'end_date_2': '2018',
        }
        form = self.form(data)

        self.assertFalse(form.is_valid())

        # Check error messages
        self.assertEqual(form.errors, {
            'start_date': [ERROR_MESSAGE_MONTH_OUT_OF_RANGE],
            'end_date': [ERROR_MESSAGE_MONTH_OUT_OF_RANGE]
        })

    def test_invalid_if_start_or_end_month_too_small(self):
        data = {
            'first_name': 'Fred',
            'middle_names': '',
            'last_name': 'Bloggs',
            'start_date_0': '1',
            'start_date_1': '0',
            'start_date_2': '2018',
            'end_date_0': '2',
            'end_date_1': '0',
            'end_date_2': '2018',
        }
        form = self.form(data)

        self.assertFalse(form.is_valid())

        # Check error messages
        self.assertEqual(form.errors, {
            'start_date': [ERROR_MESSAGE_MONTH_OUT_OF_RANGE],
            'end_date': [ERROR_MESSAGE_MONTH_OUT_OF_RANGE]
        })

    def test_invalid_if_start_or_end_year_before_1900(self):

        data = {
            'first_name': 'Fred',
            'middle_names': '',
            'last_name': 'Bloggs',
            'start_date_0': '1',
            'start_date_1': '8',
            'start_date_2': '1888',
            'end_date_0': '2',
            'end_date_1': '10',
            'end_date_2': '1889',
        }
        form = self.form(data)

        self.assertFalse(form.is_valid())

        # Check error messages
        self.assertEqual(form.errors, {
            'start_date': [ERROR_MESSAGE_START_YEAR_BEFORE_1900],
            'end_date': [ERROR_MESSAGE_END_YEAR_BEFORE_1900]
        })

    def test_invalid_if_start_or_end_year_less_than_4_digits(self):

        data = {
            'first_name': 'Fred',
            'middle_names': '',
            'last_name': 'Bloggs',
            'start_date_0': '1',
            'start_date_1': '8',
            'start_date_2': '199',
            'end_date_0': '2',
            'end_date_1': '10',
            'end_date_2': '18',
        }
        form = self.form(data)

        self.assertFalse(form.is_valid())

        # Check error messages
        self.assertEqual(form.errors, {
            'start_date': [ERROR_MESSAGE_YEAR_LESS_THAN_4_DIGITS],
            'end_date': [ERROR_MESSAGE_YEAR_LESS_THAN_4_DIGITS],
        })

    def test_invalid_if_start_or_end_date_is_not_a_real_date(self):

        data = {
            'first_name': 'Fred',
            'middle_names': '',
            'last_name': 'Bloggs',
            'start_date_0': '31',   # Only 30 days in June
            'start_date_1': '6',
            'start_date_2': '2017',
            'end_date_0': '29',     # 1999 wasn't a leap year
            'end_date_1': '2',
            'end_date_2': '1999',
        }
        form = self.form(data)

        self.assertFalse(form.is_valid())

        # Check error messages
        self.assertEqual(form.errors, {
            'start_date': [ERROR_MESSAGE_INVALID_DATE],
            'end_date': [ERROR_MESSAGE_INVALID_DATE],
        })

    def test_invalid_if_start_or_end_date_contains_non_numeric_data(self):

        data = {
            'first_name': 'Fred',
            'middle_names': '',
            'last_name': 'Bloggs',
            'start_date_0': '16',
            'start_date_1': 'H',
            'start_date_2': '2017',
            'end_date_0': '!!',
            'end_date_1': '3',
            'end_date_2': '20XX',
        }
        form = self.form(data)

        self.assertFalse(form.is_valid())

        # Check error messages
        self.assertEqual(form.errors, {
            'start_date': [ERROR_MESSAGE_NON_NUMERIC],
            'end_date': [ERROR_MESSAGE_NON_NUMERIC],
        })

    class MockDate(datetime.date):
        @classmethod
        def today(cls):
            return datetime.date(2018, 12, 14)

    @patch('datetime.date', MockDate)
    def test_invalid_if_start_date_after_current_date(self):

        data = {
            'first_name': 'Fred',
            'middle_names': '',
            'last_name': 'Bloggs',
            'start_date_0': '15',
            'start_date_1': '12',
            'start_date_2': '2018',
            'end_date_0': '1',
            'end_date_1': '11',
            'end_date_2': '2017',
        }
        form = self.form(data)

        self.assertFalse(form.is_valid())

        # Check error messages
        self.assertEqual(form.errors, {
            'start_date': [ERROR_MESSAGE_START_DATE_AFTER_CURRENT_DATE],
        })

    @patch('datetime.date', MockDate)
    def test_invalid_if_end_date_after_current_date(self):

        data = {
            'first_name': 'Fred',
            'middle_names': '',
            'last_name': 'Bloggs',
            'start_date_0': '21',
            'start_date_1': '6',
            'start_date_2': '2017',
            'end_date_0': '15',
            'end_date_1': '12',
            'end_date_2': '2018',
        }
        form = self.form(data)

        self.assertFalse(form.is_valid())

        # Check error messages
        self.assertEqual(form.errors, {
            'end_date': [ERROR_MESSAGE_END_DATE_AFTER_CURRENT_DATE],
        })

    def test_invalid_if_start_date_after_end_date(self):

        data = {
            'first_name': 'Fred',
            'middle_names': '',
            'last_name': 'Bloggs',
            'start_date_0': '21',
            'start_date_1': '6',
            'start_date_2': '2017',
            'end_date_0': '15',
            'end_date_1': '12',
            'end_date_2': '2016',
        }
        form = self.form(data)

        self.assertFalse(form.is_valid())

        # Check error messages
        self.assertEqual(form.errors, {
            'start_date': [ERROR_MESSAGE_START_DATE_AFTER_END_DATE],
            'end_date': [ERROR_MESSAGE_END_DATE_BEFORE_START_DATE],
        })
