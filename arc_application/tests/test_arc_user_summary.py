from django.conf import settings
from django.contrib.auth.models import Group, User
from django.test import TestCase


class ArcUserSummaryPageTests(TestCase):
    """
    Test suite for the functionality within the ARC summary page.
    """
    def setUp(self):
        self.user = User.objects.create_user(
            username='arc_test', email='test@test.com', password='my_secret')
        g = Group.objects.create(name=settings.ARC_GROUP)
        g.user_set.add(self.user)

        global arc_test_user
        arc_test_user = self.user

    # ----------------------- #
    # Integration level tests #
    # ----------------------- #

    def test_list_nanny_tasks_to_review(self):
        """
        If we are mocking the Gateway response, this test will continue to pass even if the models are updated.
        Must be an integration test?
        """
        pass

    # ---------------- #
    # HTTP level tests #
    # ---------------- #

    def test_can_render_arc_user_summary_page(self):
        pass

    def test_page_renders_with_table_if_user_has_assigned_apps(self):
        pass

    def test_page_renders_without_table_if_user_has_no_assigned_apps(self):
        pass

    def test_page_renders_with_error_if_no_nanny_apps_available(self):
        pass

    def test_page_renders_with_error_if_no_childminder_apps_available(self):
        pass

    def test_assigns_childminder_app_if_one_available(self):
        pass

    def test_assigns_nanny_app_if_one_available(self):
        pass

    def test_cannot_assign_more_than_five_applications(self):
        pass

    # ---------- #
    # UNIT tests #
    # ---------- #

    def test_count_assigned_apps(self):
        pass

    def test_get_oldest_nanny_app_id(self):
        pass

    def test_get_oldest_childminder_app_id(self):
        pass

    def test_sort_applications_by_date_submitted(self):
        pass

    def test_assign_nanny_app_to_user(self):
        pass

    def test_assign_childminder_app_to_user(self):
        pass

    def test_list_childminder_tasks_to_review(self):
        pass

    def test_release_nanny_app_to_pool(self):
        pass

    def test_release_childminder_app_to_pool(self):
        pass

    def test_get_all_table_data(self):
        pass

    def test_get_nanny_row_data(self):
        pass

    def test_get_childminder_row_data(self):
        pass
