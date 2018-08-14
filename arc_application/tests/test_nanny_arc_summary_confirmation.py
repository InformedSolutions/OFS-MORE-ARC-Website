from unittest import mock

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.http import HttpResponse
from django.test import tag, TestCase
from django.urls import reverse


class NannyArcSummaryConfirmationTests(TestCase):
    """
    Test suite for testing nanny helper functions
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username='something_sensible',
            email='test@test.com',
            password='passwordspeltbackwards'
        )
        g = Group.objects.create(name=settings.ARC_GROUP)
        g.user_set.add(self.user)

        global arc_test_user
        arc_test_user = self.user

        self.client.login(username='something_sensible', password='passwordspeltbackwards')

        self.mock_general_data = {
            'application_id': 'e54bd2a9-8e8c-419a-9691-64e432713626',
            'user_id': '1',
            'last_accessed': '2018-08-13T15:06:57.014581Z',
            'app_type': 'Nanny'
        }

        self.mock_arc_application_mixed = {
            'login_details_review': 'COMPLETED',
            'personal_details_review': 'FLAGGED',
            'childcare_address_review': 'COMPLETED',
            'first_aid_review': 'FLAGGED',
            'childcare_training_review': 'COMPLETED',
            'dbs_review': 'FLAGGED',
            'insurance_cover_review': 'COMPLETED',
        }

        self.mock_arc_application_completed = {
            'login_details_review': 'COMPLETED',
            'personal_details_review': 'COMPLETED',
            'childcare_address_review': 'COMPLETED',
            'first_aid_review': 'COMPLETED',
            'childcare_training_review': 'COMPLETED',
            'dbs_review': 'COMPLETED',
            'insurance_cover_review': 'COMPLETED',
        }

    @tag('unit')
    def test_send_accepted_email_called(self):
        with mock.patch('arc_application.services.db_gateways.NannyGatewayActions.read') as mock_nanny_read, \
                mock.patch('arc_application.services.db_gateways.IdentityGatewayActions.read') as mock_identity_read, \
                mock.patch('arc_application.models.Arc.objects.get') as mock_arc, \
                mock.patch('arc_application.views.nanny_views.nanny_arc_summary_confirmation.send_accepted_email') as mock_send_accepted_email:

            mock_arc_application_dict = self.mock_general_data
            mock_arc_application_dict.update(self.mock_arc_application_completed)
            mock_arc_application = MockApplication(mock_arc_application_dict)

            mock_arc.return_value = mock_arc_application

            mock_nanny_read.side_effect = mock_nanny_read_side_effect
            mock_identity_read.return_value = mock_identity_return_value

            mock_application_id = mock_arc_application['application_id']
            response = self.client.get(reverse('nanny_confirmation')+'?id='+mock_application_id)
            print(response)
            self.assertTrue(mock_send_accepted_email.called)

    @tag('unit')
    def test_send_returned_email_called(self):
        with mock.patch('arc_application.services.db_gateways.NannyGatewayActions.read') as mock_nanny_read, \
                mock.patch('arc_application.services.db_gateways.IdentityGatewayActions.read') as mock_identity_read, \
                mock.patch('arc_application.models.Arc.objects.get') as mock_arc, \
                mock.patch('arc_application.views.nanny_views.nanny_arc_summary_confirmation.send_returned_email') as mock_send_returned_email:

            mock_arc_application_dict = self.mock_general_data
            mock_arc_application_dict.update(self.mock_arc_application_mixed)
            mock_arc_application = MockApplication(mock_arc_application_dict)

            mock_arc.return_value = mock_arc_application

            mock_nanny_read.side_effect = mock_nanny_read_side_effect
            mock_identity_read.return_value = mock_identity_return_value

            mock_application_id = mock_arc_application['application_id']
            response = self.client.get(reverse('nanny_confirmation')+'?id='+mock_application_id)
            print(response)
            self.assertTrue(mock_send_returned_email.called)


def mock_nanny_read_side_effect(endpoint, *args, **kwargs):
    return mock_nanny_return_values[endpoint]


def create_response(return_record):
    mock_response = HttpResponse()
    mock_response.status_code = 200
    mock_response.record = return_record

    return mock_response


class MockApplication:
    def __init__(self, data_dict):
        self.data_dict = data_dict

    def __getattr__(self, item):
        return self.data_dict.get(item)

    def __getitem__(self, item):
        return self.data_dict.get(item)


mock_application_response_record = {
    'application_reference': 'NA1000001'
}

mock_personal_details_response_record = {
    'first_name': 'test'
}

mock_identity_response_record = {
    'email': 'test@test.com'
}

mock_nanny_return_values = {
    'application': create_response(mock_application_response_record),
    'applicant-personal-details': create_response(mock_personal_details_response_record)
}

mock_identity_return_value = create_response(mock_identity_response_record)