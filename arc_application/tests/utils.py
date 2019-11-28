import datetime
import unittest

import django
from lxml import etree
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.models import User, Group

from ..models import *


class StubIdentityGatewayActions:
    """
    Stub that returns static data for identity gateway endpoints. Can be instantiated, tweaked and discarded for
    each test
    """
    def __init__(self):
        self.identity_record = {
            'email': 'test@informed.com',
            'application_id': 'a4e6633f-5339-4de5-ae03-69c71fd008b3',
            'magic_link_sms': '12345',
            'sms_resend_attempts': 0,
            'mobile_number': '000000000012',
            'magic_link_email': 'ABCDEFGHIJKL',
            'add_phone_number': '',
        }
        self.identity_read_response = self.make_ok_response(self.identity_record)
        self.identity_list_response = self.make_ok_response()
        self.identity_create_response = self.make_ok_response()
        self.identity_patch_response = self.make_ok_response()
        self.identity_put_response = self.make_ok_response()
        self.identity_delete_response = self.make_ok_response()

    def list(self, *args, **kwargs):
        return self.identity_list_response

    def read(self, *args, **kwargs):
        return self.identity_read_response

    def create(self, *args, **kwargs):
        return self.identity_create_response

    def patch(self, *args, **kwargs):
        return self.identity_patch_response

    def put(self, *args, **kwargs):
        return self.identity_put_response

    def delete(self, *args, **kwargs):
        return self.identity_delete_response

    def make_ok_response(self, record=None):
        resp = HttpResponse()
        resp.status_code = 200
        resp.record = record if record is not None else {}
        return resp


class StubNannyGatewayActions:
    """
    Stub that returns static data for nanny gateway endpoints. Can be instantiated, tweaked and discarded for
    each test
    """

    def __init__(self):
        self.nanny_application = {
            'application_status': 'DRAFTING',
            'application_id': '998fd8ec-b96b-4a71-a1a1-a7a3ae186729',
            'application_type': '',
            'cygnum_urn': '',
            'login_details_status': 'COMPLETED',
            'login_details_arc_flagged': False,
            'personal_details_status': 'NOT_STARTED',
            'personal_details_arc_flagged': False,
            'childcare_address_status': 'COMPLETED',
            'childcare_address_arc_flagged': False,
            'first_aid_status': 'COMPLETED',
            'first_aid_arc_flagged': False,
            'childcare_training_status': 'NOT_STARTED',
            'childcare_training_arc_flagged': False,
            'dbs_status': 'NOT_STARTED',
            'dbs_arc_flagged': False,
            'insurance_cover_status': 'COMPLETED',
            'insurance_cover_arc_flagged': False,
            'declarations_status': 'NOT STARTED',
            'share_info_declare': True,
            'follow_rules': None,
            'information_correct_declare': None,
            'change_declare': None,
            'date_created': None,
            'date_updated': '2018-07-31 17:20:46.011717+00',
            'date_accepted': None,
            'date_submitted': '2018-07-31 17:20:46.011717+00',
            'application_reference': 'NA',
            'ofsted_visit_email_sent': None,
            'address_to_be_provided': True,
        }
        self.nanny_application_read_response = self.make_response(record=self.nanny_application)

        self.personal_details_record = {
            'application_id': '998fd8ec-b96b-4a71-a1a1-a7a3ae186729',
            'personal_detail_id': '9835bf4b-9ba9-4162-a25b-4c56e7d33d67',
            'title': 'The',
            'first_name': 'Dark Lord',
            'middle_names': '',
            'last_name': 'Selenium',
            'date_of_birth': '2000-01-01',
            'known_to_social_services': True,
            'reasons_known_to_social_services': 'An IMPORTANT reason'
        }
        self.personal_details_read_response = self.make_response(record=self.personal_details_record)

        self.previous_registration_record = {
            'application_id': '998fd8ec-b96b-4a71-a1a1-a7a3ae186729',
            'previous_registration_id': '9835bf3b-8ba9-4162-a25b-4c55e7d33d69',
            'previous_registration': True,
            'individual_id': '12345567',
            'five_years_in_UK': True
        }
        self.previous_registration_read_response = self.make_response(record=self.previous_registration_record)

        self.childcare_training_record = {
            'application_id': '998fd8ec-b96b-4a71-a1a1-a7a3ae186729',
            'childcare_training_id': '9835bf3b-8ba9-4162-a25b-4c55e7d33d69',
            'level_2_training': False,
            'common_core_training': False,
            'no_training': False
        }
        self.childcare_training_read_response = self.make_response(record=self.childcare_training_record)

        self.dbs_record = {
            'application_id': '998fd8ec-b96b-4a71-a1a1-a7a3ae186729',
            'dbs_id': '9835bf3b-8ba9-4162-a25b-4c55e7d33d77',
            'lived_abroad': True,
            'is_ofsted_dbs': True,
            'within_three_months': False,
            'enhanced_check': None,
            'on_dbs_update_service': True,
            'dbs_number': '000000000012',
        }
        self.dbs_check_read_response = self.make_response(record=self.dbs_record)

        self.previous_name_record = {
            'application_id': '998fd8ec-b96b-4a71-a1a1-a7a3ae186729',
            'previous_name_id': '9935bf3b-8ba9-4162-a25b-4c55e7d33d67',
            'first_name': 'Robin',
            'middle_names': '',
            'last_name': 'Hood',
            'start_day': 1,
            'start_month': 12,
            'start_year': 2003,
            'end_day': 3,
            'end_month': 12,
            'end_year': 2004,
            'order': 0
        }
        self.previous_name_read_response = self.make_response(record=self.previous_name_record)

        self.home_address_record = {
            'application_id': '998fd8ec-b96b-4a71-a1a1-a7a3ae186729',
            'home_address_id': '9935bf3b-8ba9-4162-a25b-4c55e7d33d67',
            'street_line1': 'Test',
            'street_line2': None,
            'town': 'Middle Earth',
            'county': None,
            'postcode': 'WA14 4PA',
            'childcare_address': False,
        }
        self.home_address_read_response = self.make_response(record=self.home_address_record)

        self.previous_address_record = {
            'previous_address_id': '88888888-4444-4444-4444-121212121212',
            'person_id': '998fd8ec-b96b-4a71-a1a1-a7a3ae186729',
            'person_type': 'APPLICANT',
            'street_line1': '1 Street Road',
            'street_line2': '',
            'town': 'Cityston',
            'county': 'Greater Countyshire',
            'country': '',
            'postcode': 'M9 9MP',
            'moved_in_date': '2016-06-02',
            'moved_out_date': '2018-02-23',
            'order': 0,
        }
        self.previous_address_read_response = self.make_response(record=self.previous_address_record)
        self.previous_address_list_response = self.make_response(record=[self.previous_address_record])

        self.childcare_address_record = [
            {
                'application_id': '998fd8ec-b96b-4a71-a1a1-a7a3ae186729',
                'childcare_address_id': '9835bf3b-8aa9-4162-a25b-4c55e7d33d67',
                'street_line1': 'Test',
                'street_line2': None,
                'town': 'New New York',
                'county': None,
                'postcode': 'WA14 4PA',
            },
            {
                'application_id': '998fd8ec-b96b-4a71-a1a1-a7a3ae186729',
                'childcare_address_id': '9835bf3b-8aa9-4162-a25b-4c55e7d33d68',
                'street_line1': 'Buckingham Palace',
                'street_line2': None,
                'town': 'London',
                'county': None,
                'postcode': 'SW1 1AA',
            }
        ]
        self.childcare_address_read_response = self.make_response(record=self.childcare_address_record)

        self.first_aid_record = {
            'application_id': '998fd8ec-b96b-4a71-a1a1-a7a3ae186729',
            'first_aid_id': '9835bf3b-8ba9-4162-a25b-4c56e7d33d67',
            'training_organisation': 'St Johns Ambulance',
            'course_title': 'Pediatric First Aid',
            'course_date': '2016-03-31'
        }
        self.first_aid_read_response = self.make_response(record=self.first_aid_record)

        self.insurance_cover_record = {
            'application_id': '998fd8ec-b96b-4a71-a1a1-a7a3ae186729',
            'insurance_cover_id': '9835bf3b-9ba9-4162-a25b-4c56e7d33d67',
            'public_liability': True
        }
        self.insurance_cover_read_response = self.make_response(record=self.insurance_cover_record)

        self.declaration_record = {
            'application_id': '998fd8ec-b96b-4a71-a1a1-a7a3ae186729',
            'follow_rules': True,
            'share_info_declare': True,
            'information_correct_declare': True,
            'change_declare': True,
        }
        self.declaration_read_response = self.make_response(record=self.declaration_record)

        self.arc_comments_read_response = self.make_response(404)
        self.arc_comments_list_response = self.make_response(404)

        self.timeline_log_record = {}
        self.timeline_log_read_response = self.make_response(record=self.timeline_log_record)

        self.default_list_response = self.make_response()
        self.default_read_response = self.make_response()
        self.default_create_response = self.make_response()
        self.default_patch_response = self.make_response()
        self.default_put_response = self.make_response()
        self.default_delete_response = self.make_response()

        self.endpoint_mapping = {
            'application': 'nanny_application',
            'applicant-personal-details': 'personal_details',
            'previous-registration-details': 'previous_registration',
            'childcare-training': 'childcare_training',
            'childcare-address': 'childcare_address',
            'applicant-home-address': 'home_address',
            'dbs-check': 'dbs_check',
            'first-aid': 'first_aid',
            'insurance-cover': 'insurance_cover',
            'declaration': 'declaration',
            'arc-comments': 'arc_comments',
            'timeline-log': 'timeline_log',
            'previous-name': 'previous_name',
            'previous-address': 'previous_address',
        }

    def list(self, endpoint, *_, **__):
        return getattr(self, '{}_list_response'.format(self.endpoint_mapping[endpoint]), self.default_list_response)

    def read(self, endpoint, *_, **__):
        return getattr(self, '{}_read_response'.format(self.endpoint_mapping[endpoint]), self.default_read_response)

    def create(self, endpoint, *_, **__):
        return getattr(self, '{}_create_response'.format(self.endpoint_mapping[endpoint]), self.default_create_response)

    def patch(self, endpoint, *_, **__):
        return getattr(self, '{}_patch_response'.format(self.endpoint_mapping[endpoint]), self.default_patch_response)

    def put(self, endpoint, *_, **__):
        return getattr(self, '{}_put_response'.format(self.endpoint_mapping[endpoint]), self.default_put_response)

    def delete(self, endpoint, *_, **__):
        return getattr(self, '{}_delete_response'.format(self.endpoint_mapping[endpoint]), self.default_delete_response)

    # noinspection PyMethodMayBeStatic
    def make_response(self, status=200, record=None):
        resp = HttpResponse()
        resp.status_code = status
        resp.record = record if record is not None else {}
        return resp

class StubHMGatewayActions:
    """
    Stub that returns static data for household member gateway endpoints. Can be instantiated, tweaked and discarded for
    each test
    """

    def __init__(self):
        self.dpa_auth_record = {
            "token_id": "51cdabff-a9c5-4032-bf50-0c8d1dd90888",
            "URN": "EY456721",
            "date_of_birth_day": 25,
            "date_of_birth_month": 5,
            "date_of_birth_year": 1981,
            "postcode": "BH21 4AY",
            "individual_id": "1786117",
        }
        self.dpa_auth_read_response = self.make_response(record=self.dpa_auth_record)

        self.adult_record = {
            "adult_id": "ffc54793-4694-4d33-9d7b-e9aa8c0ad2a3",
            "date_of_birth": "1980-03-31",
            "get_full_name": "Adult Test Adults",
            "start_date": None,
            "end_date": None,
            "order": 1,
            "first_name": "Adult",
            "middle_names": "Test",
            "last_name": "Adults",
            "birth_day": 31,
            "birth_month": 3,
            "birth_year": 1980,
            "relationship": "Husband",
            "email": "test@test.com",
            "dbs_certificate_number": "",
            "lived_abroad": None,
            "military_base": None,
            "capita": None,
            "enhanced_check": None,
            "on_update": None,
            "certificate_information": "",
            "within_three_months": None,
            "token": None,
            "health_check_status": "To do",
            "email_resent": 0,
            "email_resent_timestamp": None,
            "validated": False,
            "current_treatment": None,
            "serious_illness": None,
            "known_to_council": None,
            "reasons_known_to_council_health_check": "",
            "hospital_admission": None,
            "name_start_day": None,
            "name_start_month": None,
            "name_start_year": None,
            "name_end_day": None,
            "name_end_month": None,
            "name_end_year": None,
            "token_id": "51cdabff-a9c5-4032-bf50-0c8d1dd90888",
            "adult_status": 'DRAFTING'
        }
        self.adult_read_response = self.make_response(record=self.adult_record)

        self.previous_registration_record = {
            'application_id': 'ffc54793-4694-4d33-9d7b-e9aa8c0ad2a3',
            'previous_registration_id': '9835bf4b-9ba9-4162-a25b-4c56e7d33d67',
            'previous_registration': True,
            'individual_id': '12345567',
            'five_years_in_UK': True
        }
        self.previous_registration_read_response = self.make_response(record=self.previous_registration_record)

        self.previous_name_record = {
            'application_id': 'ffc54793-4694-4d33-9d7b-e9aa8c0ad2a3',
            'previous_name_id': '9835bf4b-9ba9-4162-a25b-4c56e7d33d67',
            'first_name': 'Robin',
            'middle_names': '',
            'last_name': 'Hood',
            'start_day': 1,
            'start_month': 12,
            'start_year': 2003,
            'end_day': 3,
            'end_month': 12,
            'end_year': 2004,
            'order': 0
        }
        self.previous_name_read_response = self.make_response(record=self.previous_name_record)

        self.home_address_record = {
            'application_id': 'ffc54793-4694-4d33-9d7b-e9aa8c0ad2a3',
            'home_address_id': '9935bf3b-8ba9-4162-a25b-4c55e7d33d67',
            'street_line1': 'Test',
            'street_line2': None,
            'town': 'Middle Earth',
            'county': None,
            'postcode': 'WA14 4PA',
            'childcare_address': False,
        }
        self.home_address_read_response = self.make_response(record=self.home_address_record)

        self.previous_address_record = {
            'previous_address_id': '88888888-4444-4444-4444-121212121212',
            'person_id': '998fd8ec-b96b-4a71-a1a1-a7a3ae186729',
            'person_type': 'APPLICANT',
            'street_line1': '1 Street Road',
            'street_line2': '',
            'town': 'Cityston',
            'county': 'Greater Countyshire',
            'country': '',
            'postcode': 'M9 9MP',
            'moved_in_date': '2016-06-02',
            'moved_out_date': '2018-02-23',
            'order': 0,
        }
        self.previous_address_read_response = self.make_response(record=self.previous_address_record)
        self.previous_address_list_response = self.make_response(record=[self.previous_address_record])

        self.application_record = {
            "application_id": "3afa6904-074f-49c6-ade0-3abc9eea0111",
            "token_id": "51cdabff-a9c5-4032-bf50-0c8d1dd90888"
        }
        self.application_read_response = self.make_response(record=self.application_record)

        self.arc_comments_record = \
            {
                "review_id": "a4f5aafd-d985-42fc-a984-e12326307e8e",
                "token_id": "9aa5fe94-34d8-4263-9228-8e020774b5f2",
                "table_pk": "8a132ff0-ac62-47e1-9b24-662c30e66243",
                "endpoint_name": "adult",
                "field_name": "health_check_status",
                "comment": "Health questions status",
                "flagged": True
            },

        self.arc_comments_read_response = self.make_response(404)
        self.arc_comments_list_response = self.make_response(404)

        self.timeline_log_record = {}
        self.timeline_log_read_response = self.make_response(record=self.timeline_log_record)

        self.default_list_response = {
            'adult': self.make_response(record=[self.adult_record]),
            'arc-comments': self.arc_comments_list_response
        }
        self.default_read_response = self.make_response()
        self.default_create_response = self.make_response()
        self.default_patch_response = self.make_response()
        self.default_put_response = self.make_response()
        self.default_delete_response = self.make_response()

        self.endpoint_mapping = {
            'application': 'application',
            'dpa-auth': 'dpa_auth',
            'adult': 'adult',
            'arc-comments': 'arc_comments',
            'previous-name': 'previous_name',
            'previous-address': 'previous_address',
            'timeline-log': 'timeline_log',
        }

    def list(self, endpoint, *_, **__):
        return getattr(self, '{}_list_response'.format(self.endpoint_mapping[endpoint]), self.default_list_response[endpoint])

    def read(self, endpoint, *_, **__):
        return getattr(self, '{}_read_response'.format(self.endpoint_mapping[endpoint]), self.default_read_response)

    def create(self, endpoint, *_, **__):
        return getattr(self, '{}_create_response'.format(self.endpoint_mapping[endpoint]), self.default_create_response)

    def patch(self, endpoint, *_, **__):
        return getattr(self, '{}_patch_response'.format(self.endpoint_mapping[endpoint]), self.default_patch_response)

    def put(self, endpoint, *_, **__):
        return getattr(self, '{}_put_response'.format(self.endpoint_mapping[endpoint]), self.default_put_response)

    def delete(self, endpoint, *_, **__):
        return getattr(self, '{}_delete_response'.format(self.endpoint_mapping[endpoint]), self.default_delete_response)

    # noinspection PyMethodMayBeStatic
    def make_response(self, status=200, record=None):
        resp = HttpResponse()
        resp.status_code = status
        resp.record = record if record is not None else {}
        return resp

# CamelCase naming to match unittest module
def assertXPath(response, xpath):
    """
    Asserts that content described by the given xpath expression can be found in the given response's HTML

    :param response: The http response object
    :param xpath: An XPath expression to test for
    """
    result = _do_xpath(response, xpath)
    if result is None or (isinstance(result, list) and len(result) == 0):
        raise AssertionError('"{}" evaluated to {} but content expected'.format(xpath, repr(result)))


def assertNotXPath(response, xpath):
    """
    Asserts that no content can be found at the given xpath in the response's HTML

    :param response: The http response object
    :param xpath: An XPath expression to test for
    """
    result = _do_xpath(response, xpath)
    if result is not None and not (isinstance(result, list) and len(result) == 0):
        raise AssertionError('"{}" evaluated to {} but no content expected'.format(xpath, repr(result)))


def assertXPathValue(response, xpath, expected_value, strip=False):
    """
    Asserts that the given value can be found at the given xpath in the response's HTML

    :param response: The http response object
    :param xpath: An XPath expression to test for
    :param expected_value: The content expected to be found
    :param strip: (optional) Run results through str.strip to trim whitespace
    """
    if strip and not isinstance(expected_value, str):
        raise ValueError('strip parameter only applies to expected str type')

    result = _do_xpath(response, xpath)

    if strip:
        if isinstance(result, str):
            result = result.strip()
        elif isinstance(result, list):
            result = list(map(str.strip, result))
        else:
            raise AssertionError('Expected str or list to strip at "{}", but found {}'.format(xpath, repr(result)))

    if isinstance(result, list):
        found = expected_value in result
    else:
        found = result == expected_value

    if not found:
        raise AssertionError('Expected {} at "{}", but found {}'.format(repr(expected_value), xpath, repr(result)))


def assertXPathCount(response, xpath, expected_quantity):
    """
    Asserts that the given quantity of instances can be found in the response's HTML for the given xpath expression

    :param response: The http response object
    :param xpath: An XPath expression to test for
    :param expected_quantity: The number of instances expected to be found
    """
    result = _do_xpath(response, xpath)
    if len(result) != expected_quantity:
        raise AssertionError('Expected {} instances of "{}", found {}'.format(expected_quantity, xpath, len(result)))


def _do_xpath(response, xpath):
    tree = etree.fromstring(response.content, parser=etree.HTMLParser()).getroottree()
    return tree.xpath(xpath)


def assertView(response, expected_view_obj):
    expected_name = expected_view_obj if isinstance(expected_view_obj, str) else expected_view_obj.__name__
    actual_name = response.resolver_match.func.__name__
    if actual_name != expected_name:
        raise AssertionError('Expected view "{}", found view "{}"'.format(expected_name, actual_name))


def assertRedirectView(response, expected_view_obj):
    expected_name = expected_view_obj if isinstance(expected_view_obj, str) else expected_view_obj.__name__
    try:
        actual_name = django.urls.resolve(response.url).func.__name__
    except django.urls.exceptions.Resolver404:
        raise AssertionError('Redirect url "{}" did not resolve to a view'.format(response.url))
    if actual_name != expected_name:
        raise AssertionError('Expected redirect to view "{}", found view "{}"'.format(expected_name, actual_name))


def create_childminder_application(user_id=None):

    application = Application.objects.create(
        application_type='CHILDMINDER',
        application_id='da2265c2-2d65-4214-bfef-abcfe59b75aa',
        application_status='DRAFTING',
        cygnum_urn='',
        login_details_status='NOT_STARTED',
        login_details_arc_flagged=False,
        personal_details_status='NOT_STARTED',
        personal_details_arc_flagged=False,
        childcare_type_status='NOT_STARTED',
        childcare_type_arc_flagged=False,
        first_aid_training_status='NOT_STARTED',
        first_aid_training_arc_flagged=False,
        childcare_training_status='COMPLETED',
        childcare_training_arc_flagged=False,
        criminal_record_check_status='NOT_STARTED',
        criminal_record_check_arc_flagged=False,
        health_status='NOT_STARTED',
        health_arc_flagged=False,
        references_status='NOT_STARTED',
        references_arc_flagged=False,
        people_in_home_status='NOT_STARTED',
        people_in_home_arc_flagged=False,
        declarations_status='NOT_STARTED',
        adults_in_home=False,
        children_in_home=False,
        date_created=datetime.datetime.today(),
        date_updated=datetime.datetime.today(),
        date_accepted=None,
        reasons_known_to_social_services=None,
        known_to_social_services_pith=None,
        reasons_known_to_social_services_pith=None,
    )

    details = ApplicantPersonalDetails.objects.create(
        personal_detail_id='da2265c2-2d65-4214-bfef-abcfe59b75aa',
        application_id=application,
        birth_day='01',
        birth_month='01',
        birth_year='2001'
    )

    ChildcareType.objects.create(
        application_id=application,
        zero_to_five=True,
        five_to_eight=True,
        eight_plus=True,
        overnight_care=True
    )

    ApplicantHomeAddress.objects.create(
        home_address_id='da2265c2-2d65-4214-bfef-abcfe59b75aa',
        personal_detail_id=details,
        application_id=application,
        street_line1='1 Test Street',
        street_line2='',
        town='Testville',
        county='Testshire',
        country='Testland',
        postcode='WA14 4PX',
        current_address=True,
        childcare_address=True,
    )

    ApplicantName.objects.create(
        name_id='da2265c2-2d65-4214-bfef-abcfe59b75aa',
        personal_detail_id=details,
        application_id=application,
        current_name='True',
        first_name='Erik',
        middle_names='Tolstrup',
        last_name='Odense'
    )

    UserDetails.objects.create(
        login_id='8362d470-ecc9-4069-876b-9b3ddc2cae07',
        application_id=application,
        email='test@test.com',
    )

    FirstAidTraining.objects.create(
        first_aid_id='da2265c2-2d65-4214-bfef-abcfe59b75aa',
        application_id=application,
        training_organisation='Test First Aid',
        course_title='Test First Aid',
        course_day='01',
        course_month='01',
        course_year='2018',
        show_certificate=True,
        renew_certificate=True
    )

    ChildcareTraining.objects.create(
        eyfs_id='da2265c2-2d65-4214-bfef-abcfe59b75aa',
        application_id=application,
        eyfs_course_name='Test Childcare Training',
        eyfs_course_date_day=1,
        eyfs_course_date_month=2,
        eyfs_course_date_year=2018,
    )

    HealthDeclarationBooklet.objects.create(
        hdb_id='da2265c2-2d65-4214-bfef-abcfe59b75aa',
        application_id=application,
        send_hdb_declare=True,
    )

    CriminalRecordCheck.objects.create(
        criminal_record_id='da2265c2-2d65-4214-bfef-abcfe59b75aa',
        application_id=application,
        dbs_certificate_number='123456654321',
        cautions_convictions=True
    )

    AdultInHome.objects.create(
        adult_id='da2265c2-2d65-4214-bfef-abcfe59b75aa',
        application_id=application,
        adult=1,
        first_name='Test',
        middle_names='Test',
        last_name='Test',
        birth_day=1,
        birth_month=1,
        birth_year=1975,
        relationship='Test',
        dbs_certificate_number='123456789012',
    )

    ChildInHome.objects.create(
        child_id='da2265c2-2d65-4214-bfef-abcfe59b75aa',
        application_id=application,
        child='1',
        first_name='Test',
        middle_names='Test',
        last_name='Test',
        birth_day='01',
        birth_month='01',
        birth_year='1995',
        relationship='Test'
    )

    Reference.objects.create(
        reference_id='da2265c2-2d65-4214-bfef-abcfe59b75aa',
        application_id=application,
        reference='1',
        first_name='Test',
        last_name='Test',
        relationship='Test',
        years_known='1',
        months_known='1',
        street_line1='1 Test Street',
        street_line2='',
        town='Testville',
        county='Testshire',
        country='Testland',
        postcode='WA14 4PX',
        phone_number='07783446526',
        email='test@informed.com'
    )

    Reference.objects.create(
        reference_id='da2265c2-2d65-4214-bfef-abcfe59b75ab',
        application_id=application,
        reference='2',
        first_name='Test',
        last_name='Test',
        relationship='Test',
        years_known='1',
        months_known='1',
        street_line1='1 Test Street',
        street_line2='',
        town='Testville',
        county='Testshire',
        country='Testland',
        postcode='WA14 4PX',
        phone_number='07783446526',
        email='test@informed.com'
    )

    # create arc record and assign to specified user
    create_childminder_review(application.application_id, user_id)

    return application


def create_childminder_review(application_id, user_id=None):
    return Arc.objects.create(
        application_id=application_id,
        # user_id field is non-null and uses empty string when no user is assigned
        user_id=user_id if user_id is not None else '',
        app_type='Childminder',
    )


def create_nanny_review(application_id, user_id=None):
    return Arc.objects.create(
        application_id=application_id,
        # user_id field is non-null and uses empty string when no user is assigned
        user_id=user_id if user_id is not None else '',
        app_type='Nanny',
    )

def create_adult_review(application_id, user_id=None):
    return Arc.objects.create(
        application_id=application_id,
        # user_id field is non-null and uses empty string when no user is assigned
        user_id=user_id if user_id is not None else '',
        app_type='Adult update'
    )


def create_arc_user():
    user = User.objects.create_user(
        username='arc_test', email='test@test.com', password='my_secret')
    g = Group.objects.create(name=settings.ARC_GROUP)
    g.user_set.add(user)
    return user


def create_contact_centre_user():
    user = User.objects.create_user(
        username='cc_test', email='testing@test.com', password='my_secret')
    g2 = Group.objects.create(name=settings.CONTACT_CENTRE)
    g2.user_set.add(user)
    return user


def assertSummaryField(response, label, value, heading=None):
    """Raises assertion error if given field is not found on the page with the specified value

    :param response: the http response to check
    :param label: the expected text of the field label
    :param value: the expected text of the field value
    :param heading: (optional) the expected text of the heading the field is found under"""

    if heading is not None:
        assertXPath(response, _heading_xpath(heading))

    assertXPath(response, _field_xpath(label, heading))
    assertXPathValue(response, _field_value_xpath(label, heading), value, strip=True)


def assertNotSummaryField(response, label, heading=None):
    """Raises assertion error if given field IS found on the page

    :param response: the http response to check
    :param label: the (un)expected text of the field label
    :param heading: (optional) the (un)expected text of the heading the field is (not) found under"""

    if heading is not None:
        assertXPath(response, _heading_xpath(heading))

    assertNotXPath(response, _field_xpath(label, heading))


def _heading_xpath(heading):
    return ("(//h1|//h2|//h3|//h4|//h5|//h6|//thead)"
            "/descendant-or-self::*[normalize-space(text())=\"{}\"]").format(heading)


def _field_xpath(label, heading=None):
    xpath = ""
    if heading is not None:
        xpath += _heading_xpath(heading)
        xpath += "/following::tbody[1]"
    xpath += "//td[normalize-space(text())=\"{}\"]".format(label)
    return xpath


def _field_value_xpath(label, heading=None):
    xpath = _field_xpath(label, heading)
    xpath += "/following-sibling::td[1]/text()"
    return xpath


def patch_for_setUp(test_case, *args, **kwargs):
    """
    Performs a unittest.mock.patch such that it will remain in place for the duration of a single test in the given
    TestCase before being undone. Suitable for invoking in a TestCase.setUp method.
    :param test_case: The TestCase instance
    :param args: positional arguments to pass to patch
    :param kwargs: keyword arguments to pass to patch
    :return: The result of the patch call, i.e. either a MagicMock or None
    """
    patcher = unittest.mock.patch(*args, **kwargs)
    test_case.addCleanup(patcher.stop)
    return patcher.start()


def patch_object_for_setUp(test_case, *args, **kwargs):
    """
    Performs a unittest.mock.patch.object such that it will remain in place for the duration of a single test in the
    given TestCase before being undone. Suitable for invoking in a TestCase.setUp method.
    :param test_case: The TestCase instance
    :param args: positional arguments to pass to patch.object
    :param kwargs: keyword arguments to pass to patch.object
    :return: The result of the patch.object call, i.e. either a MagicMock or None
    """
    patcher = unittest.mock.patch.object(*args, **kwargs)
    test_case.addCleanup(patcher.stop)
    return patcher.start()

