
from django.test import TestCase, tag

from ...models import ChildcareType
from ...tests.utils import create_childminder_application, create_arc_user
from ...childminder_task_util import get_number_of_tasks
from ...views.childminder_views.type_of_childcare import get_register_name


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