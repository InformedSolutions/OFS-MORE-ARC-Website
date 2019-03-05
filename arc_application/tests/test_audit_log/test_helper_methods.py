from unittest import mock, TestCase

from django.test import RequestFactory

from arc_application.views.audit_log import audit_log_dispatcher, ChildminderAuditlog, NannyAuditLog


class AuditLogDispatcherUnitTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.factory = RequestFactory()

    @mock.patch.object(ChildminderAuditlog, 'dispatch')
    def test_app_type_childminder_returns_childminder_audit_log(self, dispatch):
        request = self.factory.get('arc/auditlog/?app_type=Childminder')
        audit_log_dispatcher(request)

        self.assertTrue(dispatch.called_with(request))

    def test_incorrect_app_type_raises_value_error(self):
        request = self.factory.get('arc/auditlog/?app_type=Neither')

        with self.assertRaises(ValueError):
            audit_log_dispatcher(request)

    def test_app_type_none_raises_key_error(self):
        request = self.factory.get('arc/auditlog/')

        with self.assertRaises(KeyError):
            audit_log_dispatcher(request)
