from unittest import TestCase
from uuid import uuid4

from arc_application.forms import *
from arc_application.models import *


class StandardFormValidationTests(TestCase):
    """
    Tests for standard form (i.e not other people) to show it can populate and validate
    """

    def test_log_in_details(self):
        """Login form with correct test data"""
        test_key = uuid4()
        initial_data = {'email_address_declare': True, 'email_address_comments': 'Test'}
        form = LogInDetailsForm(data=initial_data, table_keys=[test_key])
        self.assertTrue(form.is_valid())

    def test_personal_details(self):
        """Personal details form with correct test data"""
        test_key = uuid4()
        initial_data = {'name_declare': True, 'name_comments': 'Test'}
        form = PersonalDetailsForm(data=initial_data, table_keys=[test_key])
        self.assertTrue(form.is_valid())

    def test_first_aid_training(self):
        """First aid training form with correct test data"""
        test_key = uuid4()
        initial_data = {'first_aid_training_organisation_declare': True, 'first_aid_training_organisation_comments': 'Test'}
        form = FirstAidTrainingForm(data=initial_data, table_keys=[test_key])
        self.assertTrue(form.is_valid())

    def test_DBS_check(self):
        """DBS check form with correct test data"""
        test_key = uuid4()
        initial_data = {'dbs_certificate_number_declare': True, 'dbs_certificate_number_comments': 'Test'}
        form = DBSCheckForm(data=initial_data, table_keys=[test_key])
        self.assertTrue(form.is_valid())

    def test_references(self):
        """References form with correct test data"""
        test_key = uuid4()
        initial_data = {'full_name_declare': True, 'full_name_comments': 'Test'}
        form = ReferencesForm(data=initial_data, table_keys=[test_key])
        self.assertTrue(form.is_valid())

    def test_references2(self):
        """Second references form with correct test data"""
        test_key = uuid4()
        initial_data = {'full_name_declare': True, 'full_name_comments': 'Test'}
        form = ReferencesForm2(data=initial_data, table_keys=[test_key])
        self.assertTrue(form.is_valid())


class StandardFormPopulationTests(TestCase):
    """
    Tests each form can populate a piece of initial data when it exists in the tests database
    """

    @classmethod
    def setUp(self):
        self.key_dict = {
            'USER_DETAILS': (uuid4(), 'email'),
            'APPLICANT_PERSONAL_DETAILS': (uuid4(), 'date_of_birth'),
            'APPLICANT_NAME': (uuid4(), 'name'),
            'APPLICANT_HOME_ADDRESS': (uuid4(), 'street_line1'),
            'FIRST_AID_TRAINING': (uuid4(), 'training_organisation'),
            'CRIMINAL_RECORD_CHECK': (uuid4(), 'dbs_submission_number'),
            'REFERENCE': (uuid4(), 'full_name'),
        }

        self.obj_dict = {}

        for key, value in self.key_dict.items():
            data_object = ArcComments.objects.create(table_pk=value[0], table_name=key, field_name=value[1],
                                                     flagged=True, comment='Test')
            self.obj_dict[key] = data_object

    def test_log_in_details_population(self):
        """Log In Details form with initial data to populate from USER_DETAILS"""
        form = LogInDetailsForm(table_keys=[self.key_dict['USER_DETAILS'][0]])
        form.email_address_comments = 'Test'
        form.email_address_declare = True

    def test_personal_details_population(self):
        """Personal Details form with initial data to populate from APPLICANT_PERSONAL_DETAILS, APPLICANT_NAME, and APPLICANT_HOME_ADDRESS"""
        key_list = [self.key_dict['APPLICANT_PERSONAL_DETAILS'][0], self.key_dict['APPLICANT_NAME'][0],
                    self.key_dict['APPLICANT_HOME_ADDRESS'][0]]
        form = PersonalDetailsForm(table_keys=key_list)
        form.date_of_birth_comments = 'Test'
        form.date_of_birth_declare = True
        form.name_comments = 'Test'
        form.name_declare = True
        form.street_line1_comments = 'Test'
        form.street_line1_declare = True

    def test_first_aid_training_population(self):
        """First Aid Training with initial data to populate from FIRST_AID_TRAINING"""
        form = FirstAidTrainingForm(table_keys=[self.key_dict['FIRST_AID_TRAINING'][0]])
        form.first_aid_training_organisation_comments = 'Test'
        form.first_aid_training_organisation_declare = True

    def test_DBS_check_population(self):
        """DBS form with initial data to populate from CRIMINAL_RECORD_CHECK"""
        form = DBSCheckForm(table_keys=[self.key_dict['CRIMINAL_RECORD_CHECK'][0]])
        form.dbs_submission_number_comments = 'Test'
        form.dbs_submission_number_declare = True

    def test_references_population(self):
        """Reference form with initial data to populate from REFERENCE"""
        form = ReferencesForm(table_keys=[self.key_dict['REFERENCE'][0]])
        form.full_name_comments = 'Test'
        form.full_name_declare = True

    def test_references2_population(self):
        """Reference form with initial data to populate from REFERENCE"""
        form = ReferencesForm2(table_keys=[self.key_dict['REFERENCE'][0]])
        form.full_name_comments = 'Test'
        form.full_name_declare = True
