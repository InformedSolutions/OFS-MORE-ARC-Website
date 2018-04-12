"""
Selenium test cases for the Childminder service
"""

import os
import random
from datetime import datetime

from django.test import LiveServerTestCase, override_settings, tag
from selenium import webdriver

from .selenium_task_executor import SeleniumTaskExecutor

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

        base_url = os.environ.get('DJANGO_LIVE_TEST_SERVER_ADDRESS')

        if os.environ.get('LOCAL_SELENIUM_DRIVER') == 'True':
            # If running on a windows host, make sure to drop the
            # geckodriver.exe into your Python/Scripts installation folder
            selenium_driver = webdriver.Firefox()
        else:
            # If not using local driver, default requests to a selenium grid server
            selenium_driver = webdriver.Remote(
                command_executor=os.environ['SELENIUM_HOST'],
                desired_capabilities={'platform': 'ANY', 'browserName': 'firefox', 'version': ''}
            )

        selenium_driver.maximize_window()
        selenium_driver.implicitly_wait(5)

        self.verification_errors = []
        self.accept_next_alert = True

        selenium_task_executor = SeleniumTaskExecutor(selenium_driver, base_url)

        super(TestArcFunctions, self).setUp()

    # Test wrappers are used here to allow ordering of tests. Tests are also split to produce more
    # meaningful test report outputs in the event of a failure.
    def test_can_login_as_arc_user(self):
        self.assert_can_login_as_arc_user()

    def assert_can_login_as_arc_user(self):
        """
        Tests that an ARC user can login
        """
        global selenium_task_executor

        try:
            selenium_task_executor.navigate_to_base_url()
            selenium_task_executor.get_driver().find_element_by_id("id_username").send_keys("arc1")
            selenium_task_executor.get_driver().find_element_by_id("id_password").send_keys("[jack-in]")
            selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Log in']").click()
            self.assertEqual("Logout", selenium_task_executor.get_driver().find_element_by_link_text("Logout").text)
            selenium_task_executor.get_driver().find_element_by_link_text("Logout").click()
        except Exception as e:
            self.capture_screenshot()
            raise e

    def test_can_login_as_contact_centre_user(self):
        self.assert_can_login_as_contact_centre_user()

    def assert_can_login_as_contact_centre_user(self):
        """
        Tests that an ARC user can login
        """
        global selenium_task_executor

        try:
            selenium_task_executor.navigate_to_base_url()
            selenium_task_executor.get_driver().find_element_by_id("id_username").send_keys("cc1")
            selenium_task_executor.get_driver().find_element_by_id("id_password").send_keys("[jack-in]")
            selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Log in']").click()
            self.assertEqual("Logout", selenium_task_executor.get_driver().find_element_by_link_text("Logout").text)
            selenium_task_executor.get_driver().find_element_by_link_text("Logout").click()
        except Exception as e:
            self.capture_screenshot()
            raise e

    def capture_screenshot(self):
        now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        scr = selenium_driver.find_element_by_tag_name('html')
        scr.screenshot('selenium/screenshot-%s-%s.png' % (self.__class__.__name__, now))

    def tearDown(self):
        global selenium_driver
        selenium_driver.quit()
        super(TestArcFunctions, self).tearDown()
        self.assertEqual([], self.verification_errors)

