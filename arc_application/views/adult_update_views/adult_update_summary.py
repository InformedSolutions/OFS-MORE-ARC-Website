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
from ...forms.adult_update_forms.adult_update_form import NewAdultForm

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

    summary_data = get_summary_data(application_id)

    ey_number = dpa_auth.record['URN']

    variables = {
        'summary_data': summary_data,
        'application_id': application_id,
        'ey_number': ey_number
    }

    return variables

def get_summary_data(adult_id):
    address_history = get_address_history(adult_id)
    current_address = get_current_address(adult_id)
    current_address_values = get_current_address_values(adult_id)
    previous_names = get_previous_names(adult_id)
    health_questions = get_health_questions(adult_id)
    context = {
        'address_history': address_history['history'],
        'prev_addresses_exist': address_history['prev_addresses_exist'],
        'prev_address_gap_exist': address_history['prev_address_gap_exist'],
        'current_address': current_address,
        'current_address_values': current_address_values,
        'name_history': previous_names,
        'health_questions': health_questions,
        'individual_lookup': get_individual_lookup(adult_id),
        'field_comments': get_all_comments(adult_id)
        #'adult_id': adult_id
    }
    return context


def get_all_comments(adult_id):
    all_fields = NewAdultForm.declared_fields.keys()
    field_name_dict = dict()
    for field_name in all_fields:
        if field_name[-8:] == '_declare':
            comment_response = get_comment(adult_id, field_name[:-8])
            if comment_response is not None:
                #field_name_list.append([field_name[:-8], comment_response])
                field_name_dict[field_name[:-8]] = comment_response

    return field_name_dict


def get_comment(id, field):
    comment_response = HMGatewayActions().list('arc-comments', params={'table_pk': id, 'field_name': field})
    if comment_response.status_code == 200:
        return comment_response.record[0]['comment']


def get_individual_lookup(adult_id):
    previous_registration_response = HMGatewayActions().read("previous-registration", params={'adult_id': adult_id})
    if previous_registration_response.status_code == 200:
        prev_reg_record = previous_registration_response.record
        return prev_reg_record["individual_id"] if prev_reg_record[
            "previous_registration"] else False


def get_current_address(adult_id):
    address_response = HMGatewayActions().read('adult-in-home-address', params={'adult_id': adult_id})
    if address_response.status_code == 200:
        address_record = address_response.record
        return address_record


def get_current_address_values(adult_id):
    adult_response = HMGatewayActions().read('adult', params={'adult_id': adult_id})
    if adult_response.status_code == 200:
        address_record = adult_response.record
        return {'moved_in_date': datetime.datetime.strptime(address_record['moved_in_date'], "%Y-%m-%d").date(),
                'lived_abroad': address_record['lived_abroad'],
                'military': address_record['military_base'],
                'previous_address_id': 'current',
                'title': 'Current address'
                }


def get_address_history(adult_id):
    prev_addresses = get_previous_addresses(adult_id)
    prev_address_gaps = get_previous_address_gaps(adult_id)
    history = sorted((prev_addresses + prev_address_gaps),
                     key=lambda address: address['moved_in_date'] if address['moved_in_date'] else 0)
    prev_addresses_exist = True if len(prev_addresses) > 0 else False
    prev_address_gap_exist = True if len(prev_address_gaps) > 0 else False
    gapCounter = 1
    addressCounter = 1
    for address in history:
        order = history.index(address)
        history[order].update({'moved_in_date': datetime.datetime.strptime(address['moved_in_date'], "%Y-%m-%d").date()})
        history[order].update({'moved_out_date': datetime.datetime.strptime(address['moved_out_date'], "%Y-%m-%d").date()})
        if 'previous_address_id' in history[order].keys():
            history[order]['title'] = f"Previous address {addressCounter}"
            addressCounter += 1
        else:
            history[order]['previous_address_id'] = history[order]['missing_address_gap_id']
            history[order]['title'] = f"Previous address gap {gapCounter}"
            gapCounter += 1
    return {'history': history,
            'prev_addresses_exist': prev_addresses_exist,
            'prev_address_gap_exist': prev_address_gap_exist
            }


def get_previous_addresses(adult_id):
    response = HMGatewayActions().list('previous-address', params={'adult_id': adult_id})
    if response.status_code == 200:
        addresses = response.record
        return addresses
    else:
        return []


def get_previous_address_gaps(adult_id):
    response = HMGatewayActions().list('previous-address-gap', params={'adult_id': adult_id})
    if response.status_code == 200:
        addresses = response.record
        return addresses
    else:
        return []


def get_previous_names(adult_id):
    context = dict()
    previous_names_list = []
    previous_names_response = HMGatewayActions().list('previous-name', params={'adult_id': adult_id})

    if previous_names_response.status_code == 200:
        previous_names = previous_names_response.record
        for previous_name in previous_names:
            previous_name['start_date'] = date(previous_name['start_year'], previous_name['start_month'], previous_name['start_day'])
            previous_name['end_date'] = date(previous_name['end_year'], previous_name['end_month'], previous_name['end_day'])
            previous_name['full_name'] = previous_name['first_name'] + ' ' + previous_name['last_name']
            previous_names_list.append(previous_name)
        previous_names_list = sorted(previous_names_list,
                                     key=lambda name: name['start_date'] if name['start_date'] else 0)
        for name in previous_names_list: previous_names_list[previous_names_list.index(name)][
            'title'] = f"Previous Name {previous_names_list.index(name)}"
        context['current_name_start_date'] = previous_names_list[-1]['end_date']
        #context['birth_name'] = previous_names_list[0]
    #context['previous_names'] = previous_names_list[1:]
    context['previous_names'] = previous_names_list
    context['previous_name_valid'] = False if not previous_names_list[1:] else True
    return context


def get_health_questions(adult_id):
    context = dict()
    adult_response = HMGatewayActions().list('adult', params={'adult_id': adult_id})
    serious_illnesses = []
    hospital_admissions = []

    if adult_response.status_code == 200:
        adult_records = adult_response.record[0]
        context['current_name_start_date'] = datetime.datetime.strptime(adult_records['date_of_birth'], '%Y-%m-%d').date()
        serious_illness_response = HMGatewayActions().list('serious-illness', params={'adult_id': adult_id})
        hospital_admissions_response = HMGatewayActions().list('hospital-admissions', params={'adult_id': adult_id})

        context[
            'serious_illness_set'] = serious_illness_response.record if serious_illness_response.status_code == 200 else []
        context[
            'hospital_admission_set'] = hospital_admissions_response.record if hospital_admissions_response.status_code == 200 else []
        context['current_treatment_bool'] = adult_records['currently_being_treated']
        context['current_treatment_details'] = adult_records['illness_details']
        context['your_children_bool'] = adult_records['known_to_council']
        context['your_children_reasons'] = adult_records['reasons_known_to_council_health_check']
        context['serious_illness_bool'] = adult_records['has_serious_illness']
        context['hospital_admission_bool'] = adult_records['has_hospital_admissions']
        context['current_name'] = adult_records['get_full_name']
        context['title'] = adult_records['title']
        context['DoB'] = datetime.datetime(adult_records['birth_year'], adult_records['birth_month'], adult_records['birth_day']).date()
        context['relationship'] = adult_records['relationship']
        context['email'] = adult_records['email']
        context['PITH_mobile_number'] = adult_records['PITH_mobile_number']
        context['capita'] = adult_records['capita']
        context['within_three_months'] = adult_records['within_three_months']
        context['dbs_certificate_number'] = adult_records['dbs_certificate_number']
        context['enhanced_check'] = adult_records['enhanced_check']
        context['on_update'] = adult_records['on_update']
        context['known_to_council'] = adult_records['known_to_council']
        context['reasons_known_to_council_health_check'] = adult_records['reasons_known_to_council_health_check']


        serious_illness_list = HMGatewayActions().list('serious-illness', params={'adult_id': adult_id})
        hospital_admissions_list = HMGatewayActions().list('hospital-admissions', params={'adult_id': adult_id})

        if serious_illness_list.status_code == 200:
            for illness in serious_illness_list.record:

                start_date = datetime.datetime.strptime(illness['start_date'], "%Y-%m-%d").date()
                end_date = datetime.datetime.strptime(illness['end_date'], "%Y-%m-%d").date()
                description = illness['description']
                illness_id = illness['illness_id']

                illness_record = {
                    'start_date': start_date,
                    'end_date': end_date,
                    'description': description,
                    'illness_id': illness_id

                }

                serious_illnesses.append(illness_record)

        context['serious_illnesses'] = serious_illnesses

        if hospital_admissions_list.status_code == 200:
            for admission in hospital_admissions_list.record:
                start_date = datetime.datetime.strptime(admission['start_date'], "%Y-%m-%d").date()
                end_date = datetime.datetime.strptime(admission['end_date'], "%Y-%m-%d").date()
                description = admission['description']
                admission_id = admission['admission_id']

                admission_record = {
                    'start_date': start_date,
                    'end_date': end_date,
                    'description': description,
                    'admission_id': admission_id
                }

                hospital_admissions.append(admission_record)

        context['hospital_admissions'] = hospital_admissions

        return context


def load_json(adult_id):
    table_list = []
    record = HMGatewayActions().list('adult', params={'adult_id': adult_id}).record[0]
    # main adult details table
    if record['middle_names'] is not None or record['middle_names'] != '':
        full_name = record['first_name'] + " " + record['middle_names'] + " " + record['last_name']
    else:
        full_name = record['first_name'] + " " + record['last_name']

    # get adults address
    adult_address_response = HMGatewayActions().read('adult-in-home-address',
                                                     params={'adult_id': record['adult_id']})
    if adult_address_response.status_code == 200:
        adult_address_record = adult_address_response.record
        address_string = ' '.join([adult_address_record['street_line1'], adult_address_record['street_line2'],
                                   adult_address_record['town'],
                                   adult_address_record['county'], adult_address_record['country'] if not None else '',
                                   adult_address_record['postcode']])
    else:
        address_string = ''

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
         "value": datetime.datetime(record['birth_year'], record['birth_month'], record['birth_day']).strftime(
             '%d/%m/%Y'),
         "field": "date_of_birth"},
        {"name": "Relationship",
         "value": record['relationship'],
         "field": "relationship"},
        {"name": "Email",
         "value": record['email'],
         'field': "email"},
        {"name": "Phone number",
         "value": record['PITH_mobile_number'],
         'field': "PITH_mobile_number"},
        {"name": "Address",
         "value": address_string,
         'field': "PITH_same_address"},
    ])
    if record['moved_in_date']:
        summary_table.extend([{"name": "Moved in",
                               "value": datetime.datetime.strptime(record['moved_in_date'],'%Y-%m-%d').strftime(
                                                         '%d %m %Y'),
                               "field": "moved_in_date"}])
    summary_table.extend([
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
             'field': 'capita'},
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

    previous_registration_response = HMGatewayActions().read("previous-registration", params={'adult_id': adult_id})
    if previous_registration_response.status_code == 200:
        prev_reg_record = previous_registration_response.record
        previous_registration_table = [{"title": "Individual lookup", "id": prev_reg_record['adult_id']},
                                       {"name": "Individual ID",
                                        "value": prev_reg_record["individual_id"] if prev_reg_record[
                                            "previous_registration"] else 'Not known to Ofsted',
                                        "index": 1,
                                        "link": reverse("personal_details_individual_lookup") + '?id=' +
                                                prev_reg_record['adult_id'] + '&referrer=household_member&adult_id=' +
                                                prev_reg_record['adult_id']},
                                       ]

        table_list.append(previous_registration_table)

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
                serious_illness["start_date"] = datetime.datetime.strptime(serious_illness['start_date'],
                                                                           '%Y-%m-%d').strftime(
                    '%d/%m/%Y')
                serious_illness["end_date"] = datetime.datetime.strptime(serious_illness['end_date'],
                                                                         '%Y-%m-%d').strftime(
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
        previous_names_address_table = [
            {"title": full_name + "'s previous names and addresses", "id": record['adult_id']}
            ]
        if name_record is not None:
            link = reverse("new_adults_summary") + '?id=' + adult_id
            for i in range(0, len(name_record)):
                name = name_record[i]
                if name['middle_names'] != '' or name['middle_names'] is not None:
                    adult_name = name['first_name'] + " " + name['middle_names'] + " " + name['last_name']
                else:
                    name['name'] = name['first_name'] + " " + name['last_name']
                previous_names_address_table.append({"name": "Previous name " + str(i + 1),
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
                link = reverse("new_adults_summary") + '?id=' + adult_id + '&address_id=' + address[
                    'previous_address_id']
                if address['county'] != '':
                    full_address = full_address + ", " + address['county']
                full_address = full_address + ", " + address['country'] + ', ' + address['postcode']

                previous_names_address_table.append({"name": "Previous address " + str(i + 1),
                                                     "value": full_address,
                                                     'link': link})
                previous_names_address_table.append({"name": 'Moved in',
                                                     "value": datetime.datetime.strptime(address['moved_in_date'],
                                                                                         '%Y-%m-%d').strftime(
                                                         '%d %m %Y'),
                                                     'link': link})
                previous_names_address_table.append({"name": 'Moved out',
                                                     "value": datetime.datetime.strptime(address['moved_out_date'],
                                                                                         '%Y-%m-%d').strftime(
                                                         '%d %m %Y'),
                                                     "link": link})

        table_list.append(previous_names_address_table)

    return table_list


def add_comment(id, field, row):
    comment_response = HMGatewayActions().list('arc-comments', params={'table_pk': id, 'field_name': field})
    if comment_response.status_code == 200:
        row['comment'] = comment_response.record[0]['comment']

