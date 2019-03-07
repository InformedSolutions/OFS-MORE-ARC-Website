
from django.conf import settings
from django.contrib.auth.models import Group, User
from django.http import HttpResponse
from django.test import tag, TestCase


@tag('http')
class NannyConfirmationFunctionalTests(TestCase):

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

        # Application data containing data that will be shared between constructed mock applications.
        self.mock_general_data = {
            'application_id': 'e54bd2a9-8e8c-419a-9691-64e432713626',
            'user_id': '1',
            'last_accessed': '2018-08-13T15:06:57.014581Z',
            'app_type': 'Nanny'
        }

        # Application data containing mixed ('FLAGGED' or 'COMPLETED') statuses
        self.mock_arc_application_mixed = {
            'login_details_review': 'COMPLETED',
            'personal_details_review': 'FLAGGED',
            'childcare_address_review': 'COMPLETED',
            'first_aid_review': 'FLAGGED',
            'childcare_training_review': 'COMPLETED',
            'dbs_review': 'FLAGGED',
            'insurance_cover_review': 'COMPLETED',
        }

        # Application data containing mixed ('FLAGGED' or 'COMPLETED') statuses
        self.mock_arc_application_completed = {
            'login_details_review': 'COMPLETED',
            'personal_details_review': 'COMPLETED',
            'childcare_address_review': 'COMPLETED',
            'first_aid_review': 'COMPLETED',
            'childcare_training_review': 'COMPLETED',
            'dbs_review': 'COMPLETED',
            'insurance_cover_review': 'COMPLETED',
        }

    def test_send_accepted_email_called(self):
        self.skipTest('testNotImplemented')
        # # Mocking Both GatewayActions, Arc.objects.get and the send_accepted_email function in the confirmation view.
        # with mock.patch('arc_application.services.db_gateways.NannyGatewayActions.read') as mock_nanny_read, \
        #         mock.patch('arc_application.services.db_gateways.IdentityGatewayActions.read') as mock_identity_read, \
        #         mock.patch('arc_application.models.Arc.objects.get') as mock_arc, \
        #         mock.patch('arc_application.views.nanny_arc_summary.send_accepted_email') as mock_send_accepted_email:
        #
        #     # Setting up the mock_arc_application
        #     mock_arc_application_dict = self.mock_general_data
        #     mock_arc_application_dict.update(self.mock_arc_application_completed)
        #     # Using a MockApplication class instead of a dictionary to modify it's access methods to also accept dot
        #     #  (".") notation. E.g mock_arc_application.application_id
        #     mock_arc_application = MockApplication(mock_arc_application_dict)
        #
        #     # Arc.objects.get will return the same mock_arc_application regardless of parameters.
        #     mock_arc.return_value = mock_arc_application
        #
        #     # Both gateways.read will return a fixed output instead.
        #     # Note that nanny_read will return something different depending on the 'endpoint' param
        #     mock_nanny_read.side_effect = mock_nanny_read_side_effect
        #     mock_identity_read.return_value = mock_identity_return_value
        #
        #     mock_application_id = mock_arc_application['application_id']
        #
        #     # Send a post request to the nanny_confirmation view
        #     response = self.client.get(reverse('nanny_confirmation')+'?id='+mock_application_id)
        #     print(response)
        #
        #     # Assert that send_accepted_email was called.
        #     self.assertTrue(mock_send_accepted_email.called)


    def test_send_returned_email_called(self):
        self.skipTest('testNotImplemented')
        # with mock.patch('arc_application.services.db_gateways.NannyGatewayActions.read') as mock_nanny_read, \
        #         mock.patch('arc_application.services.db_gateways.IdentityGatewayActions.read') as mock_identity_read, \
        #         mock.patch('arc_application.models.Arc.objects.get') as mock_arc, \
        #         mock.patch('arc_application.views.nanny_arc_summary.send_returned_email') as mock_send_returned_email:
        #
        #     # Setting up the mock_arc_application
        #     mock_arc_application_dict = self.mock_general_data
        #     mock_arc_application_dict.update(self.mock_arc_application_mixed)
        #     mock_arc_application = MockApplication(mock_arc_application_dict)
        #
        #     # Arc.objects.get will return the same mock_arc_application regardless of parameters.
        #     mock_arc.return_value = mock_arc_application
        #
        #     # Both gateways.read will return a fixed output instead.
        #     # Note that nanny_read will return something different depending on the 'endpoint' param
        #     mock_nanny_read.side_effect = mock_nanny_read_side_effect
        #     mock_identity_read.return_value = mock_identity_return_value
        #
        #     # Send a post request to the nanny_confirmation view
        #     mock_application_id = mock_arc_application['application_id']
        #     response = self.client.get(reverse('nanny_confirmation')+'?id='+mock_application_id)
        #     print(response)
        #
        #     # Assert that send_accepted_email was called.
        #     self.assertTrue(mock_send_returned_email.called)


def mock_nanny_read_side_effect(endpoint, *args, **kwargs):
    """
    Splits up what the mock_nanny_read function will do when called with a different 'endpoint' parameter.
    :param endpoint: String containing the endpoint, e.g 'application'.
    :param args: Unused, Extra variables are caught.
    :param kwargs: Unused, Extra variables are caught.
    :return: The assigned response to that endpoint parameter passed.
    """
    return mock_nanny_return_values[endpoint]


def create_response(return_record):
    """
    Creates a HttpResponse instance that returns a specific record and an 'OK' status code.
    :param return_record: The record to be returned, expected as a dictionary.
    :return:
    """
    mock_response = HttpResponse()
    mock_response.status_code = 200
    mock_response.record = return_record

    return mock_response


class MockApplication:
    """
    Simple class used to allow a dictionary to be accessed in a similar way to a model.
    Specifically with dot ('.') notation (__getattr__), e.g MockApplication.first_name
    """
    def __init__(self, data_dict):
        self.data_dict = data_dict

    def __getattr__(self, item):
        return self.data_dict.get(item)

    def __getitem__(self, item):
        return self.data_dict.get(item)


mock_application_response_record = {
    'application_reference': 'NA1000001',
    'application_status': 'ACCEPTED'
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