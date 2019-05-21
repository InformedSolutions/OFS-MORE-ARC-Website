from unittest import TestCase
from django.test import tag


@tag('http')
class NannyAuditLogFunctionalTests(TestCase):

    def test_can_render_audit_log_page_as_arc_user(self):
        self.skipTest('testNotImplemented')

    def test_can_render_audit_log_page_as_cc_user(self):
        self.skipTest('testNotImplemented')

    def test_get_request_to_audit_log_page_as_cc_user_creates_timeline_log(self):
        self.skipTest('testNotImplemented')

    def test_returning_application_creates_timeline_log(self):
        self.skipTest('testNotImplemented')

    def test_accepting_application_creates_timeline_log(self):
        self.skipTest('testNotImplemented')

    def test_assigning_application_creates_timeline_log(self):
        self.skipTest('testNotImplemented')

    def test_releasing_application_creates_timeline_log(self):
        self.skipTest('testNotImplemented')

    def test_adding_arc_comment_to_personal_details_creates_timeline_log(self):
        self.skipTest('testNotImplemented')

    def test_adding_arc_comment_to_first_aid_training_creates_timeline_log(self):
        self.skipTest('testNotImplemented')

    def test_adding_arc_comment_to_childcare_training_creates_timeline_log(self):
        self.skipTest('testNotImplemented')

    def test_adding_arc_comment_to_dbs_checks_creates_timeline_log(self):
        self.skipTest('testNotImplemented')

    def test_adding_arc_comment_to_insurance_cover_creates_timeline_log(self):
        self.skipTest('testNotImplemented')

    def test_duplicate_log_not_added_if_preexisting_arc_comment(self):
        self.skipTest('testNotImplemented')
