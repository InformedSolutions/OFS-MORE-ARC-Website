import logging
from datetime import datetime
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from timeline_logger.models import TimelineLog

from ...decorators import group_required, user_assigned_application
from ...models import *
from ...services.db_gateways import HMGatewayActions
from .confirmation import review
from django.utils.safestring import mark_safe

# Initiate logging
log = logging.getLogger('')

@login_required
@group_required(settings.ARC_GROUP)
@user_assigned_application
def arc_summary(request):
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        variables = get_application_summary_variables(application_id_local)
        log.debug("Rendering arc summary page")
        return render(request, 'adult_update_templates/arc_summary.html', variables)

    elif request.method == 'POST':
        application_id_local = request.POST["id"]
        status = Arc.objects.get(pk=application_id_local)
        status.adult_update_review = 'COMPLETED'
        status.save()
        log.debug("Handling submissions for arc summary page")
        return review(request, application_id_local)


def get_application_summary_variables(application_id):
    """
    A function for generating the summary page contents in the ARC view. Note that this is re-used by the
    document generation function so changes will be applied in both the UI and PDF exports.
    :param application_id: the unique identifier of the application
    :param apply_filtering_for_eyc: a filter flag to exclude fields that should not appear in an EYC form
    :return: a variables object for use in Django templates including all application information
    (and similarly EYC form contents).
    """

    adult = HMGatewayActions().read('adult', params={'adult_id': application_id})
    token_id = adult.record['token_id']
    dpa_auth = HMGatewayActions().read('dpa-auth', params={'token_id': token_id})

    json = load_json(application_id)

    ey_number = dpa_auth.record['URN']

    variables = {
        'json': json,
        'application_id': application_id,
        'ey_number': ey_number
    }

    return variables

def load_json(adult_id):
    table_list = []
    record = HMGatewayActions().list('adult', params={'adult_id': adult_id}).record[0]
    # main adult details table
    if record['middle_names'] is not None or record['middle_names'] != '':
        full_name = record['first_name'] + " " +record['middle_names'] + " " + record['last_name']
    else:
        full_name = record['first_name'] + " " + record['last_name']
    link = reverse("new_adults_summary") + '?id=' + adult_id
    summary_table = [
            {"title": full_name,
             "id": record['adult_id']},
        {"name": "Health questions status",
         "value": record['health_check_status'],
         "field": 'health_check_status'},
    ]

    if record['title'] != '':
        summary_table.extend([{"name": "Title",
                              "value": record['title'],
                              "field": "title"}])

    summary_table.extend([
            {"name": "Name",
             "value": full_name,
             'field': "full_name"},
            {"name": "Date of birth",
             "value": datetime.datetime(record['birth_year'], record['birth_month'], record['birth_day']).strftime('%d/%m/%Y'),
             "field": "date_of_birth"},
            {"name": "Relationship",
             "value": record['relationship'],
             "field": "relationship"},
            {"name": "Email",
             "value": record['email'],
             'field': "email"},
            {"name": "Phone Number",
             "value": record['PITH_mobile_number'],
             'field': "PITH_mobile_number"},
            {"name": "Lived abroad in the last 5 years?",
             "value": 'Yes' if record['lived_abroad'] else 'No',
             'field': "lived_abroad"},
            {"name": "Lived or worked on British military base in the last 5 years?",
            "value": 'Yes' if record['military_base'] else 'No',
             'field': 'military_base'}
            ])

    if record['enhanced_check']:

        summary_table += [
                {"name": "Did they get their DBS check from the Ofsted DBS application website?",
                 "value": 'Yes' if record['capita'] else 'No',
                'field':'capita'},
            ]

        if record['capita']:
            summary_table += [
                    {"name": "Is it dated within the last 3 months?",
                     "value": 'Yes' if record['within_three_months'] else 'No',
                     'field': "capita"}
                ]

        summary_table += [
                {"name": "DBS certificate number",
                "value": record['dbs_certificate_number'],
                 "field": 'dbs_certificate_number'},
            ]


    summary_table += [
            {"name": "Enhanced DBS check for home-based childcare?",
             "value": 'Yes' if record['enhanced_check'] else 'No',
             "field": 'enhanced_check'}
        ]

    if record['enhanced_check'] and not (record['capita'] or record['within_three_months']):
        summary_table += [
                {"name": "DBS Update Service?",
                 "value": 'Yes' if record['on_update'] else 'No',
                 'field': "on_update"}
            ]

    summary_table += [
            {"name": "Known to council social Services in regards to their own children?",
             "value": "Yes" if record['known_to_council'] else "No",
             'field': "known_to_council"}
        ]

    if record['known_to_council']:
        summary_table += [
                {"name": "Tell us why",
                 "value": record['reasons_known_to_council_health_check'],
                 'field': "reasons_known_to_council_health_check"}
            ]


    for row in summary_table:
        field = row["field"] if row.get("field") else ''
        add_comment(adult_id, field, row)
        row["link"] = link
    table_list.append(summary_table)

    current_treatment_table = [
        {"title": "Current treatment",
         "id": record['adult_id']},
           {"name": "Are you currently being treated by your GP, another doctor or a hospital?",
         "value": 'Yes' if record["currently_being_treated"] else 'No'}
    ]

    if record["currently_being_treated"]:
        current_treatment_table.append(
            {"name": "Details of illness or condition",
             "value": record["illness_details"]}
        )

    serious_illness_table = [
        {"title": "Serious illnesses",
         "id": record['adult_id']},
       {"name": "Have you had any serious illnesses within the last five years?",
         "value": 'Yes' if record["has_serious_illness"] else 'No'}
    ]

    if record["has_serious_illness"]:
        response = HMGatewayActions().list("serious-illness", params={'adult_id': adult_id})
        if response.status_code == 200:
            for serious_illness in response.record:
                serious_illness["start_date"] = datetime.datetime.strptime(serious_illness['start_date'], '%Y-%m-%d').strftime(
            '%d/%m/%Y')
                serious_illness["end_date"] = datetime.datetime.strptime(serious_illness['end_date'], '%Y-%m-%d').strftime(
            '%d/%m/%Y')
                serious_illness_table.append(
                    {"name": serious_illness["description"],
                    "value": serious_illness["start_date"] + " to " + serious_illness["end_date"]}
        )

    hospital_admission_table = [
        {"title": "Hospital admissions",
         "id": record['adult_id']},
           {"name": "Have you been admitted to hospital in the last 2 years?",
         "value": 'Yes' if record["has_hospital_admissions"] else 'No'}
    ]

    if record["has_hospital_admissions"]:
        response = HMGatewayActions().list("hospital-admissions", params={'adult_id': adult_id})
        if response.status_code == 200:
            for admission in response.record:
                admission["start_date"] = datetime.datetime.strptime(admission['start_date'], '%Y-%m-%d').strftime(
                    '%d/%m/%Y')
                admission["end_date"] = datetime.datetime.strptime(admission['end_date'], '%Y-%m-%d').strftime(
                    '%d/%m/%Y')

                hospital_admission_table.append(
                    {"name": admission["description"],
                     "value": admission["start_date"] + " to " + admission["end_date"]}
                )

    table_list.append(current_treatment_table)
    table_list.append(serious_illness_table)
    table_list.append(hospital_admission_table)

    previous_names_response = HMGatewayActions().list("previous-name", params={'adult_id': adult_id})
    previous_address_response = HMGatewayActions().list("previous-address", params={'adult_id': adult_id})
    name_record = None
    address_record = None
    if previous_names_response.status_code == 200:
        name_record = previous_names_response.record
    if previous_address_response.status_code == 200:
        address_record = previous_address_response.record

    if previous_names_response.status_code == 200 or previous_address_response.status_code == 200:
        previous_names_address_table = [{"title": full_name + "'s previous names and addresses", "id": record['adult_id']}
                                       ]
        if name_record is not None:
            link = reverse("adult-update-previous-names") + '?id=' + adult_id
            for i in range(0, len(name_record)):
                name = name_record[i]
                if name['middle_names'] != '' or name['middle_names'] is not None:
                    adult_name = name['first_name'] + " " + name['middle_names'] + " " + name['last_name']
                else:
                    name['name'] = name['first_name'] + " " + name['last_name']
                previous_names_address_table.append({"name":"Previous name " + str(i+1),
                                                     "value": adult_name,
                                                     'link': link})
                previous_names_address_table.append({"name": 'Start date',
                                                     "value": datetime.datetime(name['start_year'], name['start_month'],
                                                                                             name['start_day']).strftime('%d %m %Y'),
                                                     'link': link})
                previous_names_address_table.append({"name": 'End date',
                                                     "value": datetime.datetime(name['end_year'], name['end_month'],
                                                             name['end_day']).strftime('%d %m %Y'),
                                                     'link': link})

        if address_record is not None:
            for i in range(0, len(address_record)):
                address = address_record[i]
                full_address = address['street_line1'] + ", " + address['street_line2'] + ", " + address['town']
                link = reverse("adult_add_previous_address_change") + '?id=' + adult_id + '&address_id=' + address['previous_address_id']
                if address['county'] != '':
                    full_address = full_address + ", " + address['county']
                full_address = full_address + ", " +address['country'] + ', ' + address['postcode']

                previous_names_address_table.append({"name": "Previous address " + str(i+1),
                                                     "value": full_address,
                                                     'link': link})
                previous_names_address_table.append({"name": 'Moved in',
                                                     "value": datetime.datetime.strptime(address['moved_in_date'], '%Y-%m-%d').strftime('%d %m %Y'),
                                                     'link': link})
                previous_names_address_table.append({"name": 'Moved out',
                                                     "value": datetime.datetime.strptime(address['moved_out_date'], '%Y-%m-%d').strftime('%d %m %Y'),
                                                     "link": link })

        table_list.append(previous_names_address_table)


    previous_registration_response = HMGatewayActions().read("previous-registration", params={'adult_id': adult_id})
    if previous_registration_response.status_code == 200:
        record = previous_registration_response.record

        if record["previous_registration"]:
            previous_registration_table = [{"title": "Previous Registration", "id": record['adult_id']},
                                        {"name": "Has the applicant previously registered with Ofsted?",
                                         "value": 'Yes' if record["previous_registration"] else 'No',
                                         "index": 0,
                                         "link": reverse("adults-previous-registration") + '?id=' + adult_id},
                                        {"name": "Individual ID",
                                         "value": record["individual_id"],
                                         "index": 1,
                                         "link": reverse("adults-previous-registration") + '?id=' + adult_id},
                                        {"name": "Has the applicant lived in England for more than 5 years?",
                                         "value": 'Yes' if record['five_years_in_UK'] else 'No',
                                         "index": 2,
                                         "link": reverse("adults-previous-registration") + '?id=' + adult_id}
                                        ]
        else:
            previous_registration_table = [{"title": "Previous Registration", "id": record['adult_id']},
                                           {"name": "Has the applicant previously registered with Ofsted?",
                                            "value": 'Yes' if record["previous_registration"] else 'No',
                                            "index": 0,
                                            "link": reverse("adults-previous-registration") + '?id=' + adult_id},
                                           {"name": "Has the applicant lived in England for more than 5 years?",
                                            "value": 'Yes' if record["five_years_in_UK"] else 'No',
                                            "index": 1,
                                            "link": reverse("adults-previous-registration") + '?id=' + adult_id}
                                           ]

        table_list.append(previous_registration_table)


    return table_list

def add_comment(id, field, row):
    comment_response = HMGatewayActions().list('arc-comments', params={'table_pk':id, 'field_name':field})
    if comment_response.status_code == 200:
        row['comment'] = comment_response.record[0]['comment']

