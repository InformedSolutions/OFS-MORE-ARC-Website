
from django.test import TestCase, tag
from django.urls import reverse

from arc_application.models import Arc, Application
from arc_application.tests.utils import create_childminder_application, create_arc_user


@tag('http')
class LoginFunctionalTests(TestCase):

    def setUp(self):
        self.test_arc_user = create_arc_user()

    def test_login_redirect(self):
        self.client.login(username='arc_test', password='my_secret')
        resp = self.client.get('/arc/login/')
        self.assertEqual(resp.url, '/arc/summary')
        self.assertEqual(resp.status_code, 302)

    def test_task_login_details(self):
        # Assemble
        application = create_childminder_application(self.test_arc_user.pk)

        post_dictionary = {
            'id': application.application_id,
        }

        # Act
        self.client.login(username='arc_test', password='my_secret')

        response = self.client.post(reverse('contact_summary'), post_dictionary)

        # Assert

        # 1. Check HTTP status code correct
        self.assertEqual(response.status_code, 302)

        # 2. Ensure overall task status marked as FLAGGED in ARC view
        reloaded_arc_record = Arc.objects.get(pk=application.application_id)
        self.assertEqual(reloaded_arc_record.login_details_review, 'COMPLETED')

        # 2. Check flagged boolean indicator is set on the application record
        reloaded_application = Application.objects.get(pk=application.application_id)
        self.assertTrue(not reloaded_application.login_details_arc_flagged)
