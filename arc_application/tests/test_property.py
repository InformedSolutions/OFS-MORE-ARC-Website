import hypothesis
from hypothesis import given, strategies

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.test import RequestFactory

from arc_application.review_util import build_url


class PropertyTests(hypothesis.extra.django.TestCase):

    def setUp(self):
        """
        setUp method taken from the ArcSummaryTest class.
        :return: None
        """
        # Every test needs access to the request factory.
        self.request_factory = RequestFactory()
        self.user = User.objects.create_user(
            username='arc_test', email='test@test.com', password='my_secret')
        g = Group.objects.create(name=settings.ARC_GROUP)
        g.user_set.add(self.user)

        global arc_test_user
        arc_test_user = self.user

        self.user = User.objects.create_user(
            username='cc_test', email='testing@test.com', password='my_secret')
        g2 = Group.objects.create(name=settings.CONTACT_CENTRE)
        g2.user_set.add(self.user)

        global cc_test_user
        cc_test_user = self.user

    @given(strategies.dictionaries(strategies.text(), strategies.text()))
    def test_build_url(self, test_dict):
        """
        Property test for the build_url function.

        This will test that the build_url function can be passed a randomly generated dictionary as url variables,
        generate a url and still retrieve a 200 code when rendering the login page with those additional url variables.

        :param test_dict: Randomly generated dictionary to be passed as variables to build_url's url.
        :return: None
        """
        target_url = build_url('login', get=test_dict)
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 200)
