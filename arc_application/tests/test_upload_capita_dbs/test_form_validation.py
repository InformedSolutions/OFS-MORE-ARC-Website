from django.test import SimpleTestCase, RequestFactory


class UploadCapitaDBSFormTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_no_file_selected_raises_error(self):
        self.skipTest('testNotImplemented')

    def test_invalid_file_extension_raises_error(self):
        self.skipTest('testNotImplemented')

    def test_csvx_file_passes_validation(self):
        self.skipTest('testNotImplemented')

    def test_csv_file_passes_validation(self):
        self.skipTest('testNotImplemented')