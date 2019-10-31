import logging
import os

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.cache import cache
from django.http import HttpResponseRedirect
from django.urls import reverse
import requests

from ...decorators import group_required, user_assigned_application
from ...models import Application, ApplicantPersonalDetails, ApplicantName, ApplicantHomeAddress, AdultInHome, PreviousRegistrationDetails
from ...forms.individual_lookup_forms import IndividualLookupSearchForm
from ...services.db_gateways import HMGatewayActions, NannyGatewayActions
from ...services.integration_service import get_individual_search_results
from ...review_util import build_url

log = logging.getLogger()


def read_record(actions, endpoint, params):
    response = getattr(actions, 'read')(endpoint, params=params)
    if response.status_code != 200 or not hasattr(response, 'record'):
        return {}
    return response.record


def fetch_childminder_data(app_id):
    try:
        personal_details = ApplicantPersonalDetails.objects.get(application_id=app_id)
        name_record = ApplicantName.objects.get(personal_detail_id=personal_details)
        home_address = ApplicantHomeAddress.objects.get(
            personal_detail_id=personal_details,
            current_address=True
        )
    except ObjectDoesNotExist:
        return {}

    return {
        'first_name': name_record.first_name,
        'middle_names': name_record.middle_names,
        'last_name': name_record.last_name,
        'date_of_birth': personal_details.date_of_birth,
        'street_line1': home_address.street_line1,
        'street_line2': home_address.street_line2,
        'town': home_address.town,
        'postcode': home_address.postcode,
        'application_id': app_id,
    }


def fetch_nanny_data(app_id):
    nanny_actions = NannyGatewayActions()
    personal_details = read_record(
        nanny_actions, 'applicant-personal-details', {'application_id': app_id}
    )
    home_address_record = read_record(
        nanny_actions, 'applicant-home-address', {'application_id': app_id}
    )

    return {
        'first_name': personal_details.get('first_name', ''),
        'middle_names': personal_details.get('middle_names', ''),
        'last_name': personal_details.get('last_name', ''),
        'date_of_birth': personal_details.get('date_of_birth', ''),
        'street_line1': home_address_record.get('street_line1', ''),
        'street_line2': home_address_record.get('street_line2', ''),
        'town': home_address_record.get('town', ''),
        'postcode': home_address_record.get('postcode', ''),
        'application_id': app_id,
    }


def fetch_household_member_data(app_id):
    hm_gateway = HMGatewayActions()
    adult_record = read_record(
        hm_gateway, 'adult', {'adult_id': app_id}
    )
    dpa_record = read_record(
        hm_gateway, 'dpa-auth', {'token_id': adult_record['token_id']}
    )

    return {
        'first_name': adult_record.get('first_name', ''),
        'middle_names': adult_record.get('middle_names', ''),
        'last_name': adult_record.get('last_name', ''),
        'date_of_birth': adult_record.get('date_of_birth', ''),
        'street_line1': '',
        'street_line2': '',
        'town': '',
        'postcode': dpa_record.get('postcode', ''),
        'application_id': app_id,
    }


DATA_FETCHER_MAPPING = {
    'childminder': fetch_childminder_data,
    'nanny': fetch_nanny_data,
    'household_member': fetch_household_member_data,
}


@login_required
@group_required(settings.ARC_GROUP, raise_exception=True)
@user_assigned_application
def personal_details_individual_lookup(request):
    '''
    Search for individual and redirect to view with results
    '''

    application_id = request.GET.get('id')
    referrer_type = request.GET.get('referrer')
    form = None
    if request.method == 'GET':

        # Check if form values are in cache
        if application_id in cache:
            form_data = cache.get(application_id)
            search_cached_data = _rewrite_keys_for_search_fields(form_data.copy())
            form = IndividualLookupSearchForm(search_cached_data)
        else:
            form = IndividualLookupSearchForm()

    # Validate form and redirect to view with results
    elif request.method == 'POST':

        # Check if not known to Ofsted
        if request.POST.get('not-known') is not None:
            # Save not known to Ofsted data and redirect to personal details page for given type
            return mark_not_known_to_ofsted(referrer_type, application_id)

        form = IndividualLookupSearchForm(request.POST)

        if form.is_valid():
            form_data = {
                    'forename': form.cleaned_data['forenames'],
                    'surname': form.cleaned_data['last_name'],
                    'day': form.cleaned_data['day'],
                    'month': form.cleaned_data['month'],
                    'year': form.cleaned_data['year'],
                    'address1': form.cleaned_data['street'],
                    'town': form.cleaned_data['town'],
                    'postcode': form.cleaned_data['postcode']
                }

            # Check if form values are in cache
            if application_id in cache:
                cache.set(application_id, form_data)
            else:
                cache.add(application_id, form_data)


            return redirect('././results/?id='+application_id+'&referrer='+referrer_type)

    # Fetch context from a referrer app for 'Applicant's data' box
    if not application_id or referrer_type not in DATA_FETCHER_MAPPING:
        context = {}
    else:
        context = DATA_FETCHER_MAPPING[referrer_type](application_id)

    context['form'] = form

    return render(request, 'childminder_templates/personal-details-individual-lookup.html', context)


@login_required
@group_required(settings.ARC_GROUP, raise_exception=True)
@user_assigned_application
def personal_details_individual_lookup_search_result(request):
    '''
    Search for individual and show results
    '''

    individuals = None
    individuals_list = None
    page = None
    application_id = request.GET['id']
    referrer_type = request.GET.get('referrer')

    if request.method == 'GET':
        # Check if form values are in cache
        if application_id in cache:
            form_data = cache.get(application_id)
            search_cached_data = _rewrite_keys_for_search_fields(form_data.copy())

            form = IndividualLookupSearchForm(search_cached_data)

            # Request to IntegrationAdapter API
            api_response = _fetch_individuals_from_integration_adapter(form_data.copy())
            individuals_list = _extract_json_to_list(api_response.individuals)


            # Set a paginator if there are invdividuals
            if individuals_list:
                paginator = Paginator(individuals_list, 10)
                page = request.GET.get('page')

                try:
                    individuals = paginator.page(page)
                except PageNotAnInteger:
                    individuals = paginator.page(1)
                except EmptyPage:
                    individuals = paginator.page(paginator.num_pages)
            else:
                individuals = None
        else:
            form = IndividualLookupSearchForm()

    # Search in results view
    if request.method == 'POST':

        # Check if not known to Ofsted
        if request.POST.get('not-known') is not None:
            # Save not known to Ofsted data and redirect to personal details page for given type
            return mark_not_known_to_ofsted(referrer_type, application_id)

        form = IndividualLookupSearchForm(request.POST)

        if form.is_valid():
            form_data = {
                    'forename': form.cleaned_data['forenames'],
                    'surname': form.cleaned_data['last_name'],
                    'day': form.cleaned_data['day'],
                    'month': form.cleaned_data['month'],
                    'year': form.cleaned_data['year'],
                    'address1': form.cleaned_data['street'],
                    'town': form.cleaned_data['town'],
                    'postcode': form.cleaned_data['postcode']
                }

            # Get a data from search fields stored in cache
            if application_id in cache:
                cache.set(application_id, form_data)
            else:
                cache.add(application_id, form_data)

            # Request to IntegrationAdapter API
            api_response = _fetch_individuals_from_integration_adapter(form_data.copy())
            individuals_list = _extract_json_to_list(api_response.individuals)

            # Set a paginator if there are invdividuals
            if individuals_list:
                paginator = Paginator(individuals_list, 10)
                page = 1

                try:
                    individuals = paginator.page(page)
                except PageNotAnInteger:
                    individuals = paginator.page(1)
                except EmptyPage:
                    individuals = paginator.page(paginator.num_pages)
            else:
                individuals = None

            page = request.GET.get(page)

    # Fetch context from a referrer app for 'Applicant's data' box
    if not application_id or referrer_type not in DATA_FETCHER_MAPPING:
        context = {}
    else:
        context = DATA_FETCHER_MAPPING[referrer_type](application_id)

    context.update({
        'form': form,
        'individuals': individuals,
        'page': page,
        'referrer_type': referrer_type
    })

    return render(request, 'childminder_templates/personal-details-individual-lookup-search-result.html', context)

@login_required
@group_required(settings.ARC_GROUP, raise_exception=True)
@user_assigned_application
def personal_details_individual_lookup_search_choice(request):
    '''
    Choose one record and decide whether it has to be confirmed or marked as 'None to the Ofsted'
    '''
    individuals = None
    application_id = request.GET['id']
    referrer_type = request.GET.get('referrer')

    # Check if not known to Ofsted
    if request.method == 'POST' and request.POST.get('not-known') is not None:
        # Save not known to Ofsted data and redirect to personal details page for given type
        return mark_not_known_to_ofsted(referrer_type, application_id)

    if request.method == 'GET':
            form_data = cache.get(application_id)

            # Request to cygnum database
            api_response = _fetch_individuals_from_integration_adapter(form_data.copy())
            individuals_list = _extract_json_to_list(api_response.individuals)

            # Set a paginator if 'individuals_list' is setted
            if individuals_list:
                paginator = Paginator(individuals_list, 10)
                page = request.GET.get('page')

                try:
                    individuals = paginator.page(page)
                except PageNotAnInteger:
                    individuals = paginator.page(1)
                except EmptyPage:
                    individuals = paginator.page(paginator.num_pages)
            else:
                individuals = None

            compare = request.GET.get('compare')

    # Fetch context from a referrer app for 'Applicant's data' box
    if not application_id or referrer_type not in DATA_FETCHER_MAPPING:
        context = {}
    else:
        context = DATA_FETCHER_MAPPING[referrer_type](application_id)

    context.update({
        'individuals': individuals,
        'compare': compare,
        'referrer_type': referrer_type,
        'individuals_list': individuals_list,
        'page': page
    })

    return render(request, 'childminder_templates/personal-detials-individual-lookup-search-choice.html', context)


def mark_not_known_to_ofsted(referrer_type, application_id):
    '''
    For the given application type call the correct method to mark that the individual is not known
    :param referrer_type: the applicant or individual type
    :param application_id: the id of the application or individual
    :return:
    '''
    if referrer_type == 'nanny':
        return save_nanny_not_known_to_ofsted(application_id)
    elif referrer_type == 'childminder':
        return save_childminder_not_known_to_ofsted(application_id)
    elif referrer_type == 'household_member':
        return save_household_member_not_known_to_ofsted(application_id)


def save_nanny_not_known_to_ofsted(application_id):
    '''
    Mark a nanny applicant as being unknown to Ofsted
    :param application_id: the application to update
    :return: redirect to the application's personal details review
    '''
    api_response = NannyGatewayActions().read('previous-registration-details',
                                              params={'application_id': application_id})

    if api_response.status_code == 200:
        previous_registration_record = api_response.record
        previous_registration_record['previous_registration'] = False
        previous_registration_record['individual_id'] = 0

        NannyGatewayActions().put('previous-registration-details', params=previous_registration_record)
        log.debug("Handling submissions for nanny without previous registration details - updating details")
    else:
        previous_registration_new = {}
        previous_registration_new['application_id'] = application_id
        previous_registration_new['previous_registration'] = False
        previous_registration_new['individual_id'] = 0

        NannyGatewayActions().create('previous-registration-details',
                                     params=previous_registration_new)
        log.debug("Handling submissions for nanny without previous registration details - new details")

    return HttpResponseRedirect(build_url('nanny_personal_details_summary', get={'id': application_id}))


def save_childminder_not_known_to_ofsted(application_id):
    '''
    Mark a childminder applicant as being unknown to Ofsted
    :param application_id: the application to update
    :return: redirect to the application's personal details review
    '''
    if PreviousRegistrationDetails.objects.filter(application_id=application_id).exists():
        previous_reg_details = PreviousRegistrationDetails.objects.get(application_id=application_id)
    else:
        application = Application.objects.get(application_id=application_id)
        previous_reg_details = PreviousRegistrationDetails(application_id=application)

    previous_reg_details.previous_registration = False
    previous_reg_details.individual_id = 0
    previous_reg_details.save()

    log.debug("Handling submissions for childminder without previous registration details")
    return HttpResponseRedirect(build_url('personal_details_summary', get={'id': application_id}))


def save_household_member_not_known_to_ofsted(adult_id):
    '''
    Mark a household member applicant as being unknown to Ofsted
    :param adult_id: the adult to update
    :return: redirect to the adult's personal details review
    '''
    previous_registration_response = HMGatewayActions().list('previous-registration', params={'adult_id': adult_id})

    if previous_registration_response.status_code == 200:
        previous_registration_record = {
            'adult_id': adult_id,
            'previous_registration': False,
            'individual_id': 0,
        }

        HMGatewayActions().put('previous-registration', params=previous_registration_record)
    else:
        previous_registration_record = {
            'previous_registration': False,
            'individual_id': 0,
            'adult_id': adult_id
        }

        HMGatewayActions().create('previous-registration', params=previous_registration_record)

    log.debug("Handling submissions for household members without previous registration details")
    return HttpResponseRedirect(build_url('new_adults_summary', get={'id': adult_id}))


def _fetch_individuals_from_integration_adapter(form_values):
    url_params = {}
    if form_values['year'] and form_values['month'] and form_values['day']:
        url_params['dob'] = '{0}-{1}-{2}'.format(form_values.pop('year'), form_values.pop('month'), form_values.pop('day'))
    for key, value in form_values.items():
        if value:
           url_params[key] = value
    return get_individual_search_results(url_params)


def _extract_json_to_list(response):
    if type(response) is list:
        return response
    if type(response) is dict:
        item = [response]
        return item


def _rewrite_keys_for_search_fields(form_values):
    form_values['forenames'] = form_values.pop('forename')
    form_values['last_name'] = form_values.pop('surname')
    form_values['street'] = form_values.pop('address1')

    return form_values

