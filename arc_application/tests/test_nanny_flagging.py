from django.conf import settings
from django.forms import Form
from django.contrib.auth.models import Group, User
from django.test import tag, TestCase

from arc_application.forms.nanny_forms.nanny_form_builder import NannyFormBuilder


class NannyArcFlaggingTests(TestCase):
    """
    Class to handle testing of the flagging functionality in the ARC service for Nanny applications.
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

    @tag('http')
    def test_can_flag_all_fields(self):
        pass

    @tag('http')
    def test_complete_review_appears_if_all_tasks_reviewed(self):
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
