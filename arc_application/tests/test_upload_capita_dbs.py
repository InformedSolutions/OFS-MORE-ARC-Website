from arc_application.forms import UploadCapitaDBSForm

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.forms import ValidationError
from django.test import SimpleTestCase, TestCase
from django.urls import reverse


class UploadCapitaDBSRoutingTests(TestCase):
    def setUp(self):
        # Create ARC user and login.
        self.arc_user = User.objects.create_user(
            username='governor_tARCin',
            email='test@test.com',
            password='my_secret'
        )

        g = Group.objects.create(name=settings.ARC_GROUP)
        g.user_set.add(self.arc_user)

        self.client.login(username='governor_tARCin', password='my_secret')

    def test_can_render_capita_dbs_list_upload_page(self):
        response = self.client.get(reverse('Upload-Capita-DBS'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='upload-capita-dbs.html')

    def test_page_loads_with_date_and_filename_of_previous_upload(self):
        self.skipTest('FunctionalityNotImplemented')

    def test_can_post_valid_csv_file(self):
        self.skipTest('FunctionalityNotImplemented')

    def test_post_request_to_dbs_api_made_for_valid_csv_upload(self):
        self.skipTest('FunctionalityNotImplemented')

    def test_cc_user_cannot_see_nav_bar_link(self):
        self.skipTest('testNotImplemented')

    def test_cc_user_accessing_capita_dbs_list_upload_page_raises_access_denied(self):
        self.skipTest('FunctionalityNotImplemented')


class UploadCapitaDBSHelperFunctionTests(SimpleTestCase):
    def test_formatting_of_previous_upload_information(self):
        self.skipTest('FunctionalityNotImplemented')


class UploadCapitaDBSFormTests(SimpleTestCase):
    def test_no_file_selected_raises_error(self):
        form = UploadCapitaDBSForm(data={'capita_list_file': None})

        with self.assertRaisesMessage(ValidationError, 'No file chosen'):
            form.clean_capita_list_file()

    def test_invalid_file_extension_raises_error(self):
        form = UploadCapitaDBSForm(data={'capita_list_file': 'myfile.png'})

        with self.assertRaisesMessage(ValidationError, 'The file must be .csv or .xlxs'):
            form.clean_capita_list_file()

    def test_xlxs_file_passes_validation(self):
        form = UploadCapitaDBSForm(data={'capita_list_file': 'myfile.xlxs'})

        self.assertTrue(form.is_valid())

    def test_csv_file_passes_validation(self):
        form = UploadCapitaDBSForm(data={'capita_list_file': 'myfile.csv'})

        self.assertTrue(form.is_valid())