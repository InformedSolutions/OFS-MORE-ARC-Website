from django.http import HttpResponse


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
    'application_reference': 'NA'
}

mock_personal_details_record = {
    'application_id': '998fd8ec-b96b-4a71-a1a1-a7a3ae186729',
    'personal_detail_id': '9835bf4b-9ba9-4162-a25b-4c56e7d33d67',
    'first_name': 'The Dark Lord',
    'middle_names': '',
    'last_name': 'Selenium',
    'date_of_birth': '2000-01-01',
    'lived_abroad': True,
    'your_children': True
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
    'dbs_number': '000000000012',
    'convictions': False,
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
    'timeline-log': timeline_log_response
}


def side_effect(endpoint_name, *args, **kwargs):
    return mock_endpoint_return_values[endpoint_name]
