import json

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render

from arc_application import address_helper
from arc_application.forms.form import OtherPersonPreviousPostcodeEntry, OtherPeoplePreviousAddressLookupForm, \
    OtherPeoplePreviousAddressManualForm
from arc_application.models import PreviousAddress
from arc_application.review_util import build_url
from ..decorators import group_required, user_assigned_application


@login_required
@group_required(settings.ARC_GROUP)
@user_assigned_application
def address_state_dispatcher(request):
    """
    Dispatcher function to handle the different pages to be rendered
    :param request: Standard Httprequest object
    :return:
    """

    context = get_context(request)
    context = get_urls(context)

    if context['state'] == 'entry':
        return postcode_entry(request, context)

    if context['state'] == 'selection':
        return postcode_selection(request, context)

    if context['state'] == 'manual':
        return postcode_manual(request, context)

    if context['state'] == 'submission':
        return postcode_submission(request, context)

    if context['state'] == 'update':
        return address_update(request, context)


def postcode_entry(request, context):
    """
    Function to refer the user to the postcode entry page, or redirect them appropriately should it be a POST request
    :param request: Standard Httprequest object
    :param context: See get_context declaration for definition
    :return:
    """
    current_form = OtherPersonPreviousPostcodeEntry()
    context['form'] = current_form

    if request.method == 'GET':
        # Grabs any relative urls needed for the page (enter address manually, for example)
        context = get_urls(context)

        return render(request, 'previous-address-select.html', context)

    if request.method == 'POST':
        current_form = OtherPersonPreviousPostcodeEntry(request.POST)
        context['form'] = current_form

        # Add the fully finished form to the context, so it can be submitted to the next page or saved
        if current_form.is_valid():
            context = get_context(request)
            postcode = current_form.cleaned_data['postcode']
            context['postcode'] = postcode

            # Define next sate to perform get request on
            context['state'] = 'selection'
            return HttpResponseRedirect(build_url('other-people-previous-addresses', get=context))

        return render(request, 'previous-address-select.html', context)


def postcode_selection(request, context):
    """
    Function to allow the user to select the postcode from the list, or redirect appropriately
    :param request: Standard Httprequest object
    :param context: See get_context declaration for definition
    :return:
    """

    if request.method == 'GET':
        context = get_urls(context)

        # Call addressing API with entered postcode
        addresses = address_helper.AddressHelper.create_address_lookup_list(context['postcode'])

        # Populate form for page with choices from this API call
        context['form'] = OtherPeoplePreviousAddressLookupForm(choices=addresses)

        return render(request, 'previous-address-lookup.html', context)

    if request.method == 'POST':
        addresses = address_helper.AddressHelper.create_address_lookup_list(context['postcode'])
        current_form = OtherPeoplePreviousAddressLookupForm(request.POST, choices=addresses)
        context['form'] = current_form
        if current_form.is_valid():
            context = get_context(request)
            address = current_form.cleaned_data['address']
            context['address'] = address
            context['state'] = 'submission'

            if 'save-and-continue' in request.POST.keys():
                context['referrer'] = 'save-and-continue'
            elif "add-another" in request.POST.keys():
                context['referrer'] = "add-another"

            # Different things must be done for submission if it is manual or a postcode lookup, this variable
            # differentiates the two functions
            context['lookup'] = True

            return HttpResponseRedirect(build_url('other-people-previous-addresses', get=context))

    return render(request, 'previous-address-lookup.html', context)


def postcode_manual(request, context):
    """
    Function to allow the user to manually enter an address, or be redirected appropriately
    :param request: Standard Httprequest object
    :param context: See get_context declaration for definition
    :return:
    """

    if request.method == 'GET':
        context = get_urls(context)
        context['form'] = OtherPeoplePreviousAddressManualForm()

        return render(request, 'other-people-previous-address-manual.html', context)

    if request.method == 'POST':
        current_form = OtherPeoplePreviousAddressManualForm(request.POST)
        context['form'] = current_form
        if current_form.is_valid():
            # Store entered address as json to be sent to to the submission view to be saved
            context['address'] = json.dumps({'line1': current_form.cleaned_data['street_name_and_number'],
                                             'line2': current_form.cleaned_data['street_name_and_number2'],
                                             'townOrCity': current_form.cleaned_data['town'],
                                             'county': current_form.cleaned_data['county'],
                                             'postcode': current_form.cleaned_data['postcode']})
            context['state'] = 'submission'

            # As this is a manual entry rather than a postcode lookup, this is set to false
            context['lookup'] = False

            return HttpResponseRedirect(build_url('other-people-previous-addresses', get=context))

        return render(request, 'other-people-previous-address-manual.html', context)


def postcode_submission(request, context):
    """
    Function to allow submission of data from the other views into the previous address table
    :param request: Standard Httprequest object
    :param context: See get_context declaration for definition
    :return:
    """

    if request.method == 'GET':

        # If this is a postcode lookup
        if context['lookup'] == 'True':
            # The original postcode selection returns an index, which when called again the addressing API, returns
            # the real value
            selected_address_index = int(context["address"])
            selected_address = address_helper.AddressHelper.get_posted_address(
                selected_address_index, context["postcode"])
            line1 = selected_address['line1']
            line2 = selected_address['line2']
            town = selected_address['townOrCity']
            postcode = selected_address['postcode']
        else:
            # If a manual entry, load the json into a dictionary and parse appropriately
            selected_address = json.loads(context['address'])
            line1 = selected_address['line1']
            line2 = selected_address['line2']
            town = selected_address['townOrCity']
            postcode = selected_address['postcode']

        # Actual saving is the same regardless of lookup, so done beneath
        previous_address_record = PreviousAddress(person_id=context['person_id'],
                                                  person_type=context['person_type'],
                                                  street_line1=line1,
                                                  street_line2=line2,
                                                  town=town,
                                                  county='',
                                                  country='United Kingdom',
                                                  postcode=postcode)
        previous_address_record.save()

        # Next state is set to entry, so that they may enter a new address or continue
        context['state'] = 'entry'
        if context['referrer'] == 'add-another':
            return HttpResponseRedirect(build_url('personal_details_previous_addresses', get=context))
        elif context['referrer'] == 'save-and-continue':
            return HttpResponseRedirect(build_url('other_people_summary', get=context))
        else:
            return HttpResponseRedirect(build_url('personal_details_previous_addresses', get=context))


def address_update(request, context):
    """
    Function to allow the user to update an entry to the address table from the other people summary page
    :param request: Standard Httprequest object
    :param context: See get_context declaration for definition
    :return:
    """
    if request.method == 'GET':
        # Populate form with entry from table, uses address primary key to do this
        context['form'] = OtherPeoplePreviousAddressManualForm(id=request.GET['address_id'])

        return render(request, 'previous-address-manual-update.html', context)

    if request.method == 'POST':
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

            return HttpResponseRedirect(build_url('other_people_summary', get={'id': context['id']}))

        return render(request, 'previous-address-manual-update.html', context)


def get_stored_addresses(person_id, person_type):
    """
    A utility function to get the addresses already stored in the previous address table for the current person
    :param person_id: The id of the person involved (adult or child)
    :param person_type: Whether the person is an adult or child
    :return:
    """
    address_queryset = PreviousAddress.objects.filter(person_id=person_id, person_type=person_type)
    return address_queryset


def get_context(request):
    """
    A utility method to grab either the get or post context for use in the views
    :param request: The current httprequest object
    :return:
    """

    if request.method == 'GET':
        app_id = request.GET['id']
        state = request.GET['state']
        person_id = request.GET['person_id']
        person_type = request.GET['person_type']

        # These variables may not exist (depends on view). In order to keep generic, caught in try catch
        try:
            postcode = request.GET['postcode']
        except:
            postcode = None

        try:
            address = request.GET['address']
        except:
            address = None

        try:
            lookup = request.GET['lookup']
        except:
            lookup = None
        try:
            address_id = request.GET['address_id']
        except:
            address_id = None
        try:
            referrer = request.GET['referrer']
        except:
            referrer = None

    if request.method == 'POST':
        app_id = request.POST['id']
        state = request.POST['state']
        person_id = request.POST['person_id']
        person_type = request.POST['person_type']

        # These variables may not exist (depends on view). In order to keep generic, caught in try catch
        try:
            postcode = request.POST['postcode']
        except:
            postcode = None
        try:
            address = request.POST['address']
        except:
            address = None
        try:
            lookup = request.GET['lookup']
        except:
            lookup = None
        try:
            address_id = request.POST['address_id']
        except:
            address_id = None
        try:
            referrer = request.POST['referrer']
        except:
            referrer = None

    # Actual context definition after variable assignment
    context = {
        'application_id': app_id,
        'id': app_id,
        'state': state,
        'person_id': person_id,
        'person_type': person_type,
        'postcode': postcode,
        'address': address,
        'previous_addresses': get_stored_addresses(person_id, person_type),
        'lookup': lookup,
        'address_id': address_id,
        'referrer': referrer
    }

    return context


def get_urls(context):
    """
    A utility method to get any extra urls needed for a page, created here to allow for different contexts
    :param context: The current views context
    :return:
    """
    state = context['state']

    # These two urls need certain 'states' to be built, therefore state is saved then changed, and finally reset
    context['state'] = 'manual'
    context['manual_url'] = build_url('other-people-previous-addresses', get=context)
    context['state'] = 'entry'
    context['entry_url'] = build_url('other-people-previous-addresses', get=context)

    # Reset occurs here
    context['state'] = state

    # List url does not require a new state, so set after state changes, once it has been reset
    context['list_url'] = build_url('other_people_summary', get={'id': context['id']})

    return context
