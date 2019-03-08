from django.test import TestCase, tag

from ..utils import create_childminder_application, create_arc_user

# TODO: Import these error messages from the form, or remove this todo.
ERROR_MESSAGE_BLANK = 'Enter the date, including the month and year'
ERROR_MESSAGE_DAY_OUT_OF_RANGE = 'Day must be between 1 and 31'
ERROR_MESSAGE_MONTH_OUT_OF_RANGE = 'Month must be between 1 and 12'
ERROR_MESSAGE_YEAR_BEFORE_1900 = 'Start date must be after 1900'
ERROR_MESSAGE_YEAR_LESS_THAN_4_DIGITS = 'Enter the whole year (4 digits)'
ERROR_MESSAGE_INVALID_DATE = 'Enter a real date'
ERROR_MESSAGE_NON_NUMERIC = 'Use numbers for the date'

ERROR_MESSAGE_START_DATE_AFTER_CURRENT_DATE = 'Start date must be today or in the past'
ERROR_MESSAGE_START_DATE_AFTER_END_DATE = 'Start date must be before the end date'

ERROR_MESSAGE_END_DATE_AFTER_CURRENT_DATE = 'End date must be before today or in the past'
ERROR_MESSAGE_END_DATE_BEFORE_START_DATE = 'End date must be after the start date'


@tag('unit')
class ReviewPersonalDetailsPreviousNamesFormValidationTests(TestCase):
    # TODO: Import and set the relevant form to this value
    form = None

    def setUp(self):
        self.arc_user = create_arc_user()
        self.application = create_childminder_application(self.arc_user.pk)
        self.client.login(username='arc_test', password='my_secret')

    def test_blank_data(self):
        data = {}  # TODO: Data depends on implementation
        form = self.form(data)

        self.assertFalse(form.is_valid())

        # Check error messages
        self.assertEqual(form.errors, {
            'start_date': ERROR_MESSAGE_BLANK,
            'end_date': 'Enter the date, including the month and year'
        })
        # TODO: start_date and end_date may not be field names

    def test_day_out_of_range(self):
        data = {}
        form = self.form(data)

        self.assertFalse(form.is_valid())

        # Check error messages
        self.assertEqual(form.errors, {
            'start_date': ERROR_MESSAGE_DAY_OUT_OF_RANGE,
            'end_date': ERROR_MESSAGE_DAY_OUT_OF_RANGE
        })
        # TODO: start_date and end_date may not be field names

    def test_month_out_of_range(self):
        data = {}
        form = self.form(data)

        self.assertFalse(form.is_valid())

        # Check error messages
        self.assertEqual(form.errors, {
            'start_date': ERROR_MESSAGE_MONTH_OUT_OF_RANGE,
            'end_date': ERROR_MESSAGE_MONTH_OUT_OF_RANGE
        })
        # TODO: start_date and end_date may not be field names

    def test_year_before_1900(self):
        self.skipTest('functionalityNotImplemented')

    def test_year_less_than_4_digits(self):
        self.skipTest('functionalityNotImplemented')

    def test_invalid_date(self):
        self.skipTest('functionalityNotImplemented')

    def test_non_numeric_date(self):
        self.skipTest('functionalityNotImplemented')

    def test_start_date_after_current_date(self):
        self.skipTest('functionalityNotImplemented')

    def test_end_date_after_current_date(self):
        self.skipTest('functionalityNotImplemented')

    def test_start_date_after_end_date(self):
        self.skipTest('functionalityNotImplemented')
