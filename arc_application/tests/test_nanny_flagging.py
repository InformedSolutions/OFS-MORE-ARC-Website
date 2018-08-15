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
from arc_application.services.db_gateways import NannyGatewayActions
from arc_application.views import NannyDbsCheckSummary, NannyArcSummary, NannyContactDetailsSummary, \
    NannyPersonalDetailsSummary, NannyChildcareAddressSummary, NannyFirstAidTrainingSummary,\
    NannyChildcareTrainingSummary, NannyInsuranceCoverSummary, NannyTaskList

from .test_utils import side_effect


test_app_id = side_effect('application').record['application_id']


@mock.patch('arc_application.services.db_gateways.NannyGatewayActions.read', side_effect=side_effect)
@mock.patch('arc_application.services.db_gateways.NannyGatewayActions.list', side_effect=side_effect)
@mock.patch('arc_application.services.db_gateways.NannyGatewayActions.patch', side_effect=side_effect)
@mock.patch('arc_application.services.db_gateways.NannyGatewayActions.create', side_effect=side_effect)
@mock.patch('arc_application.services.db_gateways.IdentityGatewayActions.read', side_effect=side_effect)
class ArcUserSummaryPageTests(TestCase):  # , metaclass=MockedGatewayTests):
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

    @classmethod
    def setUpTestData(cls):
        Arc.objects.create(application_id=test_app_id)

    # ----------------- #
    # Integration tests #
    # ----------------- #

    @tag('integration')
    def test_if_field_flagged_then_task_status_is_flagged(self, *args):
        pass

    @tag('integration')
    def test_if_nothing_flagged_then_task_status_is_done(self, *args):
        pass

    # ---------- #
    # HTTP tests #
    # ---------- #

    def test_can_render_sign_in_details_page(self, *args):
        """
        Test to ensure that the page for flagging sign in details can be rendered.
        """
        response = self.client.get(reverse('nanny_contact_summary') + '?id=' + test_app_id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__, NannyContactDetailsSummary.as_view().__name__)

    def test_can_render_personal_details_page(self, *args):
        """
        Test to ensure that the page for flagging personal details can be rendered.
        """
        response = self.client.get(reverse('nanny_personal_details_summary') + '?id=' + test_app_id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__, NannyPersonalDetailsSummary.as_view().__name__)

    def test_can_render_childcare_address_details_page(self, *args):
        """
        Test to ensure that the page for flagging childcare address details can be rendered.
        """
        response = self.client.get(reverse('nanny_childcare_address_summary') + '?id=' + test_app_id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__, NannyChildcareAddressSummary.as_view().__name__)

    def test_can_render_first_aid_details_page(self, *args):
        """
        Test to ensure that the page for flagging first aid details can be rendered.
        """
        response = self.client.get(reverse('nanny_first_aid_training_summary') + '?id=' + test_app_id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__, NannyFirstAidTrainingSummary.as_view().__name__)

    def test_can_render_childcare_training_details_page(self, *args):
        """
        Test to ensure that the page for flagging childcare training details can be rendered.
        """
        response = self.client.get(reverse('nanny_childcare_training_summary') + '?id=' + test_app_id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__, NannyChildcareTrainingSummary.as_view().__name__)

    @tag('http')
    def test_can_render_criminal_record_details_page(self, *args):
        """
        Test to ensure that the page for flagging dbs certificate details can be rendered.
        """
        response = self.client.get(reverse('nanny_dbs_summary') + '?id=' + test_app_id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__, NannyDbsCheckSummary.as_view().__name__)

    def test_can_render_insurance_cover_details_page(self, *args):
        """
        Test to ensure that the page for flagging insurance cover details can be rendered.
        """
        response = self.client.get(reverse('nanny_insurance_cover_summary') + '?id=' + test_app_id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__, NannyInsuranceCoverSummary.as_view().__name__)

    def test_continue_complete_review_button_appears_only_if_all_tasks_reviewed(self, *args):
        """
        Test to ensure that the 'Complete Review' button is only present if all tasks are either 'Reviewed'
        or 'Flagged'.
        """
        pass

    def test_sign_in_details_redirects_to_personal_details(self, *args):
        """
        Test that a POST request to the sign in details page redirects to the personal details page.
        """
        response = self.client.post(reverse('nanny_contact_summary') + '?id=' + test_app_id)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.resolver_match.func.__name__, NannyPersonalDetailsSummary.as_view().__name__)

    def test_personal_details_redirects_to_the_childcare_address_page(self, *args):
        """
        Test that a POST request to the personal details page redirects to the childcare address details page.
        """
        response = self.client.post(reverse('nanny_personal_details_summary') + '?id=' + test_app_id)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.resolver_match.func.__name__, NannyChildcareAddressSummary.as_view().__name__)

    def test_childcare_address_details_redirects_to_the_first_aid_page(self, *args):
        """
        Test that a POST request to the childcare address details page redirects to the first aid details page.
        """
        response = self.client.post(reverse('nanny_childcare_address_summary') + '?id=' + test_app_id)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.resolver_match.func.__name__, NannyFirstAidTrainingSummary.as_view().__name__)

    def test_first_aid_details_redirects_to_the_childcare_training_page(self, *args):
        """
        Test that a POST request to the first aid details page redirects to the childcare training details page.
        """
        response = self.client.post(reverse('nanny_first_aid_training_summary') + '?id=' + test_app_id)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.resolver_match.func.__name__, NannyChildcareTrainingSummary.as_view().__name__)

    def test_childcare_training_redirects_to_the_criminal_record_page(self, *args):
        """
        Test that a POST request to the childcare training details page redirects to the criminal record details page.
        """
        response = self.client.post(reverse('nanny_childcare_training_summary') + '?id=' + test_app_id)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.resolver_match.func.__name__, NannyDbsCheckSummary.as_view().__name__)

    def test_criminal_record_redirects_to_the_insurance_cover_page(self, *args):
        """
        Test that a POST request to the criminal record page redirects to the insurance cover details page.
        """
        response = self.client.post(reverse('nanny_dbs_summary') + '?id=' + test_app_id)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.resolver_match.func.__name__, NannyInsuranceCoverSummary.as_view().__name__)

    def test_insurance_cover_details_redirects_to_the_task_list_page(self, *args):
        """
        Test that a POST request to the insurance cover page redirects to the task list page.
        """
        response = self.client.post(reverse('nanny_insurance_cover_summary') + '?id=' + test_app_id)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.resolver_match.func.__name__, NannyTaskList.as_view().__name__)

    def test_can_flag_personal_details(self, *args):
        """
        Test to ensure that personal details can be flagged.
        """
        pass

    def test_can_flag_childcare_address_details(self, *args):
        """
        Test to ensure that childcare address details can be flagged.
        """
        # TODO - Write test once work commences on flagging Childcare Address details.
        pass

    def test_can_flag_first_aid_details(self, *args):
        """
        Test to ensure that first aid details can be flagged.
        """
        pass

    def test_can_flag_childcare_training_details(self, *args):
        """
        Test to ensure that childcare training details can be flagged.
        """
        pass

    def test_can_flag_criminal_record_details(self, *args):
        """
        Test to ensure that dbs certificate details can be flagged.
        """
        pass

    def test_insurance_cover_details_can_be_flagged(self, *args):
        """
        Test to ensure that insurance cover details can be flagged.
        """
        pass

    def test_can_render_arc_summary_page(self, *args):
        """
        Test to ensure that the Nanny ARC summary page can be rendered.
        """
        response = self.client.get(reverse('nanny_arc_summary') + '?id=' + test_app_id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__, NannyArcSummary.as_view().__name__)

    @tag('integration')
    def test_can_remove_previously_added_dbs_task_arc_comment(self, *args):
        """
        Test to ensure that an ARC user who had previously flagged and commented on a field in the dbs task
        can later remove that comment. Test then that this then does not appear in the view.
        """
        # TODO - figure out precisely how to test this. End-to-end selenium test more applicable?
        # with mock.patch('arc_application.services.db_gateways.NannyGatewayActions.read') as nanny_gateway_read:
        #     nanny_gateway_read.side_effect = side_effect

        self.client.post(
            reverse('nanny_dbs_summary') + '?id=' + '998fd8ec-b96b-4a71-a1a1-a7a3ae186729',
            data={
                'dbs_number_declare': 'on',
                'dbs_number_comments': 'Test this will be removed.'
            }
        )

        # self.assertEqual(TASK_STATUS, 'FLAGGED')

        self.client.post(
            reverse('nanny_dbs_summary') + '?id=' + test_app_id,
            data={}
        )

        api_query = NannyGatewayActions().list('arc-comments', params={''})

        self.assertEqual(api_query.status_code, 404)
        # self.assertEqual(TASK_STATUS, 'REVIEWED')

        self.client.get(reverse('nanny_dbs_summary') + '?id=' + test_app_id)
        # assert that the boxes are unchecked and the comments box not appearing.

    @tag('integration')
    def test_that_flagged_dbs_task_field_renders_with_get_request(self, *args):
        """
        Test that a field which has been flagged in the dbs task will then render in the template with the box checked
        and the comments box visible.
        """
        self.client.post(
            reverse('nanny_dbs_summary') + '?id=' + test_app_id,
            data={
                'dbs_number_declare': 'on',
                'dbs_number_comments': 'Test this will appear.'
            }
        )

        response = self.client.get(reverse('nanny_dbs_summary') + '?id=' + test_app_id)
        # self.assertContains(BOX_CHECKED)

    # ---------- #
    # UNIT tests #
    # ---------- #

    @tag('unit')
    def test_form_view_builder(self, *args):
        pass

    @tag('unit')
    def test_form_builder(self, *args):
        """
        Test to assert that the form_builder functions as expected.
        """
        example_fields = [
            'field_1',
            'field_2',
        ]

        form = NannyFormBuilder(example_fields, api_endpoint_name='fake-endpoint', pk_field_name='fake-pk').create_form()

        self.assertIsInstance(form(), Form)

        for field in example_fields:
            self.assertTrue(hasattr(form(), field + '_declare'))
            self.assertTrue(hasattr(form(), field + '_comments'))
