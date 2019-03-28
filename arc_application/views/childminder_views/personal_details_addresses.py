from datetime import date
import logging
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import render

from ...address_helper import AddressHelper
from ...decorators import group_required, user_assigned_application
from ...forms.previous_addresses import PreviousAddressEntryForm, PreviousAddressSelectForm, \
    PreviousAddressManualForm
from ...models import PreviousAddress, ApplicantPersonalDetails
from ...review_util import build_url

# Initiate logging
log = logging.getLogger('')

@login_required
@group_required(settings.ARC_GROUP)
@user_assigned_application
def personal_details_previous_address(request):
    """
    Dispatcher function to handle the different pages to be rendered.
    :param request: HttpRequest object.
    :return: function call for the appropriate state.
    """
    request_data = getattr(request, request.method)

    state = request_data.get('state')

    remove = request_data.get('remove', False)
    if remove:
        remove_address_pk = get_remove_address_pk(request_data)
        remove_previous_address(previous_name_id=remove_address_pk)

    if state == 'entry':
        return postcode_entry(request, remove=remove)

    if state == 'selection':
        return postcode_selection(request, remove=remove)

    if state == 'manual':
        return postcode_manual(request, remove=remove)

    if state == 'submission':
        return postcode_submission(request)

    raise ValueError('State not found. State: {0}'.format(state))


def postcode_entry(request, remove=False):
    """
    Function to refer the user to the postcode entry page, or redirect them appropriately should it be a POST request
    :param request: Standard Httprequest object
    :return:
    """
    context = get_context(request)

    if request.method == 'GET' or remove is True:
        context['form'] = PreviousAddressEntryForm()
        log.debug("Render previous address entry page")
        return render(request, 'childminder_templates/previous-address-entry.html', context)

    elif request.method == 'POST':

        if 'add-another' in request.POST:
            form = PreviousAddressEntryForm()
            context['form'] = form
            log.debug("Render previous address entry page - from add-another")
            return render(request, 'childminder_templates/previous-address-entry.html', context)

        form = PreviousAddressEntryForm(request.POST)
        context['form'] = form

        if form.is_valid():
            postcode = form.cleaned_data['postcode']

            if 'postcode-search' in request.POST:
                return postcode_selection(request)

        log.debug("Handling submissions for previous address page - postcode lookup")
        return render(request, 'childminder_templates/previous-address-entry.html', context)


def postcode_selection(request, remove=False):
    """
    Function to allow the user to select the postcode from the list, or redirect appropriately
    :param request: Standard Httprequest object
    :return:
    """
    context = get_context(request)
    context['state'] = 'selection'

    if request.method == 'GET' or remove is True:
        # Call addressing API with entered postcode
        postcode = context.get('postcode', None)
        addresses = AddressHelper.create_address_lookup_list(postcode)

        # Populate form for page with choices from this API call
        context['form'] = PreviousAddressSelectForm(choices=addresses)
        log.debug("Render previous address postcode selection")
        return render(request, 'childminder_templates/previous-address-select.html', context)

    elif request.method == 'POST':

        # If the user selects 'I can't find my address in the list', redirect them to the manual address page.
        # Also, populate the manual form with data that has already been entered (postcode, move in/out)
        request_data = getattr(request, request.method)

        swap_to_manual = request_data.get('swap-to-manual', None)
        if swap_to_manual is not None:
            postcode = request_data['postcode']

            moved_in_day = request_data['moved_in_date_0']
            moved_in_month = request_data['moved_in_date_1']
            moved_in_year = request_data['moved_in_date_2']

            moved_out_day = request_data['moved_out_date_0']
            moved_out_month = request_data['moved_out_date_1']
            moved_out_year = request_data['moved_out_date_2']

            address = {
                'postcode': postcode,
                'moved_in_date': [moved_in_day, moved_in_month, moved_in_year],
                'moved_out_date': [moved_out_day, moved_out_month, moved_out_year]
            }
            log.debug("Swap address input to manual")
            return postcode_manual(request, swap_to_manual=True, address=address)

        addresses = AddressHelper.create_address_lookup_list(request.POST['postcode'])

        if 'postcode-search' in request.POST:
            context['form'] = PreviousAddressSelectForm(choices=addresses)
            return render(request, 'childminder_templates/previous-address-select.html', context)

        current_form = PreviousAddressSelectForm(request.POST, choices=addresses)
        context['form'] = current_form

        if current_form.is_valid():
            return postcode_submission(request)

    log.debug("Handling submissions for previous address page - postcode select")
    return render(request, 'childminder_templates/previous-address-select.html', context)


def postcode_manual(request, remove=False, swap_to_manual=False, address=None):
    """
    Function to allow the user to manually enter an address, or be redirected appropriately
    :param request: Standard Httprequest object
    :return:
    """
    context = get_context(request)
    context['state'] = 'manual'

    if request.method == 'GET' or remove is True or swap_to_manual is True:
        if not swap_to_manual:
            context['form'] = PreviousAddressManualForm()
        else:
            # If you've come from the address selection page, then populate the form with the entered data
            context['form'] = PreviousAddressManualForm(initial=address)

        log.debug("Render previous address - manual entry page")
        return render(request, 'childminder_templates/previous-address-manual.html', context)

    elif request.method == 'POST':
        current_form = PreviousAddressManualForm(request.POST)
        context['postcode'] = request.POST['postcode']
        context['form'] = current_form

        if current_form.is_valid():
            return postcode_submission(request)

        log.debug("Handling submissions for previous address page - manual entry")
        return render(request, 'childminder_templates/previous-address-manual.html', context)


def postcode_submission(request):
    """
    Function to allow submission of data from the other views into the previous address table
    :param request: Standard Httprequest object
    :return:
    """
    if request.method == 'POST':
        if request.POST['state'] == 'manual':
            line1 = request.POST['street_line1']
            line2 = request.POST['street_line2']
            town = request.POST['town']
            county = request.POST['county']
            postcode = request.POST['postcode']

        else:
            selected_address_index = int(request.POST['address'])
            selected_address = AddressHelper.get_posted_address(selected_address_index, request.POST['postcode'])
            line1 = selected_address['line1']
            line2 = selected_address['line2']
            town = selected_address['townOrCity']
            county = ''
            postcode = selected_address['postcode']

        moved_in_day = int(request.POST['moved_in_date_0'])
        moved_in_month = int(request.POST['moved_in_date_1'])
        moved_in_year = int(request.POST['moved_in_date_2'])

        moved_out_day = int(request.POST['moved_out_date_0'])
        moved_out_month = int(request.POST['moved_out_date_1'])
        moved_out_year = int(request.POST['moved_out_date_2'])

        moved_in_date = date(moved_in_year, moved_in_month, moved_in_day)
        moved_out_date = date(moved_out_year, moved_out_month, moved_out_day)

        # Actual saving is the same regardless of lookup, so done beneath
        previous_address_record = create_previous_address(
            person_id=request.POST['person_id'],
            person_type=request.POST['person_type'],
            street_line1=line1,
            street_line2=line2,
            town=town,
            county=county,
            country='United Kingdom',
            postcode=postcode
        )

        # Update previous address moved in/out dates
        previous_address_record.moved_in_date = moved_in_date
        previous_address_record.moved_out_date = moved_out_date
        previous_address_record.save()

        # If updating a record related to the applicant, set their moved in/out dates for their current address
        if previous_address_record.person_type == 'APPLICANT':
            update_applicant_current_address(previous_address_record.person_id)

        if 'save-and-continue' in request.POST:
            log.debug("Handling submissions for previous address page - following save and continue")
            return HttpResponseRedirect(build_url('personal_details_summary', get={'id': request.POST['id']}))
        elif 'add-another' in request.POST:
            log.debug("Handling submissions for previous address page - following add another")
            return postcode_entry(request)


@login_required
@group_required(settings.ARC_GROUP)
@user_assigned_application
def personal_details_previous_address_change(request):
    """
    Function to allow the user to update an entry to the address table from the other people summary page
    :param request: Standard Httprequest object
    :return:
    """
    context = get_context(request)
    request_data = getattr(request, request.method)
    remove_address_pk = get_remove_address_pk(request_data)

    if remove_address_pk is not None:
        remove_previous_address(previous_name_id=remove_address_pk)
        log.debug("Remove previous address")
        return HttpResponseRedirect(build_url('personal_details_summary', get={'id': context['id']}))

    if request.method == 'GET':
        record = get_previous_address(pk=request.GET['address_id'])
        context['form'] = PreviousAddressManualForm(record=record)
        log.debug("Render change previous address page")
        return render(request, 'childminder_templates/previous-address-change.html', context)

    elif request.method == 'POST':
        address_id = context['address_id']
        address_record = get_previous_address(address_id)

        current_form = PreviousAddressManualForm(request.POST)
        context['form'] = current_form

        if current_form.is_valid():
            # For ease of use, update saving is done here rather than in submission section, adding it would make it
            # harder to understand
            address_record.street_line1 = current_form.cleaned_data['street_line1']
            address_record.street_line2 = current_form.cleaned_data['street_line2']
            address_record.town = current_form.cleaned_data['town']
            address_record.county = current_form.cleaned_data['county']
            address_record.country = 'United Kingdom'
            address_record.postcode = current_form.cleaned_data['postcode']

            # Update previous address moved in/out dates
            address_record.moved_in_date = current_form.cleaned_data['moved_in_date']
            address_record.moved_out_date = current_form.cleaned_data['moved_out_date']

            address_record.save()

            # If updating a record related to the applicant, set their moved in/out dates for their current address
            if address_record.person_type == 'APPLICANT':
                update_applicant_current_address(address_record.person_id)
            log.debug("Handling submissions for change previous address page")
            return HttpResponseRedirect(build_url('personal_details_summary', get={'id': context['id']}))

        log.debug("Render change previous address page")
        return render(request, 'childminder_templates/previous-address-change.html', context)


def get_stored_addresses(person_id, person_type):
    """
    A utility function to get the addresses already stored in the previous address table for the current person
    :param person_id: The id of the person involved (adult or child)
    :param person_type: Whether the person is an adult or child
    :return:
    """
    unsorted_addresses = filter_previous_address(person_id=person_id, person_type=person_type)

    # If an address does not have an order associated with it, display these addresses first.
    return sorted(unsorted_addresses, key=lambda address: address.order if address.order else 0)


def get_context(request):
    """
    Function to grab all the context required for rendering the views, by calling, in turn, the functions which grab
    data from the HttpResponse object.

    XXX: These need to be called in a particular order to avoid excessively long urls which exceed the nginx buffer size.

    :param request: HttpResponse object from which to grab the data.
    :return: context: dict containing all the information required by the views.
    """
    context = get_url_data(request)
    context.update(get_link_urls(context))
    context.update(get_post_data(request))
    return context


def get_url_data(request):
    """
    Function to grab variables required for the context and link urls from the request url.
    :param request: HttpResponse object from which to grab the data.
    :return: dict whose (key, value) pairs are the strings in url_variables_to_check and their respective values.
    """
    url_variables_to_check = [
        'id',
        'state',
        'person_id',
        'person_type'
    ]

    return dict((var, getattr(request, request.method).get(var, None)) for var in url_variables_to_check)


def get_post_data(request):
    """
    Function to grab variables required for the context from the POST data.
    :param request: HttpResponse object from which to grab the data.
    :return: dict whose (key, value) pairs are the strings in url_variables_to_check and their respective values, with
             an additional 'previous_addresses' value for the context.
    """
    post_vars_to_check = [
        'postcode',
        'address',
        'lookup',
        'address_id',
        'referrer',
        'state'
    ]

    post_data_vars = dict((var, getattr(request, request.method).get(var, None)) for var in post_vars_to_check)

    url_vars = get_url_data(request)
    post_data_vars['previous_addresses'] = get_stored_addresses(url_vars['person_id'], url_vars['person_type'])

    return post_data_vars


def get_link_urls(url_variables_dict):
    """
    The 'previous address' templates require urls for links contained within the page.
    These require the list of url variables from get_url_data.
    :param: url_variables_dict: dict containing the required url variables.
    :return: context: dict containing the urls to be passed as context variables.
    """
    context = dict()

    # List url does not require a new state, so set after state changes, once it has been reset
    context['list_url'] = build_url('personal_details_summary', get={'id': url_variables_dict['id']})

    # These two urls need certain 'states' to be built, therefore state is saved then changed, and finally reset
    url_variables_dict['state'] = 'manual'
    context['manual_url'] = build_url('personal_details_previous_addresses', get=url_variables_dict)

    url_variables_dict['state'] = 'entry'
    context['entry_url'] = build_url('personal_details_previous_addresses', get=url_variables_dict)

    return context


def get_previous_address(pk):
    return PreviousAddress.objects.get(pk=pk)


def filter_previous_address(**kwargs):
    return PreviousAddress.objects.filter(**kwargs)


def create_previous_address(**kwargs):
    if kwargs.get('country') is not None:
        country = kwargs.pop('country')
    else:
        # Default
        country = 'United Kingdom'

    if kwargs.get('order') is not None:
        # If order is being set
        order = kwargs.pop('order')
    else:
        # Calculate order
        person_id = kwargs.get('person_id')
        person_type = kwargs.get('person_type')

        stored_address = get_stored_addresses(person_id, person_type)
        order = len(stored_address) + 1

    previous_address_record = PreviousAddress(**kwargs, country=country, order=order)
    previous_address_record.save()

    return previous_address_record


def remove_previous_address(**kwargs):
    """
    :param kwargs: kwargs for getting the PreviousAddress record, must contain information to select exactly one record.
    :return: None
    """
    try:
        previous_address_record = PreviousAddress.objects.get(**kwargs)
        previous_address_record.delete()
    except ObjectDoesNotExist:
        # If the address cannot be found, we assume that the user has already deleted the address.
        pass


def get_remove_address_pk(request_data):
    for key, value in request_data.items():
        if key.startswith('remove-'):
            return key[7:]

    return None


def update_applicant_current_address(application_id):
    applicant_personal_details_record = ApplicantPersonalDetails.objects.get(application_id=application_id)
    previous_address_records = PreviousAddress.objects.filter(person_id=application_id)

    if not previous_address_records:
        # Set moved_in_date to Applicant's DOB
        applicant_personal_details_record.moved_in_date = applicant_personal_details_record.date_of_birth

    else:
        # Set moved_in_date to latest moved_out_date of previous addresses
        applicant_personal_details_record.moved_in_date = get_latest_moved_out_date(previous_address_records)

    applicant_personal_details_record.moved_out_date = date.today()
    applicant_personal_details_record.save()


def get_latest_moved_out_date(previous_address_list):
    # Construct a list of moved_out_dates, removes redundant data
    moved_out_date_list = [address.moved_out_date for address in previous_address_list if
                           address.moved_out_date is not None]

    # Return the first element of the sorted list, as this will be the greatest moved_out_date
    latest_moved_out_date = sorted(moved_out_date_list, reverse=True)[0]
    return latest_moved_out_date
