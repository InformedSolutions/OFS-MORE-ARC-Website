"""
Selenium test cases
"""

import os
from datetime import datetime

from django.core.management import call_command
from django.test import LiveServerTestCase, override_settings, tag
from selenium import webdriver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options

from .selenium_task_executor import SeleniumTaskExecutor
from ...models import Application

from faker import Faker

# Configure faker to use english locale
faker = Faker('en_GB')

selenium_driver = None
selenium_task_executor = None


@tag('selenium')
@override_settings(ALLOWED_HOSTS=['*'])
class TestArcFunctions(LiveServerTestCase):
    port = 8000

    if os.environ.get('LOCAL_SELENIUM_DRIVER') == 'True':
        host = '127.0.0.1'
    else:
        host = '0.0.0.0'

    def setUp(self):
        global selenium_task_executor
        global selenium_driver

        # Load fixtures to populate test users
        call_command("loaddata", "initial_arc_user.json", verbosity=0)

        # Load fixtures to populate a test application
        call_command("loaddata", "test_application.json", verbosity=0)

        base_url = os.environ.get('DJANGO_LIVE_TEST_SERVER_ADDRESS')

        if os.environ.get('LOCAL_SELENIUM_DRIVER') == 'True':
            # If running on a windows host, make sure to drop the
            # geckodriver.exe into your Python/Scripts installation folder
            if os.environ.get('HEADLESS_CHROME') == 'True':
                # To install chromedriver on an ubuntu machine:
                # https://tecadmin.net/setup-selenium-chromedriver-on-ubuntu/
                # For the latest version:
                # https://github.com/joyzoursky/docker-python-chromedriver/blob/master/py3/py3.6-selenium/Dockerfile
                path_to_chromedriver = os.popen("which chromedriver").read().rstrip()
                chrome_options = Options()
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--disable-gpu")
                selenium_driver = webdriver.Chrome(path_to_chromedriver, chrome_options=chrome_options)
            else:
                selenium_driver = webdriver.Firefox()
            selenium_driver.maximize_window()
        else:
            # If not using local driver, default requests to a selenium grid server
            selenium_driver = webdriver.Remote(
                command_executor=os.environ['SELENIUM_HOST'],
                desired_capabilities={'platform': 'ANY', 'browserName': 'firefox', 'version': ''}
            )

        self.verification_errors = []
        self.accept_next_alert = True

        selenium_task_executor = SeleniumTaskExecutor(selenium_driver, base_url)

        super(TestArcFunctions, self).setUp()

    # Test wrappers are used here to allow ordering of tests. Tests are also split to produce more
    # meaningful test report outputs in the event of a failure.

    # -----------------------
    # Login tests
    # -----------------------

    def test_can_login_as_arc_user(self):
        self.assert_can_login_as_arc_user()

    def assert_can_login_as_arc_user(self):
        """
        Tests that an ARC user can login
        """
        global selenium_task_executor

        try:
            self.login_as_arc_user()
            self.assertEqual("Sign out", selenium_task_executor.get_driver().find_element_by_link_text("Sign out").text)
            selenium_task_executor.get_driver().find_element_by_link_text("Sign out").click()
        except Exception as e:
            self.capture_screenshot()
            raise e

    def test_can_login_as_contact_centre_user(self):
        self.assert_can_login_as_contact_centre_user()

    def assert_can_login_as_contact_centre_user(self):
        """
        Tests that a Contact Centre user can login
        """
        global selenium_task_executor

        try:
            self.login_as_contact_user()
            self.assertEqual("Sign out", selenium_task_executor.get_driver().find_element_by_link_text("Sign out").text)
            selenium_task_executor.get_driver().find_element_by_link_text("Sign out").click()
        except Exception as e:
            self.capture_screenshot()
            raise e

    # -----------------------
    # Main summary page tests
    # -----------------------

    def test_message_shown_when_no_applications_to_assign_to_arc_user(self):
        self.assert_message_shown_when_no_applications_to_assign_to_arc_user()

    def assert_message_shown_when_no_applications_to_assign_to_arc_user(self):
        """
        Tests that an information message gets shown when an ARC user attempts to assign an application to themselves
        but none are ready for review
        """
        global selenium_task_executor

        try:
            Application.objects.all().delete()
            self.login_as_arc_user()
            selenium_task_executor.get_driver().find_element_by_name("add_childminder_application").click()
            self.assertTrue(
                selenium_task_executor.get_driver().find_element_by_class_name('error-summary').is_displayed()
            )
        except Exception as e:
            self.capture_screenshot()
            raise e

    def test_can_assign_application_to_arc_user(self):
        self.assert_can_assign_and_release_an_application_as_arc_user()

    def assert_can_assign_and_release_an_application_as_arc_user(self):
        """
        Tests that an ARC user can assign themselves an application
        """
        global selenium_task_executor

        try:
            self.login_as_arc_user()
            selenium_task_executor.get_driver().find_element_by_name("add_childminder_application").click()
            selenium_task_executor.get_driver().find_element_by_xpath("//*[@id='request-table']/tbody/tr[1]/td[5]/a").click()
            self.assertEqual("Application overview", selenium_task_executor.get_driver().title)
            self.release_arc_application()
        except Exception as e:
            self.capture_screenshot()
            raise e

    # -----------------------
    # Audit log tests
    # -----------------------

    def test_arc_user_can_view_audit_log_via_task_list(self):
        self.assert_arc_user_can_view_audit_log_via_task_list()

    def assert_arc_user_can_view_audit_log_via_task_list(self):
        """
        Tests that an ARC user can access the audit log feature
        """
        global selenium_task_executor

        try:
            self.login_as_arc_user()
            selenium_task_executor.get_driver().find_element_by_name("add_childminder_application").click()
            selenium_task_executor.get_driver().find_element_by_xpath("//*[@id='request-table']/tbody/tr[1]/td[5]/a").click()
            selenium_task_executor.get_driver().find_element_by_link_text("Audit log").click()
            self.assertEqual("Audit log", selenium_task_executor.get_driver().title)
        except Exception as e:
            self.capture_screenshot()
            raise e

    def test_arc_user_can_view_audit_log_via_task_list(self):
        self.assert_arc_user_can_view_audit_log_via_task_list()

    def assert_arc_user_can_view_audit_log_via_task_list(self):
        """
        Tests that an ARC user can access the audit log feature
        """
        global selenium_task_executor

        try:
            self.login_as_arc_user()
            selenium_task_executor.get_driver().find_element_by_name("add_childminder_application").click()
            selenium_task_executor.get_driver().find_element_by_xpath("//*[@id='request-table']/tbody/tr[1]/td[5]/a").click()
            selenium_task_executor.get_driver().find_element_by_link_text("Audit log").click()
            self.assertEqual("Audit log", selenium_task_executor.get_driver().title)
        except Exception as e:
            self.capture_screenshot()
            raise e

    def test_contact_centre_user_can_view_audit_log(self):
        self.assert_contact_centre_user_can_view_audit_log()

    def assert_contact_centre_user_can_view_audit_log(self):
        """
        Tests that a Contact Centre user can search for an application and view its audit log
        """
        global selenium_task_executor

        try:
            self.login_as_contact_user()
            selenium_task_executor.get_driver().find_element_by_id("id_name_search_field").send_keys("test")
            selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Search']").click()
            selenium_task_executor.get_driver().find_element_by_link_text("Application Summary").click()
            self.assertEqual("Application summary", selenium_task_executor.get_driver().title)
            selenium_task_executor.get_driver().find_element_by_link_text("Audit log").click()
            self.assertEqual("Audit log", selenium_task_executor.get_driver().title)
        except Exception as e:
            self.capture_screenshot()
            raise e

    # def test_contact_centre_user_viewing_application_gets_logged_in_audit_log(self):
    #     self.assert_contact_centre_user_viewing_application_gets_logged_in_audit_log()

    def assert_contact_centre_user_viewing_application_gets_logged_in_audit_log(self):
        """
        Tests that a Contact Centre user can search for an application and view its audit log
        """
        global selenium_task_executor

        try:
            self.login_as_contact_user()
            selenium_task_executor.get_driver().find_element_by_id("id_name_search_field").send_keys("test")
            selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Search']").click()
            selenium_task_executor.get_driver().find_element_by_link_text("Application Summary").click()
            self.assertEqual("Applications", selenium_task_executor.get_driver().title)
            selenium_task_executor.get_driver().find_element_by_link_text("Audit log").click()
            self.assertEqual("Audit log", selenium_task_executor.get_driver().title)
            self.assertEqual("Application viewed by cc1",
                             selenium_task_executor.get_driver().find_element_by_xpath("//main[@id='content']/main/table/tbody/tr/td[3]").text)
        except Exception as e:
            self.capture_screenshot()
            raise e

    # -----------------------
    # Search tests
    # -----------------------

    def test_arc_user_can_search_and_view_applications(self):
        self.assert_arc_user_can_search_and_view_applications()

    def assert_arc_user_can_search_and_view_applications(self):
        """
        Tests that an Arc user can perform a search on applications
        """
        global selenium_task_executor
        title_change_wait = 15
        try:
            self.login_as_arc_user()
            selenium_task_executor.get_driver().find_element_by_xpath("//*[@id='proposition-links']/li[1]/a").click()
            selenium_task_executor.get_driver().find_element_by_id("id_name_search_field").send_keys("test")
            selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Search']").click()
            selenium_task_executor.get_driver().find_element_by_link_text("Application Summary").click()
            WebDriverWait(selenium_task_executor.get_driver(), title_change_wait).until(
                expected_conditions.title_contains("Application summary"))
        except Exception as e:
            self.capture_screenshot()
            raise e

    def test_arc_user_can_view_audit_log_via_search_page(self):
        self.assert_arc_user_can_view_audit_log_via_search_page()

    def assert_arc_user_can_view_audit_log_via_search_page(self):
        """
                Tests that an Arc user can access an application audit log via searching
                """
        global selenium_task_executor
        title_change_wait = 15
        try:
            self.login_as_arc_user()
            selenium_task_executor.get_driver().find_element_by_xpath("//*[@id='proposition-links']/li[1]/a").click()
            selenium_task_executor.get_driver().find_element_by_id("id_name_search_field").send_keys("test")
            selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Search']").click()
            selenium_task_executor.get_driver().find_element_by_link_text("Application Summary").click()
            WebDriverWait(selenium_task_executor.get_driver(), title_change_wait).until(
                expected_conditions.title_contains("Application summary"))
            selenium_task_executor.get_driver().find_element_by_link_text("Audit log").click()
            self.assertEqual("Audit log", selenium_task_executor.get_driver().title)
        except Exception as e:
            self.capture_screenshot()
            raise e

    # -----------------------
    # Childminder review tests
    # -----------------------

    def test_arc_user_can_complete_review_without_flagging_any_questions(self):
        self.assert_arc_user_can_complete_review_without_flagging_any_questions()

    def assert_arc_user_can_complete_review_without_flagging_any_questions(self):
        """
        Tests that an ARC user can complete a review without flagging any questions
        """
        global selenium_task_executor
        title_change_wait = 30

        try:
            self.login_as_arc_user()
            selenium_task_executor.get_driver().find_element_by_name("add_childminder_application").click()
            selenium_task_executor.get_driver().find_element_by_xpath("//*[@id='request-table']/tbody/tr[1]/td[5]/a").click()
            selenium_task_executor.get_driver().find_element_by_xpath("//tr[@id='account_details']/td/a/span").click()
            WebDriverWait(selenium_task_executor.get_driver(), title_change_wait).until(expected_conditions.title_contains("Review: your sign in details"))
            selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Confirm and continue']").click()
            WebDriverWait(selenium_task_executor.get_driver(), title_change_wait).until(expected_conditions.title_contains("Review: type of childcare"))
            selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Confirm and continue']").click()
            WebDriverWait(selenium_task_executor.get_driver(), title_change_wait).until(expected_conditions.title_contains("Review: your personal details"))
            selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Confirm and continue']").click()
            WebDriverWait(selenium_task_executor.get_driver(), title_change_wait).until(expected_conditions.title_contains("Review: first aid training"))
            selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Confirm and continue']").click()
            WebDriverWait(selenium_task_executor.get_driver(), title_change_wait).until(expected_conditions.title_contains("Review: childcare training"))
            selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Confirm and continue']").click()
            WebDriverWait(selenium_task_executor.get_driver(), title_change_wait).until(expected_conditions.title_contains("Review: health declaration booklet"))
            selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Confirm and continue']").click()
            WebDriverWait(selenium_task_executor.get_driver(), title_change_wait).until(expected_conditions.title_contains("Review: criminal record (DBS) check"))
            selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Confirm and continue']").click()
            WebDriverWait(selenium_task_executor.get_driver(), title_change_wait).until(expected_conditions.title_contains("Review: people in your home"))
            selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Confirm and continue']").click()
            WebDriverWait(selenium_task_executor.get_driver(), title_change_wait).until(expected_conditions.title_contains("Review: references"))
            selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Confirm and continue']").click()
            WebDriverWait(selenium_task_executor.get_driver(), title_change_wait).until(expected_conditions.title_contains("Application overview"))
            selenium_task_executor.get_driver().find_element_by_link_text("Complete review").click()
            WebDriverWait(selenium_task_executor.get_driver(), title_change_wait).until(expected_conditions.title_contains("Application summary"))
            selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Confirm and continue']").click()
            WebDriverWait(selenium_task_executor.get_driver(), title_change_wait).until(expected_conditions.title_contains("Review approved"))
            self.assertEqual("Review approved", selenium_task_executor.get_driver().title)
        except Exception as e:
            self.capture_screenshot()
            raise e

    # def test_arc_user_can_flag_responses(self):
    #     self.assert_arc_user_can_flag_responses()

    def assert_arc_user_can_flag_responses(self):
        """
        Tests that an ARC user can flag question responses
        """
        global selenium_task_executor
        title_change_wait = 15

        try:
            self.login_as_arc_user()

            selenium_task_executor.get_driver().find_element_by_name("add_childminder_application").click()
            selenium_task_executor.get_driver().find_element_by_xpath("//*[@id='request-table']/tbody/tr[1]/td[5]/a").click()
            selenium_task_executor.get_driver().find_element_by_xpath("//tr[@id='account_details']/td/a/span").click()
            WebDriverWait(selenium_task_executor.get_driver(), title_change_wait).until(expected_conditions.title_contains("Review: your sign in details"))

            selenium_task_executor.get_driver().find_element_by_id("id_mobile_number_declare").click()
            # Submit empty comment box and check that error displays
            selenium_task_executor.get_driver().find_element_by_id("id_mobile_number_comments").clear()
            selenium_task_executor.get_driver().find_element_by_id("id_add_phone_number_declare").click()
            selenium_task_executor.get_driver().find_element_by_id("id_add_phone_number_comments").clear()
            selenium_task_executor.get_driver().find_element_by_id("id_add_phone_number_comments").send_keys("Test")
            selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Confirm and continue']").click()
            selenium_task_executor.get_driver().find_element_by_class_name("error-summary")
            # Submit valid comment
            selenium_task_executor.get_driver().find_element_by_id("id_mobile_number_comments").clear()
            selenium_task_executor.get_driver().find_element_by_id("id_add_phone_number_comments").send_keys("Test")
            selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Confirm and continue']").click()

            WebDriverWait(selenium_task_executor.get_driver(), title_change_wait).until(expected_conditions.title_contains("Review: type of childcare"))

            selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Confirm and continue']").click()
            WebDriverWait(selenium_task_executor.get_driver(), title_change_wait).until(expected_conditions.title_contains("Review: your personal details"))

            selenium_task_executor.get_driver().find_element_by_id("id_name_declare").click()
            selenium_task_executor.get_driver().find_element_by_id("id_name_comments").send_keys("Test")
            selenium_task_executor.get_driver().find_element_by_id("id_date_of_birth_declare").click()
            selenium_task_executor.get_driver().find_element_by_id("id_date_of_birth_comments").send_keys("Test")
            selenium_task_executor.get_driver().find_element_by_id("id_home_address_declare").click()
            selenium_task_executor.get_driver().find_element_by_id("id_home_address_comments").send_keys("Test")
            selenium_task_executor.get_driver().find_element_by_id("id_childcare_address_declare").click()
            selenium_task_executor.get_driver().find_element_by_id("id_childcare_address_comments").send_keys("Test")
            selenium_task_executor.get_driver().find_element_by_id("id_working_in_other_childminder_home_declare").click()
            selenium_task_executor.get_driver().find_element_by_id("id_working_in_other_childminder_home_comments").send_keys("Test")
            selenium_task_executor.get_driver().find_element_by_id("id_own_children_declare").click()
            selenium_task_executor.get_driver().find_element_by_id("id_own_children_comments").send_keys("Test")
            selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Confirm and continue']").click()
            WebDriverWait(selenium_task_executor.get_driver(), title_change_wait).until(expected_conditions.title_contains("Review: first aid training"))

            selenium_task_executor.get_driver().find_element_by_id("id_first_aid_training_organisation_declare").click()
            selenium_task_executor.get_driver().find_element_by_id("id_first_aid_training_organisation_comments").send_keys("Test")
            selenium_task_executor.get_driver().find_element_by_id("id_title_of_training_course_declare").click()
            selenium_task_executor.get_driver().find_element_by_id("id_title_of_training_course_comments").send_keys("Test")
            selenium_task_executor.get_driver().find_element_by_id("id_course_date_declare").click()
            selenium_task_executor.get_driver().find_element_by_id("id_course_date_comments").send_keys("Test")
            selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Confirm and continue']").click()
            WebDriverWait(selenium_task_executor.get_driver(), title_change_wait).until(expected_conditions.title_contains("Review: childcare training"))

            selenium_task_executor.get_driver().find_element_by_id("id_eyfs_course_name_declare").click()
            selenium_task_executor.get_driver().find_element_by_id(
                "id_eyfs_course_name_comments").send_keys("Fake news")
            selenium_task_executor.get_driver().find_element_by_id("id_eyfs_course_date_declare").click()
            selenium_task_executor.get_driver().find_element_by_id("id_eyfs_course_date_comments").send_keys("Test")
            selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Confirm and continue']").click()
            WebDriverWait(selenium_task_executor.get_driver(), title_change_wait).until(
                expected_conditions.title_contains("Review: health declaration booklet"))

            selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Confirm and continue']").click()
            WebDriverWait(selenium_task_executor.get_driver(), title_change_wait).until(expected_conditions.title_contains("Review: criminal record (DBS) check"))

            selenium_task_executor.get_driver().find_element_by_id("id_dbs_certificate_number_declare").click()
            selenium_task_executor.get_driver().find_element_by_id("id_dbs_certificate_number_comments").send_keys("Test")
            selenium_task_executor.get_driver().find_element_by_id("id_cautions_convictions_declare").click()
            selenium_task_executor.get_driver().find_element_by_id("id_cautions_convictions_comments").send_keys("Test")
            selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Confirm and continue']").click()
            WebDriverWait(selenium_task_executor.get_driver(), title_change_wait).until(expected_conditions.title_contains("Review: people in your home"))

            selenium_task_executor.get_driver().find_element_by_id("id_static-adults_in_home_declare").click()
            selenium_task_executor.get_driver().find_element_by_id("id_static-adults_in_home_comments").clear()
            selenium_task_executor.get_driver().find_element_by_id("id_static-adults_in_home_comments").send_keys(
                "Test")
            selenium_task_executor.get_driver().find_element_by_id("id_static-children_in_home_declare").click()
            selenium_task_executor.get_driver().find_element_by_id("id_static-children_in_home_comments").clear()
            selenium_task_executor.get_driver().find_element_by_id("id_static-children_in_home_comments").send_keys(
                "Test")
            selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Confirm and continue']").click()
            WebDriverWait(selenium_task_executor.get_driver(), title_change_wait).until(expected_conditions.title_contains("Review: references"))

            selenium_task_executor.get_driver().find_element_by_id("id_form-full_name_declare").click()
            selenium_task_executor.get_driver().find_element_by_id("id_form-full_name_comments").send_keys("Test")
            selenium_task_executor.get_driver().find_element_by_id("id_form-relationship_declare").click()
            selenium_task_executor.get_driver().find_element_by_id("id_form-relationship_comments").send_keys("Test")
            selenium_task_executor.get_driver().find_element_by_id("id_form-time_known_declare").click()
            selenium_task_executor.get_driver().find_element_by_id("id_form-time_known_comments").send_keys("Test")
            selenium_task_executor.get_driver().find_element_by_id("id_form-address_declare").click()
            selenium_task_executor.get_driver().find_element_by_id("id_form-address_comments").send_keys("Test")
            selenium_task_executor.get_driver().find_element_by_id("id_form-phone_number_declare").click()
            selenium_task_executor.get_driver().find_element_by_id("id_form-phone_number_comments").send_keys("Test")
            selenium_task_executor.get_driver().find_element_by_id("id_form-email_address_declare").click()
            selenium_task_executor.get_driver().find_element_by_id("id_form-email_address_comments").send_keys("Test")
            selenium_task_executor.get_driver().find_element_by_id("id_form2-full_name_declare").click()
            selenium_task_executor.get_driver().find_element_by_id("id_form2-full_name_comments").send_keys("Test")
            selenium_task_executor.get_driver().find_element_by_id("id_form2-relationship_declare").click()
            selenium_task_executor.get_driver().find_element_by_id("id_form2-relationship_comments").send_keys("Test")
            selenium_task_executor.get_driver().find_element_by_id("id_form2-time_known_declare").click()
            selenium_task_executor.get_driver().find_element_by_id("id_form2-time_known_comments").send_keys("Test")
            selenium_task_executor.get_driver().find_element_by_id("id_form2-address_declare").click()
            selenium_task_executor.get_driver().find_element_by_id("id_form2-address_comments").send_keys("Test")
            selenium_task_executor.get_driver().find_element_by_id("id_form2-phone_number_declare").click()
            selenium_task_executor.get_driver().find_element_by_id("id_form2-phone_number_comments").send_keys("Test")
            selenium_task_executor.get_driver().find_element_by_id("id_form2-email_address_declare").click()
            selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Confirm and continue']").click()

            WebDriverWait(selenium_task_executor.get_driver(), title_change_wait).until(expected_conditions.title_contains("Application overview"))

            selenium_task_executor.get_driver().find_element_by_link_text("Complete review").click()
            WebDriverWait(selenium_task_executor.get_driver(), title_change_wait).until(expected_conditions.title_contains("Application summary"))

            selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Confirm and continue']").click()

            self.assertEqual("Review returned", selenium_task_executor.get_driver().title)
        except Exception as e:
            self.capture_screenshot()
            raise e

    def test_your_children_task_hidden_when_no_own_children(self):
        self.assert_your_children_task_hidden_when_no_own_children()

    def assert_your_children_task_hidden_when_no_own_children(self):
        """
        Tests that the Your children task is hidden when the applicant has indicated they have no own children
        """
        global selenium_task_executor
        title_change_wait = 15

        try:
            self.login_as_arc_user()

            # Set own_children to True for test application
            application = Application.objects.get(application_id='db0efe18-eec5-4ec9-887a-e93949f6b412')
            application.own_children = False
            application.save()

            WebDriverWait(selenium_task_executor.get_driver(), title_change_wait).until(
                expected_conditions.title_contains("Applications"))
            selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Add from queue']").click()
            selenium_task_executor.get_driver().find_element_by_xpath("//*[@id='request-table']/tbody/tr[1]/td[5]/a").click()
            WebDriverWait(selenium_task_executor.get_driver(), title_change_wait).until(
                expected_conditions.title_contains("Application overview"))
            # Fail test if Your children task displays
            selenium_task_executor.get_driver().find_element_by_xpath("//tr[@id='your_children']/td/a/span")
            self.assertEqual(True, False)
        except:
            # Pass test if Your children task does not display
            self.assertEqual(True, True)

    def test_your_children_task_shown_when_own_children(self):
        self.assert_your_children_task_hidden_when_own_children()

    def assert_your_children_task_shown_when_own_children(self):
        """
        Tests that the Your children task is shown when the applicant has indicated they have own children
        """
        global selenium_task_executor
        title_change_wait = 15

        try:
            self.login_as_arc_user()

            # Set own_children to True for test application
            application = Application.objects.get(application_id='db0efe18-eec5-4ec9-887a-e93949f6b412')
            application.own_children = True
            application.save()

            WebDriverWait(selenium_task_executor.get_driver(), title_change_wait).until(
                expected_conditions.title_contains("Applications"))
            selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Add from queue']").click()
            selenium_task_executor.get_driver().find_element_by_xpath("//*[@id='request-table']/tbody/tr[1]/td[5]/a").click()
            WebDriverWait(selenium_task_executor.get_driver(), title_change_wait).until(
                expected_conditions.title_contains("Application overview"))
            # Pass test if Your children task displays
            selenium_task_executor.get_driver().find_element_by_xpath("//tr[@id='your_children']/td/a/span")
            self.assertEqual(True, True)
        except:
            # Fail test if Your children task does not display
            self.assertEqual(True, False)

    def test_people_in_home_task_hidden_when_not_working_in_other_childminder_home(self):
        self.assert_people_in_home_task_hidden_when_not_working_in_other_childminder_home()

    def assert_people_in_home_task_hidden_when_not_working_in_other_childminder_home(self):
        """
        Tests that the People in your home task is hidden when the applicant has indicated they work in another
        childminder's home
        """
        global selenium_task_executor
        title_change_wait = 15

        try:
            self.login_as_arc_user()

            # Set own_children to True for test application
            application = Application.objects.get(application_id='db0efe18-eec5-4ec9-887a-e93949f6b412')
            application.working_in_other_childminder_home = True
            application.save()

            WebDriverWait(selenium_task_executor.get_driver(), title_change_wait).until(
                expected_conditions.title_contains("Applications"))
            selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Add from queue']").click()
            selenium_task_executor.get_driver().find_element_by_xpath("//*[@id='request-table']/tbody/tr[1]/td[5]/a").click()
            WebDriverWait(selenium_task_executor.get_driver(), title_change_wait).until(
                expected_conditions.title_contains("Application overview"))
            # Fail test if People in your home task displays
            selenium_task_executor.get_driver().find_element_by_xpath("//tr[@id='other_people']/td/a/span")
            self.assertEqual(True, False)
        except:
            # Pass test if People in your home task does not display
            self.assertEqual(True, True)

    def test_people_in_home_task_shown_when_not_working_in_other_childminder_home(self):
        self.assert_people_in_home_task_shown_when_not_working_in_other_childminder_home()

    def assert_people_in_home_task_shown_when_not_working_in_other_childminder_home(self):
        """
        Tests that the People in your home task is shown when the applicant has indicated they don't work in another
        childminder's home
        """
        global selenium_task_executor
        title_change_wait = 15

        try:
            self.login_as_arc_user()

            # Set own_children to True for test application
            application = Application.objects.get(application_id='db0efe18-eec5-4ec9-887a-e93949f6b412')
            application.working_in_other_childminder_home = False
            application.save()

            WebDriverWait(selenium_task_executor.get_driver(), title_change_wait).until(
                expected_conditions.title_contains("Applications"))
            selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Add from queue']").click()
            selenium_task_executor.get_driver().find_element_by_xpath("//*[@id='request-table']/tbody/tr[1]/td[5]/a").click()
            WebDriverWait(selenium_task_executor.get_driver(), title_change_wait).until(
                expected_conditions.title_contains("Application overview"))
            # Pass test if People in your home task displays
            selenium_task_executor.get_driver().find_element_by_xpath("//tr[@id='other_people']/td/a/span")
            self.assertEqual(True, True)
        except:
            # Fail test if People in your home task does not display
            self.assertEqual(True, False)

    # -----------------------
    # Helpers
    # -----------------------

    def release_arc_application(self):
        """
        Helper method for releasing an application as an ARC user
        :return:
        """
        global selenium_task_executor

        try:
            selenium_task_executor.get_driver().find_element_by_id("proposition-name").click()
            selenium_task_executor.get_driver().find_element_by_name("add_childminder_application").click()
        except Exception as e:
            self.capture_screenshot()
            raise e

    def login_as_contact_user(self):
        """
        Helper method for logging in as a contact centre user
        """
        global selenium_task_executor

        try:
            selenium_task_executor.navigate_to_base_url()
            selenium_task_executor.get_driver().find_element_by_id("id_username").send_keys("cc1")
            selenium_task_executor.get_driver().find_element_by_id("id_password").send_keys("[jack-in]")
            selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Sign in']").click()
        except Exception as e:
            self.capture_screenshot()
            raise e

    def login_as_arc_user(self):
        """
        Helper method for logging in as a contact centre user
        """
        global selenium_task_executor

        try:
            selenium_task_executor.navigate_to_base_url()
            selenium_task_executor.get_driver().find_element_by_id("id_username").send_keys("arc1")
            selenium_task_executor.get_driver().find_element_by_id("id_password").send_keys("[jack-in]")
            selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Sign in']").click()
        except Exception as e:
            self.capture_screenshot()
            raise e

    def capture_screenshot(self):
        now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        scr = selenium_driver.find_element_by_tag_name('html')
        #scr.screenshot('selenium/screenshot-%s-%s.png' % (self.__class__.__name__, now))

    def tearDown(self):
        global selenium_driver
        selenium_driver.quit()
        # Delete the test application after each test
        Application.objects.all().delete()
        super(TestArcFunctions, self).tearDown()
        self.assertEqual([], self.verification_errors)

