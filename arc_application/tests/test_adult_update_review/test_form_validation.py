import datetime
from unittest.mock import patch
from unittest import skipUnless
from django.conf import settings

from django.test import TestCase, tag

from ...forms.previous_addresses import PreviousAddressManualForm, PreviousAddressSelectForm, PreviousAddressEntryForm
from ..utils import create_childminder_application, create_arc_user
from ...forms.previous_names import PersonPreviousNameForm

@tag('unit')
@skipUnless(settings.ENABLE_HM, 'Skipping test as HM feature toggle equated to False')
class ReviewPersonalDetailsPreviousNamesFormValidationTests(TestCase):
    form = PersonPreviousNameForm

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
            'first_name': [self.ERROR_MESSAGE_FIRST_NAME_BLANK],
            'last_name': [self.ERROR_MESSAGE_LAST_NAME_BLANK],
            'start_date': [self.ERROR_MESSAGE_DATE_BLANK],
            'end_date': [self.ERROR_MESSAGE_DATE_BLANK],
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
            'start_date': [self.ERROR_MESSAGE_DAY_OUT_OF_RANGE],
            'end_date': [self.ERROR_MESSAGE_DAY_OUT_OF_RANGE]
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
            'start_date': [self.ERROR_MESSAGE_DAY_OUT_OF_RANGE],
            'end_date': [self.ERROR_MESSAGE_DAY_OUT_OF_RANGE]
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
            'start_date': [self.ERROR_MESSAGE_MONTH_OUT_OF_RANGE],
            'end_date': [self.ERROR_MESSAGE_MONTH_OUT_OF_RANGE]
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
            'start_date': [self.ERROR_MESSAGE_MONTH_OUT_OF_RANGE],
            'end_date': [self.ERROR_MESSAGE_MONTH_OUT_OF_RANGE]
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
            'start_date': [self.ERROR_MESSAGE_START_YEAR_BEFORE_1900],
            'end_date': [self.ERROR_MESSAGE_END_YEAR_BEFORE_1900]
        })

    def test_invalid_all_error_messages_show_when_all_values_out_of_range(self):
        data = {
            'first_name': 'Fred',
            'middle_names': '',
            'last_name': 'Bloggs',
            'start_date_0': '43',
            'start_date_1': '59',
            'start_date_2': '1400',
            'end_date_0': '350',
            'end_date_1': '13',
            'end_date_2': '1889',
        }
        form = self.form(data)

        self.assertFalse(form.is_valid())

        # Check error messages
        self.assertEqual(form.errors, {
            'start_date': [self.ERROR_MESSAGE_DAY_OUT_OF_RANGE, self.ERROR_MESSAGE_MONTH_OUT_OF_RANGE,
                           self.ERROR_MESSAGE_START_YEAR_BEFORE_1900],
            'end_date': [self.ERROR_MESSAGE_DAY_OUT_OF_RANGE, self.ERROR_MESSAGE_MONTH_OUT_OF_RANGE,
                         self.ERROR_MESSAGE_END_YEAR_BEFORE_1900]
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
            'start_date': [self.ERROR_MESSAGE_YEAR_LESS_THAN_4_DIGITS],
            'end_date': [self.ERROR_MESSAGE_YEAR_LESS_THAN_4_DIGITS],
        })

    def test_invalid_if_start_or_end_date_is_not_a_real_date(self):
        data = {
            'first_name': 'Fred',
            'middle_names': '',
            'last_name': 'Bloggs',
            'start_date_0': '31',  # Only 30 days in June
            'start_date_1': '6',
            'start_date_2': '2017',
            'end_date_0': '29',  # 1999 wasn't a leap year
            'end_date_1': '2',
            'end_date_2': '1999',
        }
        form = self.form(data)

        self.assertFalse(form.is_valid())

        # Check error messages
        self.assertEqual(form.errors, {
            'start_date': [self.ERROR_MESSAGE_INVALID_DATE],
            'end_date': [self.ERROR_MESSAGE_INVALID_DATE],
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
            'start_date': [self.ERROR_MESSAGE_NON_NUMERIC],
            'end_date': [self.ERROR_MESSAGE_NON_NUMERIC],
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
            'start_date': [self.ERROR_MESSAGE_START_DATE_AFTER_CURRENT_DATE],
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
            'end_date': [self.ERROR_MESSAGE_END_DATE_AFTER_CURRENT_DATE],
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
            'start_date': [self.ERROR_MESSAGE_START_DATE_AFTER_END_DATE],
            'end_date': [self.ERROR_MESSAGE_END_DATE_BEFORE_START_DATE],
        })


@tag('unit')
@skipUnless(settings.ENABLE_HM, 'Skipping test as HM feature toggle equated to False')
class PersonalDetailsPreviousAddressEnterPostCodeFormValidationTests(TestCase):
    """
    Tests to check that the PreviousAddress ENTER PostCode Form validates correctly.
    """
    form = PreviousAddressEntryForm

    ERROR_MESSAGE_POSTCODE_NOT_ENTERED = 'Please enter your postcode'

    def test_invalid_when_no_postcode_entered(self):
        data = {
            'postcode': ''
        }
        form = self.form(data)

        self.assertFalse(form.is_valid())

        # Check error messages
        self.assertEqual(form.errors, {
            'postcode': [self.ERROR_MESSAGE_POSTCODE_NOT_ENTERED]
        })


@tag('unit')
@skipUnless(settings.ENABLE_HM, 'Skipping test as HM feature toggle equated to False')
class PersonalDetailsPreviousAddressSelectPostCodeFormValidationTests(TestCase):
    """
    Tests to check that the PreviousAddress SELECT PostCode Form validates correctly.
    """
    form = PreviousAddressSelectForm

    ERROR_MESSAGE_ADDRESS_BLANK = 'Please select your address'
    ERROR_MESSAGE_ADDRESS_INVALID = 'Select a valid choice. {0} is not one of the available choices.'

    ERROR_MESSAGE_DATE_BLANK = 'Enter the full date, including the day, month and year'
    ERROR_MESSAGE_DAY_OUT_OF_RANGE = 'Day must be between 1 and 31'
    ERROR_MESSAGE_MONTH_OUT_OF_RANGE = 'Month must be between 1 and 12'
    ERROR_MESSAGE_MOVED_IN_YEAR_BEFORE_1900 = 'Date moved in must be after 1900'
    ERROR_MESSAGE_MOVED_OUT_YEAR_BEFORE_1900 = 'Date you moved out must be after 1900'
    ERROR_MESSAGE_YEAR_LESS_THAN_4_DIGITS = 'Enter the whole year (4 digits)'
    ERROR_MESSAGE_INVALID_DATE = 'Enter a real date'
    ERROR_MESSAGE_NON_NUMERIC = 'Use numbers for the date'

    ERROR_MESSAGE_MOVED_IN_DATE_AFTER_CURRENT_DATE = 'Date moved in must be today or in the past'
    ERROR_MESSAGE_MOVED_IN_DATE_AFTER_MOVED_OUT_DATE = 'Date you moved in must be before date you moved out'

    ERROR_MESSAGE_MOVED_OUT_DATE_AFTER_CURRENT_DATE = 'Date you moved out must be today or in the past'
    ERROR_MESSAGE_MOVED_OUT_DATE_BEFORE_MOVED_IN_DATE = 'Date you moved out must be after the date you moved in'

    # Valid data for use in tests that are not testing that functionality #
    VALID_POSTCODE_DATA = {
        'address': 'Informed Solutions',
    }

    VALID_CHOICES = [
        ('Informed Solutions', 'Informed Solutions')
    ]

    VALID_MOVED_IN_AND_OUT_DATE_DATA = {
        'moved_in_date_0': '21',  # Day
        'moved_in_date_1': '3',  # Month
        'moved_in_date_2': '1980',  # Year
        'moved_out_date_0': '12',
        'moved_out_date_1': '8',
        'moved_out_date_2': '2002'
    }

    def test_invalid_when_all_data_is_blank(self):
        data = {
            'address': '',
            'moved_in_date_0': '',
            'moved_in_date_1': '',
            'moved_in_date_2': '',
            'moved_out_date_0': '',
            'moved_out_date_1': '',
            'moved_out_date_2': '',
        }
        choices = []

        form = self.form(data, choices=choices)

        self.assertFalse(form.is_valid())

        # Check error messages
        self.assertEqual(form.errors, {
            'address': [self.ERROR_MESSAGE_ADDRESS_BLANK],
            'moved_in_date': [self.ERROR_MESSAGE_DATE_BLANK],
            'moved_out_date': [self.ERROR_MESSAGE_DATE_BLANK],
        })

    def test_invalid_when_address_not_in_choices(self):
        data = {
            'address': 'Some Other Address'
        }
        data.update(self.VALID_MOVED_IN_AND_OUT_DATE_DATA)

        form = self.form(data, choices=self.VALID_CHOICES)

        self.assertFalse(form.is_valid())

        # Check error messages
        self.assertEqual(form.errors, {
            'address': [self.ERROR_MESSAGE_ADDRESS_INVALID.format('Some Other Address')]
        })

    def test_invalid_when_choices_blank(self):
        data = {
            'address': 'Some Other Address'
        }
        data.update(self.VALID_MOVED_IN_AND_OUT_DATE_DATA)

        form = self.form(data, choices=[])

        self.assertFalse(form.is_valid())

        # Check error messages
        self.assertEqual(form.errors, {
            'address': [self.ERROR_MESSAGE_ADDRESS_INVALID.format('Some Other Address')]
        })

    def test_invalid_when_start_or_end_day_too_large(self):
        data = {
            'moved_in_date_0': '32',
            'moved_in_date_1': '12',
            'moved_in_date_2': '2018',
            'moved_out_date_0': '33',
            'moved_out_date_1': '11',
            'moved_out_date_2': '2018',
        }
        data.update(self.VALID_POSTCODE_DATA)

        form = self.form(data, choices=self.VALID_CHOICES)

        self.assertFalse(form.is_valid())

        # Check error messages
        self.assertEqual(form.errors, {
            'moved_in_date': [self.ERROR_MESSAGE_DAY_OUT_OF_RANGE],
            'moved_out_date': [self.ERROR_MESSAGE_DAY_OUT_OF_RANGE]
        })

    def test_invalid_when_start_or_end_day_too_small(self):
        data = {
            'moved_in_date_0': '0',
            'moved_in_date_1': '9',
            'moved_in_date_2': '2018',
            'moved_out_date_0': '0',
            'moved_out_date_1': '11',
            'moved_out_date_2': '2018',
        }
        data.update(self.VALID_POSTCODE_DATA)

        form = self.form(data, choices=self.VALID_CHOICES)

        self.assertFalse(form.is_valid())

        # Check error messages
        self.assertEqual(form.errors, {
            'moved_in_date': [self.ERROR_MESSAGE_DAY_OUT_OF_RANGE],
            'moved_out_date': [self.ERROR_MESSAGE_DAY_OUT_OF_RANGE]
        })

    def test_invalid_if_moved_in_or_moved_out_month_too_large(self):
        data = {
            'moved_in_date_0': '1',
            'moved_in_date_1': '13',
            'moved_in_date_2': '2018',
            'moved_out_date_0': '2',
            'moved_out_date_1': '14',
            'moved_out_date_2': '2018',
        }
        data.update(self.VALID_POSTCODE_DATA)

        form = self.form(data, choices=self.VALID_CHOICES)

        self.assertFalse(form.is_valid())

        # Check error messages
        self.assertEqual(form.errors, {
            'moved_in_date': [self.ERROR_MESSAGE_MONTH_OUT_OF_RANGE],
            'moved_out_date': [self.ERROR_MESSAGE_MONTH_OUT_OF_RANGE]
        })

    def test_invalid_if_moved_in_or_moved_out_month_too_small(self):
        data = {
            'moved_in_date_0': '1',
            'moved_in_date_1': '0',
            'moved_in_date_2': '2018',
            'moved_out_date_0': '2',
            'moved_out_date_1': '0',
            'moved_out_date_2': '2018',
        }
        data.update(self.VALID_POSTCODE_DATA)

        form = self.form(data, choices=self.VALID_CHOICES)

        self.assertFalse(form.is_valid())

        # Check error messages
        self.assertEqual(form.errors, {
            'moved_in_date': [self.ERROR_MESSAGE_MONTH_OUT_OF_RANGE],
            'moved_out_date': [self.ERROR_MESSAGE_MONTH_OUT_OF_RANGE]
        })

    def test_invalid_if_moved_in_or_moved_out_year_before_1900(self):
        data = {
            'moved_in_date_0': '1',
            'moved_in_date_1': '8',
            'moved_in_date_2': '1888',
            'moved_out_date_0': '2',
            'moved_out_date_1': '10',
            'moved_out_date_2': '1889',
        }
        data.update(self.VALID_POSTCODE_DATA)

        form = self.form(data, choices=self.VALID_CHOICES)

        self.assertFalse(form.is_valid())

        # Check error messages
        self.assertEqual(form.errors, {
            'moved_in_date': [self.ERROR_MESSAGE_MOVED_IN_YEAR_BEFORE_1900],
            'moved_out_date': [self.ERROR_MESSAGE_MOVED_OUT_YEAR_BEFORE_1900]
        })

    def test_invalid_if_moved_in_or_moved_out_year_less_than_4_digits(self):
        data = {
            'moved_in_date_0': '1',
            'moved_in_date_1': '8',
            'moved_in_date_2': '199',
            'moved_out_date_0': '2',
            'moved_out_date_1': '10',
            'moved_out_date_2': '18',
        }
        data.update(self.VALID_POSTCODE_DATA)

        form = self.form(data, choices=self.VALID_CHOICES)

        self.assertFalse(form.is_valid())

        # Check error messages
        self.assertEqual(form.errors, {
            'moved_in_date': [self.ERROR_MESSAGE_YEAR_LESS_THAN_4_DIGITS],
            'moved_out_date': [self.ERROR_MESSAGE_YEAR_LESS_THAN_4_DIGITS],
        })

    def test_invalid_if_moved_in_or_moved_out_date_is_not_a_real_date(self):
        data = {
            'moved_in_date_0': '31',  # Only 30 days in June
            'moved_in_date_1': '6',
            'moved_in_date_2': '2017',
            'moved_out_date_0': '29',  # 1999 wasn't a leap year
            'moved_out_date_1': '2',
            'moved_out_date_2': '1999',
        }
        data.update(self.VALID_POSTCODE_DATA)

        form = self.form(data, choices=self.VALID_CHOICES)

        self.assertFalse(form.is_valid())

        # Check error messages
        self.assertEqual(form.errors, {
            'moved_in_date': [self.ERROR_MESSAGE_INVALID_DATE],
            'moved_out_date': [self.ERROR_MESSAGE_INVALID_DATE],
        })

    def test_invalid_if_moved_in_or_moved_out_date_contains_non_numeric_data(self):
        data = {
            'moved_in_date_0': '16',
            'moved_in_date_1': 'H',
            'moved_in_date_2': '2017',
            'moved_out_date_0': '!!',
            'moved_out_date_1': '3',
            'moved_out_date_2': '20XX',
        }
        data.update(self.VALID_POSTCODE_DATA)

        form = self.form(data, choices=self.VALID_CHOICES)

        self.assertFalse(form.is_valid())

        # Check error messages
        self.assertEqual(form.errors, {
            'moved_in_date': [self.ERROR_MESSAGE_NON_NUMERIC],
            'moved_out_date': [self.ERROR_MESSAGE_NON_NUMERIC],
        })

    class MockDate(datetime.date):
        @classmethod
        def today(cls):
            return datetime.date(2018, 12, 14)

    @patch('datetime.date', MockDate)
    def test_invalid_if_moved_in_date_after_current_date(self):
        data = {
            'moved_in_date_0': '15',
            'moved_in_date_1': '12',
            'moved_in_date_2': '2018',
            'moved_out_date_0': '1',
            'moved_out_date_1': '11',
            'moved_out_date_2': '2017',
        }
        data.update(self.VALID_POSTCODE_DATA)

        form = self.form(data, choices=self.VALID_CHOICES)

        self.assertFalse(form.is_valid())

        # Check error messages
        self.assertEqual(form.errors, {
            'moved_in_date': [self.ERROR_MESSAGE_MOVED_IN_DATE_AFTER_CURRENT_DATE],
        })

    @patch('datetime.date', MockDate)
    def test_invalid_if_moved_out_date_after_current_date(self):
        data = {
            'moved_in_date_0': '21',
            'moved_in_date_1': '6',
            'moved_in_date_2': '2017',
            'moved_out_date_0': '15',
            'moved_out_date_1': '12',
            'moved_out_date_2': '2018',
        }
        data.update(self.VALID_POSTCODE_DATA)

        form = self.form(data, choices=self.VALID_CHOICES)

        self.assertFalse(form.is_valid())

        # Check error messages
        self.assertEqual(form.errors, {
            'moved_out_date': [self.ERROR_MESSAGE_MOVED_OUT_DATE_AFTER_CURRENT_DATE],
        })

    def test_invalid_if_moved_in_date_after_moved_out_date(self):
        data = {
            'moved_in_date_0': '21',
            'moved_in_date_1': '6',
            'moved_in_date_2': '2017',
            'moved_out_date_0': '15',
            'moved_out_date_1': '12',
            'moved_out_date_2': '2016',
        }
        data.update(self.VALID_POSTCODE_DATA)

        form = self.form(data, choices=self.VALID_CHOICES)

        self.assertFalse(form.is_valid())

        # Check error messages
        self.assertEqual(form.errors, {
            'moved_in_date': [self.ERROR_MESSAGE_MOVED_IN_DATE_AFTER_MOVED_OUT_DATE],
            'moved_out_date': [self.ERROR_MESSAGE_MOVED_OUT_DATE_BEFORE_MOVED_IN_DATE],
        })

    def test_valid_data(self):
        data = {}
        data.update(self.VALID_MOVED_IN_AND_OUT_DATE_DATA)
        data.update(self.VALID_POSTCODE_DATA)

        form = self.form(data, choices=self.VALID_CHOICES)

        self.assertTrue(form.is_valid())


@tag('unit')
@skipUnless(settings.ENABLE_HM, 'Skipping test as HM feature toggle equated to False')
class PersonalDetailsPreviousAddressManualPostCodeFormValidationTests(TestCase):
    """
    Tests to check that the PreviousAddress MANUAL PostCode Form validates correctly.
    """
    form = PreviousAddressManualForm

    # Manual address entry field validation messages
    ERROR_MESSAGE_STREET_LINE_1_BLANK = 'Please enter the first line of your address'
    ERROR_MESSAGE_STREET_LINE_1_TOO_LONG = 'The first line of your address must be under 50 characters long'
    ERROR_MESSAGE_STREET_LINE_2_TOO_LONG = 'The second line of your address must be under 50 characters long'
    ERROR_MESSAGE_TOWN_BLANK = 'Please enter the name of the town or city'
    ERROR_MESSAGE_TOWN_INVALID = 'Please spell out the name of the town or city using letters'
    ERROR_MESSAGE_TOWN_TOO_LONG = 'The name of the town or city must be under 50 characters long'
    ERROR_MESSAGE_COUNTY_INVALID = 'Please spell out the name of the county using letters'
    ERROR_MESSAGE_COUNTY_TOO_LONG = 'The name of the county must be under 50 characters long'
    ERROR_MESSAGE_COUNTRY_BLANK = 'Please enter the name of the country'
    ERROR_MESSAGE_COUNTRY_INVALID = 'Spell out the name of the country using letters'
    ERROR_MESSAGE_COUNTRY_TOO_LONG = 'The name of the country must be under 50 characters long'
    ERROR_MESSAGE_POSTCODE_BLANK = 'Please enter their postcode'
    ERROR_MESSAGE_POSTCODE_INVALID = 'Please enter a valid postcode'

    # Moved in/out date validation messages
    ERROR_MESSAGE_DATE_BLANK = 'Enter the full date, including the day, month and year'
    ERROR_MESSAGE_DAY_OUT_OF_RANGE = 'Day must be between 1 and 31'
    ERROR_MESSAGE_MONTH_OUT_OF_RANGE = 'Month must be between 1 and 12'
    ERROR_MESSAGE_MOVED_IN_YEAR_BEFORE_1900 = 'Date moved in must be after 1900'
    ERROR_MESSAGE_MOVED_OUT_YEAR_BEFORE_1900 = 'Date you moved out must be after 1900'
    ERROR_MESSAGE_YEAR_LESS_THAN_4_DIGITS = 'Enter the whole year (4 digits)'
    ERROR_MESSAGE_INVALID_DATE = 'Enter a real date'
    ERROR_MESSAGE_NON_NUMERIC = 'Use numbers for the date'

    ERROR_MESSAGE_MOVED_IN_DATE_AFTER_CURRENT_DATE = 'Date moved in must be today or in the past'
    ERROR_MESSAGE_MOVED_IN_DATE_AFTER_MOVED_OUT_DATE = 'Date you moved in must be before date you moved out'

    ERROR_MESSAGE_MOVED_OUT_DATE_AFTER_CURRENT_DATE = 'Date you moved out must be today or in the past'
    ERROR_MESSAGE_MOVED_OUT_DATE_BEFORE_MOVED_IN_DATE = 'Date you moved out must be after the date you moved in'

    # Valid data for use in tests that are not testing that functionality #
    VALID_ADDRESS_DATA = {
        'street_line1': '202 MyFirstHomeAddressStreet',
        'street_line2': '',
        'town': 'Preston',
        'county': 'Lancashire',
        'country': 'United Kingdom',
        'postcode': 'PR2 3SQ'
    }

    VALID_MOVED_IN_AND_OUT_DATE_DATA = {
        'moved_in_date_0': '21',  # Day
        'moved_in_date_1': '3',  # Month
        'moved_in_date_2': '1980',  # Year
        'moved_out_date_0': '12',
        'moved_out_date_1': '8',
        'moved_out_date_2': '2002'
    }

    def test_invalid_when_all_data_is_blank(self):
        data = {
            'street_line1': '',
            'street_line2': '',
            'town': '',
            'county': '',
            'postcode': '',
            'moved_in_date_0': '',
            'moved_in_date_1': '',
            'moved_in_date_2': '',
            'moved_out_date_0': '',
            'moved_out_date_1': '',
            'moved_out_date_2': '',
        }
        form = self.form(data)

        self.assertFalse(form.is_valid())

        # Check error messages
        self.assertEqual(form.errors, {
            'street_line1': [self.ERROR_MESSAGE_STREET_LINE_1_BLANK],
            'town': [self.ERROR_MESSAGE_TOWN_BLANK],
            'postcode': [self.ERROR_MESSAGE_POSTCODE_BLANK],
            'moved_in_date': [self.ERROR_MESSAGE_DATE_BLANK],
            'moved_out_date': [self.ERROR_MESSAGE_DATE_BLANK],
        })

    def test_invalid_when_moved_in_or_moved_out_day_too_large(self):
        data = {
            'moved_in_date_0': '32',
            'moved_in_date_1': '12',
            'moved_in_date_2': '2018',
            'moved_out_date_0': '33',
            'moved_out_date_1': '11',
            'moved_out_date_2': '2018',
        }
        data.update(self.VALID_ADDRESS_DATA)

        form = self.form(data)

        self.assertFalse(form.is_valid())

        # Check error messages
        self.assertEqual(form.errors, {
            'moved_in_date': [self.ERROR_MESSAGE_DAY_OUT_OF_RANGE],
            'moved_out_date': [self.ERROR_MESSAGE_DAY_OUT_OF_RANGE]
        })

    def test_invalid_when_moved_in_or_moved_out_day_too_small(self):
        data = {
            'moved_in_date_0': '0',
            'moved_in_date_1': '9',
            'moved_in_date_2': '2018',
            'moved_out_date_0': '0',
            'moved_out_date_1': '11',
            'moved_out_date_2': '2018',
        }
        form = self.form(data)
        data.update(self.VALID_ADDRESS_DATA)

        self.assertFalse(form.is_valid())

        # Check error messages
        self.assertEqual(form.errors, {
            'moved_in_date': [self.ERROR_MESSAGE_DAY_OUT_OF_RANGE],
            'moved_out_date': [self.ERROR_MESSAGE_DAY_OUT_OF_RANGE]
        })

    def test_invalid_if_moved_in_or_moved_out_month_too_large(self):
        data = {
            'moved_in_date_0': '1',
            'moved_in_date_1': '13',
            'moved_in_date_2': '2018',
            'moved_out_date_0': '2',
            'moved_out_date_1': '14',
            'moved_out_date_2': '2018',
        }
        form = self.form(data)
        data.update(self.VALID_ADDRESS_DATA)

        self.assertFalse(form.is_valid())

        # Check error messages
        self.assertEqual(form.errors, {
            'moved_in_date': [self.ERROR_MESSAGE_MONTH_OUT_OF_RANGE],
            'moved_out_date': [self.ERROR_MESSAGE_MONTH_OUT_OF_RANGE]
        })

    def test_invalid_if_moved_in_or_moved_out_month_too_small(self):
        data = {
            'moved_in_date_0': '1',
            'moved_in_date_1': '0',
            'moved_in_date_2': '2018',
            'moved_out_date_0': '2',
            'moved_out_date_1': '0',
            'moved_out_date_2': '2018',
        }
        form = self.form(data)
        data.update(self.VALID_ADDRESS_DATA)

        self.assertFalse(form.is_valid())

        # Check error messages
        self.assertEqual(form.errors, {
            'moved_in_date': [self.ERROR_MESSAGE_MONTH_OUT_OF_RANGE],
            'moved_out_date': [self.ERROR_MESSAGE_MONTH_OUT_OF_RANGE]
        })

    def test_invalid_if_moved_in_or_moved_out_year_before_1900(self):
        data = {
            'moved_in_date_0': '1',
            'moved_in_date_1': '8',
            'moved_in_date_2': '1888',
            'moved_out_date_0': '2',
            'moved_out_date_1': '10',
            'moved_out_date_2': '1889',
        }
        form = self.form(data)
        data.update(self.VALID_ADDRESS_DATA)

        self.assertFalse(form.is_valid())

        # Check error messages
        self.assertEqual(form.errors, {
            'moved_in_date': [self.ERROR_MESSAGE_MOVED_IN_YEAR_BEFORE_1900],
            'moved_out_date': [self.ERROR_MESSAGE_MOVED_OUT_YEAR_BEFORE_1900]
        })

    def test_invalid_if_moved_in_or_moved_out_year_less_than_4_digits(self):
        data = {
            'moved_in_date_0': '1',
            'moved_in_date_1': '8',
            'moved_in_date_2': '199',
            'moved_out_date_0': '2',
            'moved_out_date_1': '10',
            'moved_out_date_2': '18',
        }
        form = self.form(data)
        data.update(self.VALID_ADDRESS_DATA)

        self.assertFalse(form.is_valid())

        # Check error messages
        self.assertEqual(form.errors, {
            'moved_in_date': [self.ERROR_MESSAGE_YEAR_LESS_THAN_4_DIGITS],
            'moved_out_date': [self.ERROR_MESSAGE_YEAR_LESS_THAN_4_DIGITS],
        })

    def test_invalid_if_moved_in_or_moved_out_date_is_not_a_real_date(self):
        data = {
            'moved_in_date_0': '31',  # Only 30 days in June
            'moved_in_date_1': '6',
            'moved_in_date_2': '2017',
            'moved_out_date_0': '29',  # 1999 wasn't a leap year
            'moved_out_date_1': '2',
            'moved_out_date_2': '1999',
        }
        form = self.form(data)
        data.update(self.VALID_ADDRESS_DATA)

        self.assertFalse(form.is_valid())

        # Check error messages
        self.assertEqual(form.errors, {
            'moved_in_date': [self.ERROR_MESSAGE_INVALID_DATE],
            'moved_out_date': [self.ERROR_MESSAGE_INVALID_DATE],
        })

    def test_invalid_if_moved_in_or_moved_out_date_contains_non_numeric_data(self):
        data = {
            'moved_in_date_0': '16',
            'moved_in_date_1': 'H',
            'moved_in_date_2': '2017',
            'moved_out_date_0': '!!',
            'moved_out_date_1': '3',
            'moved_out_date_2': '20XX',
        }
        form = self.form(data)
        data.update(self.VALID_ADDRESS_DATA)

        self.assertFalse(form.is_valid())

        # Check error messages
        self.assertEqual(form.errors, {
            'moved_in_date': [self.ERROR_MESSAGE_NON_NUMERIC],
            'moved_out_date': [self.ERROR_MESSAGE_NON_NUMERIC],
        })

    class MockDate(datetime.date):
        @classmethod
        def today(cls):
            return datetime.date(2018, 12, 14)

    @patch('datetime.date', MockDate)
    def test_invalid_if_moved_in_date_after_current_date(self):
        data = {
            'moved_in_date_0': '15',
            'moved_in_date_1': '12',
            'moved_in_date_2': '2018',
            'moved_out_date_0': '1',
            'moved_out_date_1': '11',
            'moved_out_date_2': '2017',
        }
        form = self.form(data)
        data.update(self.VALID_ADDRESS_DATA)

        self.assertFalse(form.is_valid())

        # Check error messages
        self.assertEqual(form.errors, {
            'moved_in_date': [self.ERROR_MESSAGE_MOVED_IN_DATE_AFTER_CURRENT_DATE],
        })

    @patch('datetime.date', MockDate)
    def test_invalid_if_moved_out_date_after_current_date(self):
        data = {
            'moved_in_date_0': '21',
            'moved_in_date_1': '6',
            'moved_in_date_2': '2017',
            'moved_out_date_0': '15',
            'moved_out_date_1': '12',
            'moved_out_date_2': '2018',
        }
        form = self.form(data)
        data.update(self.VALID_ADDRESS_DATA)

        self.assertFalse(form.is_valid())

        # Check error messages
        self.assertEqual(form.errors, {
            'moved_out_date': [self.ERROR_MESSAGE_MOVED_OUT_DATE_AFTER_CURRENT_DATE],
        })

    def test_invalid_if_moved_in_date_after_moved_out_date(self):
        data = {
            'moved_in_date_0': '21',
            'moved_in_date_1': '6',
            'moved_in_date_2': '2017',
            'moved_out_date_0': '15',
            'moved_out_date_1': '12',
            'moved_out_date_2': '2016',
        }
        form = self.form(data)
        data.update(self.VALID_ADDRESS_DATA)

        self.assertFalse(form.is_valid())

        # Check error messages
        self.assertEqual(form.errors, {
            'moved_in_date': [self.ERROR_MESSAGE_MOVED_IN_DATE_AFTER_MOVED_OUT_DATE],
            'moved_out_date': [self.ERROR_MESSAGE_MOVED_OUT_DATE_BEFORE_MOVED_IN_DATE],
        })

    def test_valid_data(self):
        data = {}
        data.update(self.VALID_ADDRESS_DATA)
        data.update(self.VALID_MOVED_IN_AND_OUT_DATE_DATA)

        form = self.form(data)

        self.assertTrue(form.is_valid())
