import datetime

from lxml import etree
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.models import User, Group

from arc_application import models


mock_nanny_application = {
    'application_status': 'DRAFTING',
    'application_id': '998fd8ec-b96b-4a71-a1a1-a7a3ae186729',
    'date_submitted': '2018-07-31 17:20:46.011717+00',
    'date_updated': '2018-07-31 17:20:46.011717+00',
    'childcare_training_status': 'NOT_STARTED',
    'login_details_status': 'COMPLETED',
    'personal_details_status': 'NOT_STARTED',
    'criminal_record_check_status': 'NOT_STARTED',
    'address_to_be_provided': True,
    'login_details_arc_flagged': False,
    'personal_details_arc_flagged': False,
    'childcare_address_status': 'COMPLETED',
    'childcare_address_arc_flagged': False,
    'first_aid_training_status': 'COMPLETED',
    'first_aid_training_arc_flagged': False,
    'childcare_training_arc_flagged': False,
    'criminal_record_check_arc_flagged': False,
    'insurance_cover_status': 'COMPLETED',
    'insurance_cover_arc_flagged': False,
    'application_reference': 'NA',
    'share_info_declare': True
}

mock_personal_details_record = {
    'application_id': '998fd8ec-b96b-4a71-a1a1-a7a3ae186729',
    'personal_detail_id': '9835bf4b-9ba9-4162-a25b-4c56e7d33d67',
    'first_name': 'The Dark Lord',
    'middle_names': '',
    'last_name': 'Selenium',
    'date_of_birth': '2000-01-01',
    'lived_abroad': True,
    'known_to_social_services': True,
    'reasons_known_to_social_services': 'An IMPORTANT reason'
}

mock_childcare_training_record = {
    'application_id': '998fd8ec-b96b-4a71-a1a1-a7a3ae186729',
    'childcare_training_id': '9835bf3b-8ba9-4162-a25b-4c55e7d33d69',
    'level_2_training': False,
    'common_core_training': False,
    'no_training': False
}

mock_dbs_record = {
    'application_id': '998fd8ec-b96b-4a71-a1a1-a7a3ae186729',
    'dbs_id': '9835bf3b-8ba9-4162-a25b-4c55e7d33d77',
    'lived_abroad': True,
    'is_ofsted_dbs': True,
    'on_dbs_update_service': True,
    'dbs_number': '000000000012',
    'within_three_months':False,
    'enhanced_check':None,
    'convictions': None,
}

mock_home_address = {
    'application_id': '998fd8ec-b96b-4a71-a1a1-a7a3ae186729',
    'home_address_id': '9935bf3b-8ba9-4162-a25b-4c55e7d33d67',
    'street_line1': 'Test',
    'street_line2': None,
    'town': 'Middle Earth',
    'county': None,
    'postcode': 'WA14 4PA',
    'childcare_address': False,
}

mock_childcare_address_record = [
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

mock_first_aid_record = {
    'application_id': '998fd8ec-b96b-4a71-a1a1-a7a3ae186729',
    'first_aid_id': '9835bf3b-8ba9-4162-a25b-4c56e7d33d67',
    'training_organisation': 'St Johns Ambulance',
    'course_title': 'Pediatric First Aid',
    'course_date': '2016-03-31'
}

mock_insurance_cover_record = {
    'application_id': '998fd8ec-b96b-4a71-a1a1-a7a3ae186729',
    'insurance_cover_id': '9835bf3b-9ba9-4162-a25b-4c56e7d33d67',
    'public_liability': True
}

mock_identity_record = {
    'email': 'test@informed.com',
    'application_id': 'a4e6633f-5339-4de5-ae03-69c71fd008b3',
    'magic_link_sms': '12345',
    'sms_resend_attempts': 0,
    'mobile_number': '000000000012',
    'magic_link_email': 'ABCDEFGHIJKL',
    'add_phone_number': '',
}

mock_your_children_record = [
  {
    "child_id": "ea55fae9-5f9f-421b-8adc-19aaad37016d",
    "child": 1,
    "lives_with_applicant": True,
    "first_name": "Mr",
    "middle_names": "",
    "last_name": "Bump",
    "birth_day": 1,
    "birth_month": 1,
    "birth_year": 2008,
    "date_created": "2018-10-31T13:44:58.948231Z",
    "street_line1": "FORTIS DEVELOPMENTS LTD, BANK HOUSE",
    "street_line2": "OLD MARKET PLACE",
    "town": "ALTRINCHAM",
    "county": "",
    "country": None,
    "postcode": "WA14 4PA",
    'application_id': '998fd8ec-b96b-4a71-a1a1-a7a3ae186729',
  },
  {
    "child_id": "d02691ff-4050-4e42-bae8-c17c12ff0f27",
    "child": 2,
    "lives_with_applicant": False,
    "first_name": "Mr",
    "middle_names": "MIDDLE",
    "last_name": "Happy",
    "birth_day": 1,
    "birth_month": 1,
    "birth_year": 2010,
    "date_created": "2018-10-31T13:45:16.802325Z",
    "street_line1": "Palace",
    "street_line2": "",
    "town": "London",
    "county": "",
    "country": None,
    "postcode": "SW1 1AA",
    'application_id': '998fd8ec-b96b-4a71-a1a1-a7a3ae186729',
  }
]

mock_declaration_record = {
    'application_id': '998fd8ec-b96b-4a71-a1a1-a7a3ae186729',
    'follow_rules': True,
    'share_info_declare': True,
    'information_correct_declare': True,
    'change_declare': True,
}

mock_timeline_log_record = {}

nanny_application_response = HttpResponse()
nanny_application_response.status_code = 200
nanny_application_response.record = mock_nanny_application

personal_details_response = HttpResponse()
personal_details_response.status_code = 200
personal_details_response.record = mock_personal_details_record

childcare_training_response = HttpResponse()
childcare_training_response.status_code = 200
childcare_training_response.record = mock_childcare_training_record

home_address_response = HttpResponse()
home_address_response.status_code = 200
home_address_response.record = mock_home_address

dbs_check_response = HttpResponse()
dbs_check_response.status_code = 200
dbs_check_response.record = mock_dbs_record

first_aid_response = HttpResponse()
first_aid_response.status_code = 200
first_aid_response.record = mock_first_aid_record

insurance_cover_response = HttpResponse()
insurance_cover_response.status_code = 200
insurance_cover_response.record = mock_insurance_cover_record

childcare_address_response = HttpResponse()
childcare_address_response.status_code = 200
childcare_address_response.record = mock_childcare_address_record

declaration_response = HttpResponse()
declaration_response.status_code = 200
declaration_response.record = mock_declaration_record

identity_response = HttpResponse()
identity_response.status_code = 200
identity_response.record = mock_identity_record

arc_comments_response = HttpResponse()
arc_comments_response.status_code = 404

timeline_log_response = HttpResponse()
timeline_log_response.status_code = 200
timeline_log_response.record = mock_timeline_log_record


mock_endpoint_return_values = {
    'application': nanny_application_response,
    'applicant-personal-details': personal_details_response,
    'childcare-training': childcare_training_response,
    'childcare-address': childcare_address_response,
    'applicant-home-address': home_address_response,
    'dbs-check': dbs_check_response,
    'first-aid': first_aid_response,
    'insurance-cover': insurance_cover_response,
    'declaration': declaration_response,
    'user': identity_response,
    'arc-comments': arc_comments_response,
    'timeline-log': timeline_log_response,
}


def side_effect(endpoint_name, *args, **kwargs):
    return mock_endpoint_return_values[endpoint_name]


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


def assertXPathValue(response, xpath, expected_value):
    """
    Asserts that the given value can be found at the given xpath in the response's HTML

    :param response: The http response object
    :param xpath: An XPath expression to test for
    :param expected_value: The content expected to be found
    """
    result = _do_xpath(response, xpath)
    if expected_value not in result:
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
        raise AssertionError('Expected {} instances of "{}", found {}', expected_quantity, xpath, len(result))


def _do_xpath(response, xpath):
    tree = etree.fromstring(response.content, parser=etree.HTMLParser()).getroottree()
    return tree.xpath(xpath)


def assertView(response, expected_view_obj):
    expected_name = expected_view_obj if isinstance(expected_view_obj, str) else expected_view_obj.__name__
    actual_name = response.resolver_match.func.__name__
    if actual_name != expected_name:
        raise AssertionError('Expected view "{}", found view "{}"'.format(expected_name, actual_name))


def create_childminder_application(user_id=None):

    application = models.Application.objects.create(
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

    details = models.ApplicantPersonalDetails.objects.create(
        personal_detail_id='da2265c2-2d65-4214-bfef-abcfe59b75aa',
        application_id=application,
        birth_day='01',
        birth_month='01',
        birth_year='2001'
    )

    models.ChildcareType.objects.create(
        application_id=application,
        zero_to_five=True,
        five_to_eight=True,
        eight_plus=True,
        overnight_care=True
    )

    models.ApplicantHomeAddress.objects.create(
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
        move_in_month=0,
        move_in_year=0
    )

    models.ApplicantName.objects.create(
        name_id='da2265c2-2d65-4214-bfef-abcfe59b75aa',
        personal_detail_id=details,
        application_id=application,
        current_name='True',
        first_name='Erik',
        middle_names='Tolstrup',
        last_name='Odense'
    )

    models.UserDetails.objects.create(
        login_id='8362d470-ecc9-4069-876b-9b3ddc2cae07',
        application_id=application,
        email='test@test.com',
    )

    models.FirstAidTraining.objects.create(
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

    models.ChildcareTraining.objects.create(
        eyfs_id='da2265c2-2d65-4214-bfef-abcfe59b75aa',
        application_id=application,
        eyfs_course_name='Test Childcare Training',
        eyfs_course_date_day=1,
        eyfs_course_date_month=2,
        eyfs_course_date_year=2018,
    )

    models.HealthDeclarationBooklet.objects.create(
        hdb_id='da2265c2-2d65-4214-bfef-abcfe59b75aa',
        application_id=application,
        send_hdb_declare=True,
    )

    models.CriminalRecordCheck.objects.create(
        criminal_record_id='da2265c2-2d65-4214-bfef-abcfe59b75aa',
        application_id=application,
        dbs_certificate_number='123456654321',
        cautions_convictions=True
    )

    models.AdultInHome.objects.create(
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

    models.ChildInHome.objects.create(
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

    models.Reference.objects.create(
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

    models.Reference.objects.create(
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

    # assign to a user
    if user_id is not None:
        models.Arc.objects.create(
            application_id=application.application_id,
            user_id=user_id,
        )

    return application


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
    assertXPathValue(response, _field_value_xpath(label, heading), value)


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
    return 'normalize-space({})'.format(xpath)