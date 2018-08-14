from unittest import mock

from django.test import TestCase, tag

from arc_application.models import Arc

from arc_application.views.nanny_views.nanny_view_helpers import *

class NannyHelperTests(TestCase):
    """
    Test suite for testing nanny helper functions
    """

    def setUp(self):
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

        self.mock_arc_application_all_flagged = {
            'login_details_review': 'FLAGGED',
            'personal_details_review': 'FLAGGED',
            'childcare_address_review': 'FLAGGED',
            'first_aid_review': 'FLAGGED',
            'childcare_training_review': 'FLAGGED',
            'dbs_review': 'FLAGGED',
            'insurance_cover_review': 'FLAGGED',
        }

        self.mock_arc_application_all_completed = {
            'login_details_review': 'COMPLETED',
            'personal_details_review': 'COMPLETED',
            'childcare_address_review': 'COMPLETED',
            'first_aid_review': 'COMPLETED',
            'childcare_training_review': 'COMPLETED',
            'dbs_review': 'COMPLETED',
            'insurance_cover_review': 'COMPLETED',
        }

        self.dob_test_list_correct = [
            ('2013-12-14', ['2013', '12', '14']),
            ('2015-02-15', ['2015', '02', '15'])
        ]

    @tag('unit')
    def test_parse_date_of_birth_correct(self):
        for test_case in self.dob_test_list_correct:
            self.assertTrue(testing_parse_date_of_birth(test_case))

    @tag('unit')
    def test_check_all_task_statuses(self):
        mock_arc_application = self.mock_general_data
        mock_arc_application.update(self.mock_arc_application_all_flagged)

        self.assertTrue(testing_check_all_task_statuses(mock_arc_application, ['FLAGGED']))

    @tag('unit')
    def test_nanny_all_completed(self):
        app_id = self.mock_general_data['application_id']

        mock_app = create_mock_dictionary(self.mock_general_data,
                                          self.mock_arc_application_mixed)
        self.assertFalse(testing_all_completed(mock_app))
        delete_mock_application(app_id)

        mock_app = create_mock_dictionary(self.mock_general_data,
                                          self.mock_arc_application_all_completed)
        self.assertTrue(testing_all_completed(mock_app))
        delete_mock_application(app_id)

        mock_app = create_mock_dictionary(self.mock_general_data,
                                          self.mock_arc_application_all_flagged)
        self.assertFalse(testing_all_completed(mock_app))
        delete_mock_application(app_id)

    @tag('unit')
    def test_nanny_all_reviewed(self):
        app_id = self.mock_general_data['application_id']

        mock_app = create_mock_dictionary(self.mock_general_data,
                                          self.mock_arc_application_mixed)
        self.assertTrue(testing_all_reviewed(mock_app))
        delete_mock_application(app_id)

        mock_app = create_mock_dictionary(self.mock_general_data,
                                          self.mock_arc_application_all_completed)
        self.assertTrue(testing_all_reviewed(mock_app))
        delete_mock_application(app_id)

        mock_app = create_mock_dictionary(self.mock_general_data,
                                          self.mock_arc_application_all_flagged)
        self.assertTrue(testing_all_reviewed(mock_app))
        delete_mock_application(app_id)


def testing_parse_date_of_birth(test_case):
    test_input, expected_output = test_case
    return parse_date_of_birth(test_input) == expected_output

def testing_check_all_task_statuses(mock_arc, status_list):
    arc_app = Arc.objects.create(**mock_arc)
    return check_all_task_statuses(arc_app, status_list)


def testing_all_completed(mock_arc):
    arc_app = Arc.objects.create(**mock_arc)
    return nanny_all_completed(arc_app)

def testing_all_reviewed(mock_arc):
    arc_app = Arc.objects.create(**mock_arc)
    return nanny_all_reviewed(arc_app)

def delete_mock_application(app_id):
    Arc.objects.get(application_id=app_id).delete()

def create_mock_dictionary(general, task_status_list):
    mock_arc_application = general
    mock_arc_application.update(task_status_list)
    return mock_arc_application