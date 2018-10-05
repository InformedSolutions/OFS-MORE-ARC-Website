from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render

from arc_application import address_helper
from arc_application.forms.childminder_forms.form import OtherPersonPreviousPostcodeEntry, OtherPeoplePreviousAddressLookupForm, \
    OtherPeoplePreviousAddressManualForm
from arc_application.models import PreviousAddress
from arc_application.review_util import build_url
from arc_application.decorators import group_required, user_assigned_application


@login_required
@group_required(settings.ARC_GROUP)
@user_assigned_application
def address_state_dispatcher(request):
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
    context = get_context(request)

    if request.method == 'GET':
        context['form'] = OtherPersonPreviousPostcodeEntry()
        return render(request, 'childminder_templates/previous-address-select.html', context)

    if request.method == 'POST':

        if 'add-another' in request.POST:
            form = OtherPersonPreviousPostcodeEntry()
            context['form'] = form
            return render(request, 'childminder_templates/previous-address-select.html', context)

        form = OtherPersonPreviousPostcodeEntry(request.POST)
        context['form'] = form

        if form.is_valid():
            postcode = form.cleaned_data['postcode']

            if 'postcode-search' in request.POST:
                return postcode_selection(request)

        return render(request, 'childminder_templates/previous-address-select.html', context)


def postcode_selection(request):
    """
    Function to allow the user to select the postcode from the list, or redirect appropriately
    :param request: Standard Httprequest object
    :return:
    """
    context = get_context(request)

    if request.method == 'GET':
        # Call addressing API with entered postcode
        addresses = address_helper.AddressHelper.create_address_lookup_list(context['postcode'])

        # Populate form for page with choices from this API call
        context['form'] = OtherPeoplePreviousAddressLookupForm(choices=addresses)

        return render(request, 'childminder_templates/previous-address-lookup.html', context)

    if request.method == 'POST':
        addresses = address_helper.AddressHelper.create_address_lookup_list(request.POST['postcode'])

        if 'postcode-search' in request.POST:
            context['form'] = OtherPeoplePreviousAddressLookupForm(choices=addresses)
            return render(request, 'childminder_templates/previous-address-lookup.html', context)

        current_form = OtherPeoplePreviousAddressLookupForm(request.POST, choices=addresses)
        context['form'] = current_form

        if current_form.is_valid():
            return postcode_submission(request)

    return render(request, 'childminder_templates/previous-address-lookup.html', context)


def postcode_manual(request):
    """
    Function to allow the user to manually enter an address, or be redirected appropriately
    :param request: Standard Httprequest object
    :return:
    """
    context = get_context(request)

    if request.method == 'GET':
        context['form'] = OtherPeoplePreviousAddressManualForm()
        return render(request, 'childminder_templates/other-people-previous-address-manual.html', context)

    if request.method == 'POST':
        current_form = OtherPeoplePreviousAddressManualForm(request.POST)
        context['postcode'] = request.POST['postcode2']
        context['form'] = current_form

        if current_form.is_valid():
            return postcode_submission(request)

        return render(request, 'childminder_templates/other-people-previous-address-manual.html', context)


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
            return HttpResponseRedirect(build_url('other_people_summary', get={'id': request.POST['id']}))
        elif 'add-another' in request.POST:
            return postcode_entry(request)


def address_update(request):
    """
    Function to allow the user to update an entry to the address table from the other people summary page
    :param request: Standard Httprequest object
    :return:
    """
    context = get_context(request)

    if request.method == 'GET':
        context['form'] = OtherPeoplePreviousAddressManualForm(id=request.GET['address_id'])
        return render(request, 'childminder_templates/previous-address-manual-update.html', context)

    if request.method == 'POST':
        current_form = OtherPeoplePreviousAddressManualForm(request.POST)
        context['form'] = current_form
        address_record = PreviousAddress.objects.get(previous_name_id=context['address_id'])
        if current_form.is_valid():
            # For ease of use, update saving is done here rather than in submission section, adding it would make it
            # harder to understand
            address_record.street_line1 = current_form.cleaned_data['street_name_and_number']
            address_record.street_line2 = current_form.cleaned_data['street_name_and_number2']
            address_record.town = current_form.cleaned_data['town']
            address_record.county = current_form.cleaned_data['county']
            address_record.country = 'United Kingdom'
            address_record.postcode = current_form.cleaned_data['postcode']
            address_record.save()

            return HttpResponseRedirect(build_url('other_people_summary', get={'id': context['id']}))

        return render(request, 'childminder_templates/previous-address-manual-update.html', context)


def get_stored_addresses(person_id, person_type):
    """
    A utility function to get the addresses already stored in the previous address table for the current person
    :param person_id: The id of the person involved (adult or child)
    :param person_type: Whether the person is an adult or child
    :return:
    """
    return PreviousAddress.objects.filter(person_id=person_id, person_type=person_type)


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
        'referrer'
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
    context['list_url'] = build_url('other_people_summary', get={'id': url_variables_dict['id']})

    # These two urls need certain 'states' to be built, therefore state is saved then changed, and finally reset
    url_variables_dict['state'] = 'manual'
    context['manual_url'] = build_url('other-people-previous-addresses', get=url_variables_dict)

    url_variables_dict['state'] = 'entry'
    context['entry_url'] = build_url('other-people-previous-addresses', get=url_variables_dict)

    return context
