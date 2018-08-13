from unittest import mock

from django.conf import settings
from django.forms import Form
from django.contrib.auth.models import Group, User
from django.http import HttpResponse
from django.test import tag, TestCase
from django.urls import reverse

from arc_application.models import Arc
from arc_application.forms.nanny_forms.nanny_form_builder import NannyFormBuilder
from arc_application.services.application_handler import NannyApplicationHandler
from arc_application.views.nanny_views.nanny_dbs_check import NannyDbsCheckSummary
from arc_application.views.nanny_views.nanny_arc_summary import NannyArcSummary


mock_nanny_application = {
    'application_status': 'SUBMITTED',
    'application_id': '998fd8ec-b96b-4a71-a1a1-a7a3ae186729',
    'date_submitted': '2018-07-31 17:20:46.011717+00',
    'date_updated': '2018-07-31 17:20:46.011717+00',
}

mock_personal_details_record = {
    'first_name': 'The Dark Lord',
    'last_name': 'Selenium',
}


nanny_application_response = HttpResponse()
nanny_application_response.status_code = 200
nanny_application_response.record = mock_nanny_application

personal_details_response = HttpResponse()
personal_details_response.status_code = 200
personal_details_response.record = mock_personal_details_record


mock_endpoint_return_values = {
    'application': nanny_application_response,
    'applicant-personal-details': personal_details_response,
}


def side_effect(endpoint_name, *args, **kwargs):
    return mock_endpoint_return_values[endpoint_name]


class ArcUserSummaryPageTests(TestCase):
    """
    Test suite for the functionality within the ARC summary page.
    """
    def setUp(self):
        self.user = User.objects.create_user(
            username='governor_tARCin',
            email='test@test.com',
            password='my_secret'
        )
        g = Group.objects.create(name=settings.ARC_GROUP)
        g.user_set.add(self.user)

        global arc_test_user
        arc_test_user = self.user

        self.client.login(username='governor_tARCin', password='my_secret')

    # ----------------- #
    # Integration tests #
    # ----------------- #

    @tag('integration')
    def test_if_field_flagged_then_task_status_is_flagged(self):
        pass

    @tag('integration')
    def test_if_nothing_flagged_then_task_status_is_done(self):
        pass

    # ---------- #
    # HTTP tests #
    # ---------- #

    def test_can_render_sign_in_details_page(self):
        """
        Test to ensure that the page for flagging sign in details can be rendered.
        """
        response = self.client.get(reverse('nanny_contact_summary'))

        self.assertEqual(response.status_code, 200)
        # self.assertEqual(response.resolver_match.func.__name__, ARCUserSummaryView.as_view().__name__)

    def test_can_render_personal_details_page(self):
        """
        Test to ensure that the page for flagging personal details can be rendered.
        """
        response = self.client.get(reverse('nanny_personal_details_summary'))

        self.assertEqual(response.status_code, 200)

    def test_can_render_childcare_address_details_page(self):
        """
        Test to ensure that the page for flagging childcare address details can be rendered.
        """
        response = self.client.get(reverse('nanny_childcare_address_summary'))

        self.assertEqual(response.status_code, 200)

    def test_can_render_first_aid_details_page(self):
        """
        Test to ensure that the page for flagging first aid details can be rendered.
        """
        response = self.client.get(reverse('nanny_first_aid_training_summary'))

        self.assertEqual(response.status_code, 200)

    def test_can_render_childcare_training_details_page(self):
        """
        Test to ensure that the page for flagging childcare training details can be rendered.
        """
        response = self.client.get(reverse('nanny_childcare_training_summary'))

        self.assertEqual(response.status_code, 200)

    def test_can_render_criminal_record_details_page(self):
        """
        Test to ensure that the page for flagging dbs certificate details can be rendered.
        """
        response = self.client.get(reverse('nanny_dbs_summary'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__, NannyDbsCheckSummary.as_view().__name__)

    def test_can_render_insurance_cover_details_page(self):
        """
        Test to ensure that the page for flagging insurance cover details can be rendered.
        """
        response = self.client.get(reverse('nanny_insurance_cover_summary'))

        self.assertEqual(response.status_code, 200)

    def test_continue_complete_review_button_appears_only_if_all_tasks_reviewed(self):
        """
        Test to ensure that the 'Complete Review' button is only present if all tasks are either 'Reviewed'
        or 'Flagged'.
        """
        pass

    def test_sign_in_details_redirects_to_personal_details(self):
        """
        Test that a POST request to the sign in details page redirects to the personal details page.
        """
        pass

    def test_personal_details_redirects_to_the_childcare_address_page(self):
        """
        Test that a POST request to the personal details page redirects to the childcare address details page.
        """
        pass

    def test_childcare_address_details_redirects_to_the_first_aid_page(self):
        """
        Test that a POST request to the childcare address details page redirects to the first aid details page.
        """
        pass

    def test_first_aid_details_redirects_to_the_childcare_training_page(self):
        """
        Test that a POST request to the first aid details page redirects to the childcare training details page.
        """
        pass

    def test_childcare_training_redirects_to_the_criminal_record_page(self):
        """
        Test that a POST request to the childcare training details page redirects to the criminal record details page.
        """
        pass

    def test_criminal_record_redirects_to_the_insurance_cover_page(self):
        """
        Test that a POST request to the criminal record page redirects to the insurance cover details page.
        """
        pass

    def test_insurance_cover_details_redirects_to_the_task_list_page(self):
        """
        Test that a POST request to the insurance cover page redirects to the task list page.
        """
        pass

    def test_can_flag_personal_details(self):
        """
        Test to ensure that personal details can be flagged.
        """
        pass

    def test_can_flag_childcare_address_details(self):
        """
        Test to ensure that childcare address details can be flagged.
        """
        # TODO - Write test once work commences on flagging Childcare Address details.
        pass

    def test_can_flag_first_aid_details(self):
        """
        Test to ensure that first aid details can be flagged.
        """
        pass

    def test_can_flag_childcare_training_details(self):
        """
        Test to ensure that childcare training details can be flagged.
        """
        pass

    def test_can_flag_criminal_record_details(self):
        """
        Test to ensure that dbs certificate details can be flagged.
        """
        pass

    def test_insurance_cover_details_can_be_flagged(self):
        """
        Test to ensure that insurance cover details can be flagged.
        """
        pass

    def test_can_render_arc_summary_page(self):
        """
        Test to ensure that the Nanny ARC summary page can be rendered.
        """
        response = self.client.get(reverse('nanny_arc_summary'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__, NannyArcSummary.as_view().__name__)

    def test_can_remove_previously_added_arc_comment(self):
        """
        Test to ensure that an ARC user who had previously flagged and commented on a field can later remove that
        comment.
        """
        # TODO - figure out precisely how to test this.
        pass

    # ---------- #
    # UNIT tests #
    # ---------- #

    @tag('unit')
    def test_form_view_builder(self):
        pass

    @tag('unit')
    def test_form_builder(self):
        """
        Test to assert that the form_builder functions as expected.
        """
        dbs_check_fields = [
            'dbs_number',
            'convictions',
        ]

        form = NannyFormBuilder(dbs_check_fields).create_form()

        self.assertIsInstance(form, Form)
        # TODO - assert each field above has _declare and _comments field in form.
