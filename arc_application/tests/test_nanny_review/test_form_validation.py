from unittest import skipUnless

from django.conf import settings
from django.test import TestCase, tag

from ...forms.nanny_forms.nanny_form_builder import NannyFormBuilder


@tag('unit')
@skipUnless(settings.ENABLE_NANNIES, 'Skipping test as Nanny feature toggle equated to False')
class NannyFormBuilderTests(TestCase):
    form = None

    ERROR_MESSAGE_BLANK_COMMENT = 'You must give reasons'
    ERROR_MESSAGE_OVER_500_CHARACTERS = ''  # The field itself limits the user to entering 500 characters, no error message

    def setUp(self):
        self.form = self.create_form()

    def create_form(self):
        """
        Creates a form using the NannyFormBuilder
        """
        example_fields = [
            'field_1',
            'field_2',
        ]

        return NannyFormBuilder(example_fields, api_endpoint_name='fake-endpoint').create_form()

    def test_valid_enter_empty_data(self):
        data = {}

        form = self.form(data)

        self.assertTrue(form.is_valid())

    def test_valid_enter_blank_data(self):
        data = {
            'field_1_declare': None,
            'field_1_comments': '',
            'field_2_declare': None,
            'field_2_comments': '',
        }

        form = self.form(data)

        self.assertTrue(form.is_valid())

    def test_valid_enter_false_declare_with_no_comment_data(self):
        data = {
            'field_1_declare': False,
            'field_1_comments': '',
            'field_2_declare': False,
            'field_2_comments': '',
        }

        form = self.form(data)

        self.assertTrue(form.is_valid())

    def test_valid_enter_false_declare_with_comment_data(self):
        data = {
            'field_1_declare': False,
            'field_1_comments': 'Some Comment',
            'field_2_declare': False,
            'field_2_comments': 'Some Other Comment 123',
        }

        form = self.form(data)

        self.assertTrue(form.is_valid())

    def test_invalid_enter_true_declare_with_no_comment_data(self):
        data = {
            'field_1_declare': True,
            'field_1_comments': '',
            'field_2_declare': True,
            'field_2_comments': '',
        }

        form = self.form(data)

        self.assertFalse(form.is_valid())

    def test_valid_enter_true_declare_with_comment_data(self):
        data = {
            'field_1_declare': True,
            'field_1_comments': 'Some Comment',
            'field_2_declare': True,
            'field_2_comments': 'Some Other Valid Comment :)',
        }

        form = self.form(data)

        self.assertTrue(form.is_valid())

    def test_invalid_enter_true_declare_with_comments_over_500_characters_data(self):
        data = {
            'field_1_declare': True,
            'field_1_comments': '1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890'
                                '1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890'
                                '1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890'
                                '1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890'
                                '1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890'
                                '1',
            'field_2_declare': True,
            'field_2_comments': 'XOX',
        }

        form = self.form(data)

        self.assertFalse(form.is_valid())

    def test_valid_enter_true_declare_with_comments_is_500_characters_data(self):
        data = {
            'field_1_declare': True,
            'field_1_comments': '1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890'
                                '1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890'
                                '1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890'
                                '1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890'
                                '1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890',
            'field_2_declare': True,
            'field_2_comments': 'XOX',
        }

        form = self.form(data)

        self.assertTrue(form.is_valid())
