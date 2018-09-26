from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render

from .. import address_helper
from ..forms.form import OtherPersonPreviousPostcodeEntry, OtherPeoplePreviousAddressLookupForm, \
    OtherPeoplePreviousAddressManualForm
from ..models import PreviousAddress
from ..review_util import build_url
from ..decorators import group_required, user_assigned_application


@login_required
@group_required(settings.ARC_GROUP)
@user_assigned_application
def personal_details_previous_address(request):
    """
    Dispatcher function to handle the different pages to be rendered.
    :param request: HttpRequest object.
    :return: function call for the appropriate state.
    """
    state = getattr(request, request.method).get('state')

    if state == 'entry':
        return postcode_entry(request)

    if state == 'selection':
        return postcode_selection(request)

    if state == 'manual':
        return postcode_manual(request)

    if state == 'submission':
        return postcode_submission(request)

    if state == 'update':
        return address_update(request)


def postcode_entry(request):
    """
    Function to refer the user to the postcode entry page, or redirect them appropriately should it be a POST request
    :param request: Standard Httprequest object
    :return:
    """
    context = dict()

    if request.method == 'GET':
        context['form'] = OtherPersonPreviousPostcodeEntry()

        # Grabs any relative urls needed for the page (enter address manually, for example)
        url_variables_data = get_url_data(request)
        body_variables_data = get_post_data(request)
        link_urls = get_link_urls(url_variables_data)
        context.update(link_urls)
        context.update(url_variables_data)
        context.update(body_variables_data)

        return render(request, 'previous-address-select.html', context)

    if request.method == 'POST':

        url_variables_data = get_url_data(request)
        body_variables_data = get_post_data(request)
        link_urls = get_link_urls(url_variables_data)
        context.update(link_urls)
        context.update(url_variables_data)
        context.update(body_variables_data)

        if 'add-another' in request.POST:
            form = OtherPersonPreviousPostcodeEntry()
            context['form'] = form
            return render(request, 'previous-address-select.html', context)

        form = OtherPersonPreviousPostcodeEntry(request.POST)
        context['form'] = form
        context.update(get_post_data(request))

        if form.is_valid():
            postcode = form.cleaned_data['postcode']

            if 'postcode-search' in request.POST:
                return postcode_selection(request)

        return render(request, 'previous-address-select.html', context)


def postcode_selection(request):
    """
    Function to allow the user to select the postcode from the list, or redirect appropriately
    :param request: Standard Httprequest object
    :return:
    """
    context = dict()

    if request.method == 'GET':
        context = get_url_data(request)
        context.update(get_link_urls(context))

        body_variables = get_post_data(request)

        # Call addressing API with entered postcode
        addresses = address_helper.AddressHelper.create_address_lookup_list(body_variables['postcode'])

        # Populate form for page with choices from this API call
        context['form'] = OtherPeoplePreviousAddressLookupForm(choices=addresses)

        return render(request, 'previous-address-lookup.html', context)

    if request.method == 'POST':
        addresses = address_helper.AddressHelper.create_address_lookup_list(request.POST['postcode'])

        if 'postcode-search' in request.POST:
            context.update(get_url_data(request))
            context['state'] = 'selection'
            context.update(get_link_urls(context))
            context.update(get_post_data(request))
            context['form'] = OtherPeoplePreviousAddressLookupForm(choices=addresses)
            return render(request, 'previous-address-lookup.html', context)

        current_form = OtherPeoplePreviousAddressLookupForm(request.POST, choices=addresses)
        context['form'] = current_form

        if current_form.is_valid() and 'save-and-continue' in request.POST:
            return postcode_submission(request)

        elif current_form.is_valid() and 'add-another' in request.POST:
            return postcode_submission(request)

        context.update(get_url_data(request))
        context['state'] = 'selection'
        context.update(get_link_urls(context))
        context.update(get_post_data(request))

    return render(request, 'previous-address-lookup.html', context)


def postcode_manual(request):
    """
    Function to allow the user to manually enter an address, or be redirected appropriately
    :param request: Standard Httprequest object
    :return:
    """
    context = dict()

    if request.method == 'GET':
        url_data = get_url_data(request)
        body_data = get_post_data(request)
        context.update(get_link_urls(url_data))
        context.update(url_data)
        context.update(body_data)
        context['form'] = OtherPeoplePreviousAddressManualForm()
        return render(request, 'other-people-previous-address-manual.html', context)

    if request.method == 'POST':
        current_form = OtherPeoplePreviousAddressManualForm(request.POST)
        context['postcode'] = request.POST['postcode2']
        context['form'] = current_form

        if current_form.is_valid():
            return postcode_submission(request)

        return render(request, 'other-people-previous-address-manual.html', context)


def postcode_submission(request):
    """
    Function to allow submission of data from the other views into the previous address table
    :param request: Standard Httprequest object
    :return:
    """
    if request.method == 'POST':
        if request.POST['state'] == 'manual':
            line1 = request.POST['street_name_and_number']
            line2 = request.POST['street_name_and_number2']
            town = request.POST['town']
            county = request.POST['county']
            postcode = request.POST['postcode']

        else:
            selected_address_index = int(request.POST['address'])
            selected_address = address_helper.AddressHelper.get_posted_address(selected_address_index, request.POST['postcode'])
            line1 = selected_address['line1']
            line2 = selected_address['line2']
            town = selected_address['townOrCity']
            county = ''
            postcode = selected_address['postcode']

        # Actual saving is the same regardless of lookup, so done beneath
        previous_address_record = PreviousAddress(person_id=request.POST['person_id'],
                                                  person_type=request.POST['person_type'],
                                                  street_line1=line1,
                                                  street_line2=line2,
                                                  town=town,
                                                  county=county,
                                                  country='United Kingdom',
                                                  postcode=postcode)
        previous_address_record.save()

        if 'save-and-continue' in request.POST:
            return HttpResponseRedirect(build_url('personal_details_summary', get={'id': request.POST['id']}))
        elif 'add-another' in request.POST:
            return postcode_entry(request)


def address_update(request):
    """
    Function to allow the user to update an entry to the address table from the other people summary page
    :param request: Standard Httprequest object
    :return:
    """
    if request.method == 'GET':
        # Populate form with entry from table, uses address primary key to do this
        context = get_url_data(request)
        context.update(get_link_urls(context))
        context.update(get_post_data(request))
        context['form'] = OtherPeoplePreviousAddressManualForm(id=request.GET['address_id'])

        return render(request, 'previous-address-manual-update.html', context)

    if request.method == 'POST':
        context = get_url_data(request)
        context.update(get_link_urls(context))
        context.update(get_post_data(request))

        current_form = OtherPeoplePreviousAddressManualForm(request.POST)
        context['form'] = current_form
        address_record = PreviousAddress.objects.get(previous_name_id=context['address_id'])
        if current_form.is_valid():
            # For ease of use, update saving is done here raather than in submission section, adding it would make it
            # harder to understand
            address_record.street_line1 = current_form.cleaned_data['street_name_and_number']
            address_record.street_line2 = current_form.cleaned_data['street_name_and_number2']
            address_record.town = current_form.cleaned_data['town']
            address_record.county = current_form.cleaned_data['county']
            address_record.country = 'United Kingdom'
            address_record.postcode = current_form.cleaned_data['postcode']
            address_record.save()

            return HttpResponseRedirect(build_url('personal_details_summary', get={'id': context['id']}))

        return render(request, 'previous-address-manual-update.html', context)


def get_stored_addresses(person_id, person_type):
    """
    A utility function to get the addresses already stored in the previous address table for the current person
    :param person_id: The id of the person involved (adult or child)
    :param person_type: Whether the person is an adult or child
    :return:
    """
    return PreviousAddress.objects.filter(person_id=person_id, person_type=person_type)


def get_url_data(request):
    url_vars = dict()
    request_method = request.method

    url_variables_to_check = [
        'id',
        'state',
        'person_id',
        'person_type'
    ]

    for var in url_variables_to_check:
        url_vars[var] = getattr(request, request_method)[var]

    return url_vars


def get_post_data(request):
    post_data_vars = dict()

    body_variables_to_check = [
        'postcode',
        'address',
        'lookup',
        'address_id',
        'referrer'
    ]

    for var in body_variables_to_check:
        post_data_vars[var] = getattr(request, request.method).get(var, default=None)

    url_vars = get_url_data(request)
    post_data_vars['previous_addresses'] = get_stored_addresses(url_vars['person_id'], url_vars['person_type'])

    return post_data_vars


def get_link_urls(url_variables_dict):
    """
    The previous address templates require urls for links contained within the page.
    This helper function generates them using the current context/url variables, before returning that same context dict
    :param: context: dict containing info to be passed to the render function.
    :return: context: same dict as was passed as arg, with additional url information included.
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
