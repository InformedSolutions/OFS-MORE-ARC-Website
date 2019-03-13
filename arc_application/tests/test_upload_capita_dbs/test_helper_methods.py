import json
from unittest import mock

from django.core.exceptions import ValidationError
from django.db import InternalError
from django.http import HttpResponse
from django.test import SimpleTestCase, RequestFactory
from django.urls import reverse

from ...views import __handle_file_upload
from ...services import dbs_api


handle_file_upload = __handle_file_upload


@mock.patch.object(dbs_api, 'batch_overwrite', return_value=HttpResponse(status=201))
class UploadCapitaDBSHelperFunctionTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_formatting_of_previous_upload_information(self, dbs_api_mock):
        self.skipTest('testNotImplemented')

    def test_validation_error_raised_if_400_status_code_from_dbs_api(self, dbs_api_mock):
        dbs_api_mock.return_value.status_code = 400
        dbs_api_mock.return_value.text = json.dumps('Test error message')

        with open('arc_application/tests/resources/test_csv.csv') as csv_file:
            request = self.factory.post(reverse('Upload-Capita-DBS'), {'capita_list_file': csv_file})
            request_files = request.FILES

        csv_file.close()

        with self.assertRaisesMessage(ValidationError, 'Test error message'):
            handle_file_upload(request_files)

    def test_internal_error_raised_if_not_201_or_400_status_code_from_dbs_api(self, dbs_api_mock):
        dbs_api_mock.return_value.status_code = 500
        dbs_api_mock.return_value.text = json.dumps('Test error message')

        with open('arc_application/tests/resources/test_csv.csv') as csv_file:
            request = self.factory.post(reverse('Upload-Capita-DBS'), {'capita_list_file': csv_file})
            request_files = request.FILES

        csv_file.close()

        with self.assertRaisesMessage(InternalError, 'The DBS API returned a 500 status code. Response text: Test error message'):
            handle_file_upload(request_files)

    def test_no_error_raised_if_201_status_code_from_dbs_api(self, dbs_api_mock):
        dbs_api_mock.return_value.status_code = 201

        with open('arc_application/tests/resources/test_csv.csv') as csv_file:
            request = self.factory.post(reverse('Upload-Capita-DBS'), {'capita_list_file': csv_file})
            request_files = request.FILES

        csv_file.close()

        x = handle_file_upload(request_files)

        self.assertEqual(x, None)