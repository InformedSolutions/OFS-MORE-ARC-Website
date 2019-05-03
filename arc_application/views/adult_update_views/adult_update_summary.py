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
        return HttpResponseRedirect(
            reverse('adults-confirmation') + '?id=' + application_id_local
        )

def get_application_summary_variables(application_id):
    """
    A function for generating the summary page contents in the ARC view. Note that this is re-used by the
    document generation function so changes will be applied in both the UI and PDF exports.
    :param application_id: the unique identifier of the application
    :param apply_filtering_for_eyc: a filter flag to exclude fields that should not appear in an EYC form
    :return: a variables object for use in Django templates including all application information
    (and similarly EYC form contents).
    """

    dpa_auth = HMGatewayActions().read('dpa-auth', params={'token_id': application_id})

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
            {"name": "Lived abroad in the last 5 years?",
             "value": 'Yes' if record['lived_abroad'] else 'No',
             'field': "lived_abroad"},
            {"name": "Lived or worked on British military base in the last 5 years?",
            "value": 'Yes' if record['military_base'] else 'No',
             'field': 'military_base'}
            ]

    if record['enhanced_check']:

        summary_table += [
                {"name": "Did they get their DBS check from the Ofsted DBS application website?",
                 "value": record['capita'],
                'field':'capita'},
            ]

        if record['capita']:
            summary_table += [
                    {"name": "Is it dated within the last 3 months?",
                     "value": record['within_three_months'],
                     'field': "capita"}
                ]

        summary_table += [
                {"name": "DBS certificate number",
                "value": record['dbs_certificate_number'],
                 "field": 'dbs_certificate_number'},
            ]


    summary_table += [
            {"name": "Enhanced DBS check for home-based childcare?",
             "value": record['enhanced_check'],
             "field": 'enhanced_check'}
        ]

    if record['enhanced_check'] and not (record['capita'] or record['within_three_months']):
        summary_table += [
                {"name": "On the update service?",
                 "value": record['on_update'],
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
                serious_illness["start_date"] = datetime.datetime.strptime(record['start_date'], '%Y-%m-%d').strftime(
            '%d/%m/%Y')
                serious_illness["end_date"] = datetime.datetime.strptime(record['end_date'], '%Y-%m-%d').strftime(
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


    return table_list

def add_comment(id, field, row):
    comment_response = HMGatewayActions().list('arc-comments', params={'table_pk':id, 'field_name':field})
    if comment_response.status_code == 200:
        row['comment'] = comment_response.record[0]['comment']

