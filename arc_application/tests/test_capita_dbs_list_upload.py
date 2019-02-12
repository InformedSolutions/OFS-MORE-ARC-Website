from django.test import SimpleTestCase, TestCase


class CapitaDBSListUploadFunctionalTests(TestCase):
    def test_can_render_capita_dbs_list_upload_page(self):
        self.skipTest('FunctionalityNotImplemented')

    def test_page_loads_with_date_and_filename_of_previous_upload(self):
        self.skipTest('FunctionalityNotImplemented')

    def test_formatting_of_previous_upload_information(self):
        self.skipTest('FunctionalityNotImplemented')

    def test_can_post_valid_csv_file(self):
        self.skipTest('FunctionalityNotImplemented')

    def test_post_request_to_dbs_api_made_for_valid_csv_upload(self):
        self.skipTest('FunctionalityNotImplemented')

    def test_cc_user_cannot_see_nav_bar_link(self):
        self.skipTest('FunctionalityNotImplemented')

    def test_cc_user_accessing_capita_dbs_list_upload_page_raises_access_denied(self):
        self.skipTest('FunctionalityNotImplemented')


class CapitaDBSListUploadFormTests(SimpleTestCase):
    def test_no_file_selected_raises_error(self):
        self.skipTest('FunctionalityNotImplemented')

    def test_invalid_file_upload_raises_error(self):
        self.skipTest('FunctionalityNotImplemented')

    def test_valid_file_upload_passes_validation(self):
        self.skipTest('FunctionalityNotImplemented')
