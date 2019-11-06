
from django.test import TestCase, tag

from ...models import ChildcareType
from ...tests.utils import create_childminder_application, create_arc_user
from ...childminder_task_util import get_number_of_tasks
from ...views.childminder_views.type_of_childcare import get_register_name
from ...views.childminder_views import personal_details_individual_lookup


@tag('unit')
class ChildminderTaskUtilUnitTests(TestCase):

    def test_get_number_of_tasks(self):
        """
        Tests the get_number_of_tasks function
        """
        user = create_arc_user()
        application = create_childminder_application(user.pk)
        childcare_type = ChildcareType.objects.get(application_id=application.pk)

        childcare_type.zero_to_five = True
        childcare_type.save()
        application.own_children = False
        application.working_in_other_childminder_home = True
        application.save()

        number_of_tasks = get_number_of_tasks(application, childcare_type)
        self.assertEqual(8, number_of_tasks)

        childcare_type.zero_to_five = True
        childcare_type.save()
        application.own_children = True
        application.working_in_other_childminder_home = True
        application.save()

        number_of_tasks = get_number_of_tasks(application, childcare_type)
        self.assertEqual(8, number_of_tasks)

        childcare_type.zero_to_five = True
        childcare_type.save()
        application.own_children = True
        application.working_in_other_childminder_home = False
        application.save()

        number_of_tasks = get_number_of_tasks(application, childcare_type)
        self.assertEqual(9, number_of_tasks)

        childcare_type.zero_to_five = False
        childcare_type.save()
        application.own_children = False
        application.working_in_other_childminder_home = True
        application.save()

        number_of_tasks = get_number_of_tasks(application, childcare_type)
        self.assertEqual(6, number_of_tasks)

        childcare_type.zero_to_five = False
        childcare_type.save()
        application.own_children = False
        application.working_in_other_childminder_home = False
        application.save()

        number_of_tasks = get_number_of_tasks(application, childcare_type)
        self.assertEqual(7, number_of_tasks)

        childcare_type.zero_to_five = False
        childcare_type.save()
        application.own_children = True
        application.working_in_other_childminder_home = False
        application.save()

        number_of_tasks = get_number_of_tasks(application, childcare_type)
        self.assertEqual(7, number_of_tasks)

        childcare_type.zero_to_five = True
        childcare_type.save()
        application.own_children = False
        application.working_in_other_childminder_home = False
        application.save()

        number_of_tasks = get_number_of_tasks(application, childcare_type)
        self.assertEqual(9, number_of_tasks)

        childcare_type.zero_to_five = False
        childcare_type.save()
        application.own_children = True
        application.working_in_other_childminder_home = True
        application.save()

        number_of_tasks = get_number_of_tasks(application, childcare_type)
        self.assertEqual(6, number_of_tasks)


@tag('unit')
class ChildminderTypeOfChildcareHelperUnitTests(TestCase):

    def test_get_register_name(self):
        """
        Tests the get_register_name function
        """
        user = create_arc_user()
        application = create_childminder_application(user.pk)
        childcare_type = ChildcareType.objects.get(application_id=application.pk)

        childcare_type.zero_to_five = True
        childcare_type.five_to_eight = True
        childcare_type.eight_plus = True
        childcare_type.save()

        register = get_register_name(childcare_type)
        self.assertEqual('Early Years Register and Childcare Register (both parts)', register)

        childcare_type.zero_to_five = False
        childcare_type.five_to_eight = True
        childcare_type.eight_plus = True
        childcare_type.save()

        register = get_register_name(childcare_type)
        self.assertEqual('Childcare Register (both parts)', register)

        childcare_type.zero_to_five = True
        childcare_type.five_to_eight = False
        childcare_type.eight_plus = False
        childcare_type.save()

        register = get_register_name(childcare_type)
        self.assertEqual('Early Years Register', register)

        childcare_type.zero_to_five = True
        childcare_type.five_to_eight = True
        childcare_type.eight_plus = False
        childcare_type.save()

        register = get_register_name(childcare_type)
        self.assertEqual('Early Years Register and Childcare Register (compulsory part)', register)

        childcare_type.zero_to_five = True
        childcare_type.five_to_eight = False
        childcare_type.eight_plus = True
        childcare_type.save()

        register = get_register_name(childcare_type)
        self.assertEqual('Early Years Register and Childcare Register (voluntary part)', register)

        childcare_type.zero_to_five = False
        childcare_type.five_to_eight = True
        childcare_type.eight_plus = False
        childcare_type.save()

        register = get_register_name(childcare_type)
        self.assertEqual('Childcare Register (compulsory part)', register)

        childcare_type.zero_to_five = False
        childcare_type.five_to_eight = False
        childcare_type.eight_plus = True
        childcare_type.save()

        register = get_register_name(childcare_type)
        self.assertEqual('Childcare Register (voluntary part)', register)


@tag('unit')
class PersonalDetailsLinkingTests(TestCase):

    def test_convert_valid_dob(self):
        """
        Tests that a valid raw date can be formatted for display
        """
        dob = '1990-12-08'
        result = personal_details_individual_lookup._format_date_of_birth(dob)
        self.assertEqual(result, '8 Dec 1990')

    def test_convert_invalid_dob(self):
        """
        Tests that a valid raw indate is returned in its original format
        """
        dob = '1-1-2001'
        result = personal_details_individual_lookup._format_date_of_birth(dob)
        self.assertEqual(result, dob)

    def test_remove_duplicates(self):
        """
        Tests that an input list with duplicates can be returned without duplicates.
        Duplicates are removed based on a shared id only, not other properties
        """
        source_list = [
            {
                'IndividualID': '1234',
                'DOB': '1990-02-21',
                'Dummy': 'Sausage'
            },
            {
                'IndividualID': '1234',
                'DOB': '1990-02-21',
                'Dummy': 'Chips'
            },
            {
                'IndividualID': '5678',
                'DOB': '1990-02-21',
                'Dummy': 'Beans'
            }
        ]

        expected_list = [
            {
                'IndividualID': '1234',
                'DOB': '21 Feb 1990',
                'Dummy': 'Sausage'
            },
            {
                'IndividualID': '5678',
                'DOB': '21 Feb 1990',
                'Dummy': 'Beans'
            }
        ]

        result_list = personal_details_individual_lookup._extract_json_to_list(source_list)
        self.assertEqual(expected_list, result_list)
