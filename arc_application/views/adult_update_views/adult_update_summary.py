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
    context = {
        'address_history': get_address_history(adult_id),
        'current_address': get_current_address(adult_id),
        'current_address_values': get_current_address_values(adult_id),
        'name_history': get_previous_names(adult_id),
        'health_questions': get_health_questions(adult_id),
        'individual_lookup': get_individual_lookup(adult_id),
        'field_comments': get_all_comments(adult_id)
    }
    return context


def get_all_comments(adult_id):
    all_fields = NewAdultForm.declared_fields.keys()
    field_name_dict = dict()
    for field_name in all_fields:
        if field_name[-8:] == '_declare':
            comment_response = get_comment(adult_id, field_name[:-8])
            if comment_response is not None:
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
    return history


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
    context['previous_names'] = previous_names_list
    context['previous_name_valid'] = False if not previous_names_list[1:] else True
    return context


def get_health_questions(adult_id):
    adult_response = HMGatewayActions().list('adult', params={'adult_id': adult_id})
    serious_illnesses = []
    hospital_admissions = []

    if adult_response.status_code == 200:
        adult_records = adult_response.record[0]

        context = {
            'current_name_start_date': datetime.datetime.strptime(adult_records['date_of_birth'], '%Y-%m-%d').date(),
            'current_treatment_bool': adult_records['currently_being_treated'],
            'current_treatment_details': adult_records['illness_details'],
            'your_children_bool': adult_records['known_to_council'],
            'your_children_reasons': adult_records['reasons_known_to_council_health_check'],
            'serious_illness_bool': adult_records['has_serious_illness'],
            'hospital_admission_bool': adult_records['has_hospital_admissions'],
            'current_name': adult_records['get_full_name'],
            'title': adult_records['title'],
            'DoB': datetime.datetime(adult_records['birth_year'], adult_records['birth_month'],
                                               adult_records['birth_day']).date(),
            'relationship': adult_records['relationship'],
            'email': adult_records['email'],
            'PITH_mobile_number': adult_records['PITH_mobile_number'],
            'capita': adult_records['capita'],
            'within_three_months': adult_records['within_three_months'],
            'dbs_certificate_number': adult_records['dbs_certificate_number'],
            'enhanced_check': adult_records['enhanced_check'],
            'on_update': adult_records['on_update'],
            'known_to_council': adult_records['known_to_council'],
            'reasons_known_to_council_health_check': adult_records['reasons_known_to_council_health_check'],
            'health_check_status': adult_records['health_check_status']
        }

        serious_illness_response = HMGatewayActions().list('serious-illness', params={'adult_id': adult_id})
        hospital_admissions_response = HMGatewayActions().list('hospital-admissions', params={'adult_id': adult_id})
        context[
            'serious_illness_set'] = serious_illness_response.record if serious_illness_response.status_code == 200 else []
        context[
            'hospital_admission_set'] = hospital_admissions_response.record if hospital_admissions_response.status_code == 200 else []

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
