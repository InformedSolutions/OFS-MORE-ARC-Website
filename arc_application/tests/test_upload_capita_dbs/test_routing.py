import json
from unittest import mock

from ...models import CapitaDBSFile
from ...services import dbs_api
from ...views.base import custom_login
from ...views import __handle_file_upload

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.http import HttpResponse
from django.test import TestCase
from django.urls import resolve, reverse


handle_file_upload = __handle_file_upload


@mock.patch.object(dbs_api, 'batch_overwrite', return_value=HttpResponse(status=201))
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

        CapitaDBSFile.objects.create(id=1, filename='initial-filename.csv', date_uploaded='2019-01-01')

    def test_can_render_capita_dbs_list_upload_page(self, dbs_api_mock):
        response = self.client.get(reverse('Upload-Capita-DBS'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='upload-capita-dbs.html')

    def test_page_loads_with_date_and_filename_of_previous_upload(self, dbs_api_mock):
        response = self.client.get(reverse('Upload-Capita-DBS'))

        self.assertContains(response, 'initial-filename.csv (01/01/2019)')

    def test_post_request_to_dbs_api_made_for_valid_csv_upload(self, dbs_api_mock):
        with open('arc_application/tests/resources/test_csv.csv') as csv_file:
            self.client.post(reverse('Upload-Capita-DBS'), {'capita_list_file': csv_file})

        csv_file.close()

        self.assertTrue(dbs_api_mock.called)

    def test_post_request_to_dbs_api_made_for_valid_csvx_upload(self, dbs_api_mock):
        with open('arc_application/tests/resources/test_csvx.csvx') as csvx_file:
            self.client.post(reverse('Upload-Capita-DBS'), {'capita_list_file': csvx_file})

        csvx_file.close()

        self.assertTrue(dbs_api_mock.called)

    def test_cc_user_cannot_see_nav_bar_link(self, dbs_api_mock):
        self.skipTest('testNotImplemented')

    def test_cc_user_accessing_capita_dbs_list_upload_page_raises_access_denied(self, dbs_api_mock):
        self.skipTest('FunctionalityNotImplemented')

    def test_unauthenticated_user_cannot_access_capita_dbs_upload_page(self, dbs_api_mock):
        self.client.logout()

        response = self.client.get(reverse('Upload-Capita-DBS'))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(resolve(response.url).func, custom_login)

    def test_error_added_to_form_if_400_status_code_from_dbs_api(self, dbs_api_mock):
        dbs_api_mock.return_value.status_code = 400
        dbs_api_mock.return_value.text = json.dumps('Test error message')

        with open('arc_application/tests/resources/test_csv.csv') as csv_file:
            response = self.client.post(reverse('Upload-Capita-DBS'), {'capita_list_file': csv_file})

        csv_file.close()

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', field='capita_list_file',
                             errors='There was an error with the file you tried to upload. '
                             'Check the file and try again')

    def test_error_added_to_form_if_not_400_or_201_status_code_from_dbs_api(self, dbs_api_mock):
        dbs_api_mock.return_value.status_code = 500
        dbs_api_mock.return_value.text = json.dumps('Test error message')

        with open('arc_application/tests/resources/test_csv.csv') as csv_file:
            response = self.client.post(reverse('Upload-Capita-DBS'), {'capita_list_file': csv_file})

        csv_file.close()

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', field='capita_list_file',
                             errors='We couldn\'t upload your new list. Try again')


