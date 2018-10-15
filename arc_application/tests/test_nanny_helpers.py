from django.test import TestCase, tag

from arc_application.models import Arc

from arc_application.services.nanny_view_helpers import *

class NannyHelperTests(TestCase):
    """
    Test suite for testing nanny helper functions
    """

    def setUp(self):

        self.dob_test_list_correct = [
            ('2013-12-14', ['2013', '12', '14']),
            ('2015-02-15', ['2015', '02', '15'])
        ]

        self.mock_arc_application_mixed = {
            'application_id': 'e54bd2a9-8e8c-419a-9691-64e432713626',
            'user_id': '1',
            'last_accessed': '2018-08-13T15:06:57.014581Z',
            'app_type': 'Nanny',
            'login_details_review': 'COMPLETED',
            'personal_details_review': 'FLAGGED',
            'childcare_address_review': 'COMPLETED',
            'first_aid_review': 'FLAGGED',
            'childcare_training_review': 'COMPLETED',
            'dbs_review': 'FLAGGED',
            'insurance_cover_review': 'COMPLETED',
        }

        self.mock_arc_application_all_flagged = {
            'application_id': 'e54bd2a9-8e8c-419a-9691-64e432713626',
            'user_id': '1',
            'last_accessed': '2018-08-13T15:06:57.014581Z',
            'app_type': 'Nanny',
            'login_details_review': 'FLAGGED',
            'personal_details_review': 'FLAGGED',
            'childcare_address_review': 'FLAGGED',
            'first_aid_review': 'FLAGGED',
            'childcare_training_review': 'FLAGGED',
            'dbs_review': 'FLAGGED',
            'insurance_cover_review': 'FLAGGED',
        }

        self.mock_arc_application_all_completed = {
            'application_id': 'e54bd2a9-8e8c-419a-9691-64e432713626',
            'user_id': '1',
            'last_accessed': '2018-08-13T15:06:57.014581Z',
            'app_type': 'Nanny',
            'login_details_review': 'COMPLETED',
            'personal_details_review': 'COMPLETED',
            'childcare_address_review': 'COMPLETED',
            'first_aid_review': 'COMPLETED',
            'childcare_training_review': 'COMPLETED',
            'dbs_review': 'COMPLETED',
            'insurance_cover_review': 'COMPLETED',
        }

    @tag('unit')
    def test_parse_date_of_birth_correct(self):
        for test_case in self.dob_test_list_correct:
            self.assertTrue(testing_parse_date_of_birth(test_case))

    @tag('unit')
    def test_check_all_task_statuses(self):
        mock_app = self.mock_arc_application_all_flagged

        self.assertTrue(testing_check_all_task_statuses(mock_app, ['FLAGGED']))

    @tag('unit')
    def test_nanny_all_completed(self):

        # Test all_completed with a MIXED dictionary asserts FALSE
        self.assertFalse(testing_all_completed(self.mock_arc_application_mixed))

        # Test all_completed with a COMPLETED dictionary asserts TRUE
        self.assertTrue(testing_all_completed(self.mock_arc_application_all_completed))

        # Test all_completed with a FLAGGED dictionary asserts FALSE
        self.assertFalse(testing_all_completed(self.mock_arc_application_all_flagged))

    @tag('unit')
    def test_nanny_all_reviewed(self):

        # Test all_reviewed with a MIXED dictionary asserts TRUE
        self.assertTrue(testing_all_reviewed(self.mock_arc_application_mixed))

        # Test all_reviewed with a COMPLETED dictionary asserts TRUE
        self.assertTrue(testing_all_reviewed(self.mock_arc_application_all_completed))

        # Test all_reviewed with a FLAGGED dictionary asserts TRUE
        self.assertTrue(testing_all_reviewed(self.mock_arc_application_all_flagged))


def testing_parse_date_of_birth(test_case):
    test_input, expected_output = test_case
    return parse_date_of_birth(test_input) == expected_output


def testing_check_all_task_statuses(mock_arc, status_list):
    arc_app = Arc.objects.create(**mock_arc)
    return check_all_task_statuses(arc_app, status_list)


def testing_all_completed(mock_arc_data):
    mock_app = MockApplication(mock_arc_data)
    return nanny_all_completed(mock_app)


def testing_all_reviewed(mock_arc_data):
    mock_app = MockApplication(mock_arc_data)
    return nanny_all_reviewed(mock_app)


def delete_mock_application(app_id):
    Arc.objects.get(application_id=app_id).delete()


def create_mock_dictionary(general, task_status_list):
    mock_arc_application = general
    mock_arc_application.update(task_status_list)
    return mock_arc_application


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