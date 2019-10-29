import logging

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.cache import cache
import requests

from ...decorators import group_required, user_assigned_application
from ...models import ApplicantPersonalDetails, ApplicantName, ApplicantHomeAddress
from ...forms.individual_lookup_forms import IndividualLookupSearchForm
from ...services.db_gateways import NannyGatewayActions

log = logging.getLogger()

BASE_CYGNUM_URL = 'https://build-lb-779835042.eu-west-2.elb.amazonaws.com/integration-adapter/api/v1/individuals-search/?'


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

DATA_FETCHER_MAPPING = {
    'childminder': fetch_childminder_data,
    'nanny': fetch_nanny_data
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
        if application_id in cache:
            form_data = cache.get(application_id)
            search_cached_data = _rewrite_keys_for_search_fields(form_data.copy())
            form = IndividualLookupSearchForm(search_cached_data)  
        else: 
            form = IndividualLookupSearchForm()

    elif request.method == 'POST':
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

            if application_id not in cache:
                cache.add(application_id, form_data)
            if application_id in cache:
                cache.set(application_id, form_data)

            return redirect('././results/?id='+application_id+'&referrer='+referrer_type)
    
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
    application_id = request.GET["id"]
    referrer_type = request.GET.get('referrer')

    if request.method == 'GET':
        # Check if form values are in cache
        if application_id in cache:
            form_data = cache.get(application_id)
            search_cached_data = _rewrite_keys_for_search_fields(form_data.copy())
            
            form = IndividualLookupSearchForm(search_cached_data)

            # Request to cygnum database
            try:
                api_response = _fetch_data_from_cygnum(form_data.copy())
                individuals_list = _extract_json_data_to_dict(api_response)
            except requests.exceptions.RequestException as e:
                print(e)

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
        else:
            form = IndividualLookupSearchForm()
    
    if request.method == 'POST':
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

            if application_id not in cache:
                cache.add(application_id, form_data)
            if application_id in cache:
                cache.set(application_id, form_data)
            
            try:
                api_response = _fetch_data_from_cygnum(form_data.copy())
                individuals_list = _extract_json_data_to_dict(api_response)
            except requests.exceptions.RequestException as e:
                print(e)

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
    application_id = request.GET["id"]
    referrer_type = request.GET.get('referrer')

    if request.method == 'GET':
            form_data = cache.get(application_id)
            # Request to cygnum database
            try:
                api_response = _fetch_data_from_cygnum(form_data.copy())
                individuals_list = _extract_json_data_to_dict(api_response)
            except requests.exceptions.RequestException as e:
                print(e)

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

def _fetch_data_from_cygnum(form_values):
    build_request = BASE_CYGNUM_URL + ''
    form_values['dob'] = '{0}-{1}-{2}'.format(form_values.pop("year"), form_values.pop("month"), form_values.pop("day"))
    for key, value in form_values.items():
        if value:
            build_request = build_request + '{0}={1}&'.format(key, value)
    build_request = build_request[0:-1]
    print(build_request)
    
    return requests.get(build_request, verify=False, auth=('beta', 'accept'))

def _extract_json_data_to_dict(response):
    response = response.json()
    if 'Individual' in response:
        if type(response['Individual']) is list:
            return response['Individual']
        if type(response['Individual']) is dict:
            item = [response['Individual']]
            return item

def _rewrite_keys_for_search_fields(form_values):
    form_values['forenames'] = form_values.pop('forename')
    form_values['last_name'] = form_values.pop('surname')
    form_values['street'] = form_values.pop('address1')

    return form_values

