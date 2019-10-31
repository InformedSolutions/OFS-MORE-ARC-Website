from datetime import datetime, date
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.forms import formset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
import logging
from ...decorators import group_required, user_assigned_application
from ...forms.adult_update_forms.adult_update_form import NewAdultForm
from .review import new_adults_initial_population, request_to_comment, save_comments
from ...services.db_gateways import HMGatewayActions
from ...models import Arc
from operator import itemgetter

# Initiate logging
log = logging.getLogger('')

@login_required
@group_required(settings.ARC_GROUP)
@user_assigned_application
def new_adults_summary(request):
    """
    Method returning the template for the People in your home: summary page (for a given application)
    displaying entered data for this task and navigating to the task list when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered People in your home: summary template
    """

    # Defines the formset using formset factory
    AdultFormSet = formset_factory(NewAdultForm, extra=0)

    adult_id_local = request.GET.get('id') or request.POST.get('id')

    # Adult data
    adults = HMGatewayActions().list('adult', params={'adult_id': adult_id_local}).record
    adult_record_list = []
    adult_id_list = []
    adult_health_check_status_list = []
    adult_title_list=[]
    adult_name_list = []
    adult_birth_day_list = []
    adult_birth_month_list = []
    adult_birth_year_list = []
    adult_relationship_list = []
    adult_email_list = []
    adult_mobile_number_list = []
    adult_dbs_cert_numbers = []
    adult_dbs_on_capitas = []
    adult_dbs_is_recents = []
    adult_dbs_is_enhanceds = []
    adult_dbs_on_updates = []
    current_illnesses = []
    serious_illnesses = []
    hospital_admissions = []
    local_authorities = []
    adult_lived_abroad = []
    adult_military_base = []
    adult_name_querysets = []
    adult_address_querysets = []
    previous_registration_querysets = []
    adult_previous_name_lists_list = []
    adult_previous_address_lists_list = []

    # Set up bool to track whether linking has been completed for all adults in this application
    linking_complete = True

    for adult in adults:

        if adult['middle_names'] is not None and adult['middle_names'] != '':
            name = adult['first_name'] + ' ' + adult['middle_names'] + ' ' + adult['last_name']
        else:
            name = adult['first_name'] + ' ' + adult['last_name']

        adult_id = adult['adult_id']

        adult_record_list.append(adult)
        adult_id_list.append(adult['adult_id'])
        adult_health_check_status_list.append(adult['health_check_status'])
        adult_title_list.append(adult['title'])
        adult_name_list.append(name)
        adult_birth_day_list.append(adult['birth_day'])
        adult_birth_month_list.append(adult['birth_month'])
        adult_birth_year_list.append(adult['birth_year'])
        adult_relationship_list.append(adult['relationship'])
        adult_email_list.append(adult['email'])
        adult_mobile_number_list.append(adult['PITH_mobile_number'])
        adult_dbs_is_enhanceds.append(adult['enhanced_check'])
        adult_dbs_cert_numbers.append(adult['dbs_certificate_number'] if adult['enhanced_check'] else None)
        adult_dbs_on_capitas.append(adult['capita'] if adult['enhanced_check'] else None)
        adult_dbs_is_recents.append(adult['within_three_months'] if adult['enhanced_check'] else None)
        adult_dbs_on_updates.append(adult['on_update'] if not adult['within_three_months'] else None)
        adult_lived_abroad.append(adult['lived_abroad'])
        adult_military_base.append(adult['military_base'])
        #health check fields

        serious_illnesses_response = HMGatewayActions().list('serious-illness',{'adult_id':adult_id})
        if serious_illnesses_response.status_code == 200:
            for record in serious_illnesses_response.record:
                record["start_date"] = datetime.strptime(record['start_date'], '%Y-%m-%d').strftime(
            '%d/%m/%Y')
                record["end_date"] = datetime.strptime(record['end_date'], '%Y-%m-%d').strftime(
            '%d/%m/%Y')
            serious_illnesses.append(serious_illnesses_response.record)
        else:
            serious_illnesses.append(None)
        hospital_admissions_response = HMGatewayActions().list('hospital-admissions', {'adult_id': adult_id})
        if hospital_admissions_response.status_code == 200:
            for record in hospital_admissions_response.record:
                record["start_date"] = datetime.strptime(record['start_date'], '%Y-%m-%d').strftime(
            '%d/%m/%Y')
                record["end_date"] = datetime.strptime(record['end_date'], '%Y-%m-%d').strftime(
            '%d/%m/%Y')
            hospital_admissions.append(hospital_admissions_response.record)
        else:
            hospital_admissions.append(None)
        local_authorities.append(adult['reasons_known_to_council_health_check'])

        previous_registration_response = HMGatewayActions().read('previous-registration', params={'adult_id': adult_id})
        if previous_registration_response.status_code == 200:
            previous_registration_record = previous_registration_response.record
            previous_registration_querysets.append(previous_registration_record)
        else:
            # If no previous registration data found then linking hasn't been attempted for this adult
            linking_complete = False

        previous_name_response = HMGatewayActions().list('previous-name', params={'adult_id': adult_id})
        if previous_name_response.status_code == 200:
            for prev_name in previous_name_response.record:
                if prev_name['middle_names'] != '' or prev_name['middle_names'] is not None:
                    prev_name['name'] = prev_name['first_name'] + " " + prev_name['middle_names'] + " " + prev_name['last_name']
                else:
                    prev_name['name'] = prev_name['first_name'] + " "  + prev_name['last_name']

                prev_name['start_date'] = datetime(prev_name['start_year'], prev_name['start_month'], prev_name['start_day']).strftime(
            '%d %m %Y')
                prev_name['end_date'] = datetime(prev_name['end_year'], prev_name['end_month'],
                                                        prev_name['end_day']).strftime(
                    '%d %m %Y')
            adult_previous_name_lists_list.append(previous_name_response.record)
        else:
            adult_previous_name_lists_list.append(None)

        previous_address_response = HMGatewayActions().list('previous-address', params={'adult_id':adult_id})
        if previous_address_response.status_code == 200:
            for prev_address in previous_address_response.record:
                prev_address['moved_in_date'] = datetime.strptime(prev_address['moved_in_date'], '%Y-%m-%d').strftime(
            '%d %m %Y')
                prev_address['moved_out_date'] = datetime.strptime(prev_address['moved_out_date'], '%Y-%m-%d').strftime(
                    '%d %m %Y')
            adult_previous_address_lists_list.append(previous_address_response.record)
        else:
            adult_previous_address_lists_list.append(None)

    previous_registration_lists = list(zip(adult_id_list, adult_name_list, previous_registration_querysets))

    if request.method == 'GET':
        # Defines the static form at the top of the page

        initial_adult_data = new_adults_initial_population(adults)

        # Instantiates the formset with the management data defined above, forcing a set amount of forms
        formset_adult = AdultFormSet(initial=initial_adult_data, prefix='adult')

        # Zips the formset into the list of adults
        # Converts it to a list, there was trouble parsing the form objects when it was in a zip object
        adult_lists = list(zip(adult_record_list, adult_id_list, adult_health_check_status_list, adult_title_list, adult_name_list, adult_birth_day_list,\
                      adult_birth_month_list, adult_birth_year_list, adult_relationship_list, adult_email_list, adult_mobile_number_list,\
                      adult_dbs_cert_numbers, adult_dbs_on_capitas, adult_dbs_is_recents, adult_dbs_is_enhanceds,\
                      adult_dbs_on_updates, adult_lived_abroad, adult_military_base, formset_adult, serious_illnesses, hospital_admissions, local_authorities,
                               adult_previous_name_lists_list, adult_previous_address_lists_list))


        variables = {
            'formset_adult': formset_adult,
            'application_id': adult_id_local,
            'adult_lists': adult_lists,
            'previous_registration_lists': previous_registration_lists,
            'linking_complete': linking_complete
        }
        log.debug("Rendering new adults in the home page")
        return render(request, 'adult_update_templates/new-adults-summary.html', variables)

    elif request.method == 'POST':

        adult_formset = AdultFormSet(request.POST, prefix='adult')
        #
        if adult_formset.is_valid():
            adult_data_list = adult_formset.cleaned_data

            section_status = 'COMPLETED'
        #
        #     # ======================================================================================================== #
        #     # To explain the below:
        #     # - Each section has at least one associated formset.
        #     # - Each formset has a list of data from the POST request.
        #     # - Each element in these lists of data is a dictionary and is associated with a single model.
        #     # - The code saves the comments stored in these dictionaries in an ARC_COMMENT using the pk from the model
        #     #   with which it corresponds.
        #     # - The correspondence is that data for a person stored at adult_data_list[1]
        #     #   maps to the model stored at adults[1]
        #     #  ======================================================================================================= #
        #
            review_sections_to_process = {
                    'adults_in_home': {
                    'POST_data': adult_data_list,
                    'models': adults
                 }
            }

            for section in review_sections_to_process.values():
                for adult_post_data, adult in zip(section['POST_data'], section['models']):
                    adult_comments = request_to_comment(adult_id, '', adult_post_data, adult_id_local)
                    token_id = adult['token_id']
                    save_comments(request, adult_comments, adult_id_local, token_id)
                    HMGatewayActions().put('adult', params={'cygnum_relationship_to_childminder': adult_post_data['cygnum_relationship'], 'adult_id':adult_id_local,'token_id': adult['token_id']})

                    #do we get a field to say if anything flagged?
                    if adult_comments:
                        HMGatewayActions().put('adult', params={'adult_id': adult_id_local, 'arc_flagged': True, 'token_id': token_id})
                    else:
                        HMGatewayActions().put('adult',
                                               params={'adult_id': adult_id_local, 'arc_flagged': False, 'token_id': token_id})


            handle_previous_name_and_address_dates(adult_id_local, adults[0])

            log.debug("Redirect to summary")
            redirect_link = reverse('new_adults')
            log.debug("Handling submissions for new adult review page")
            return HttpResponseRedirect(redirect_link + '?id=' + adult_id_local)

        else:

            # Zips the formset into the list of adults
            # Converts it to a list, there was trouble parsing the form objects when it was in a zip object
            adult_lists = list(zip(adult_record_list, adult_id_list, adult_health_check_status_list, adult_title_list, adult_name_list, adult_birth_day_list,\
                      adult_birth_month_list, adult_birth_year_list, adult_relationship_list, adult_email_list, adult_mobile_number_list,\
                      adult_dbs_cert_numbers, adult_dbs_on_capitas, adult_dbs_is_recents, adult_dbs_is_enhanceds,\
                      adult_dbs_on_updates, adult_lived_abroad, adult_military_base, adult_formset, serious_illnesses, hospital_admissions, local_authorities,
                               adult_previous_name_lists_list, adult_previous_address_lists_list))

            for adult_form, adult_name in zip(adult_formset, adult_name_list):
                adult_form.error_summary_title = 'There was a problem (' + adult_name + ')'

            variables = {
                'formset_adult': adult_formset,
                'application_id': adult_id_local,
                'adult_lists': adult_lists,
                'previous_registration_lists': previous_registration_lists}

            log.debug("Render new adult review page")
            return render(request, 'adult_update_templates/new-adults-summary.html', variables)


def handle_previous_name_and_address_dates(adult_id, adult_record):
    """
    Sets start and end dates for current name and address in db
    """
    actions = HMGatewayActions()
    end_date = date.today()
    new_adult_record = {'adult_id':adult_id,'token_id': adult_record['token_id']}

    previous_names = actions.list('previous-name', params={'adult_id': adult_id})
    if previous_names.status_code == 200:
        for name in previous_names.record:
            name['end_date'] = datetime(name['end_year'], name['end_month'], name['end_day'])
        sorted_previous_names = sorted(previous_names.record, key=itemgetter('end_date'), reverse=True)
        name_start_date = sorted_previous_names[0]['end_date']
    else:
        name_start_date = datetime.strptime(adult_record['date_of_birth'], '%Y-%m-%d')

    new_adult_record['name_start_day'] = name_start_date.day
    new_adult_record['name_start_month'] = name_start_date.month
    new_adult_record['name_start_year'] = name_start_date.year
    new_adult_record['name_end_day'] = end_date.day
    new_adult_record['name_end_month'] = end_date.month
    new_adult_record['name_end_year'] = end_date.year

    previous_addresses_response = actions.list('previous-address', params={'adult_id': adult_id})
    if previous_addresses_response.status_code == 200:
        previous_addresses = previous_addresses_response.record
        # moved_out_date is a string but due to iso format, lexicographical order will be
        # equivalent to chronological
        sorted_previous_addresses = sorted(previous_addresses, key=itemgetter('moved_out_date'), reverse=True)
        address_start_date = sorted_previous_addresses[0]['moved_out_date']
    else:
        address_start_date = adult_record['date_of_birth']

    new_adult_record['moved_in_date'] = address_start_date
    new_adult_record['moved_out_date'] = end_date

    actions.put('adult', params=new_adult_record)