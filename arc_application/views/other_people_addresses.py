from django.http import HttpResponseRedirect
from django.shortcuts import render

from arc_application import address_helper
from arc_application.forms import OtherPersonPreviousPostcodeEntry, OtherPeoplePreviousAddressLookupForm
from arc_application.models import PreviousAddress
from arc_application.review_util import build_url


def address_state_dispatcher(request):

    states = {'manual': 'manual'}

    context = get_context(request)

    if context['state'] == 'entry':
        states['submission'] = 'selection'
        context['next_states'] = states
        return postcode_entry(request, context)

    if context['state'] == 'selection':
        states['submission'] = 'submission'
        context['next_states'] = states
        return postcode_selection(request, context)

    if context['state'] == 'manual':
        states['submission'] = 'selection'
        context['next_states'] = states
        return postcode_manual(request, context)

    if context['state'] == 'submission':
        states['submission'] = 'entry'
        context['next_states'] = states
        return postcode_submission(request, context)


def postcode_entry(request, context):

    # stored_adresses = get_stored_addresses(person_id, person_type)
    if request.method == 'GET':
        current_form = OtherPersonPreviousPostcodeEntry()
        context['form'] = current_form

        return render(request, 'other-people-previous-address-select.html', context)

    if request.method == 'POST':
        current_form = OtherPersonPreviousPostcodeEntry(request.POST)
        if current_form.is_valid():
            context = get_context(request)
            postcode = current_form.cleaned_data['postcode']
            context['postcode'] = postcode

            # context['form'] = OtherPeoplePreviousAddressLookupForm(choices=addresses)
            context['state'] = 'selection'
            return HttpResponseRedirect(build_url('other-people-previous-addresses', get=context))


def postcode_selection(request, context):
    if request.method == 'GET':
        addresses = address_helper.AddressHelper.create_address_lookup_list(context['postcode'])
        context['form'] = OtherPeoplePreviousAddressLookupForm(choices=addresses)

        return render(request, 'other-people-previous-address-lookup.html', context)

    if request.method == 'POST':
        addresses = address_helper.AddressHelper.create_address_lookup_list(context['postcode'])
        current_form = OtherPeoplePreviousAddressLookupForm(request.POST, choices=addresses)
        if current_form.is_valid():
            context = get_context(request)
            address = current_form.cleaned_data['address']
            context['address'] = address
            context['state'] = 'submission'

            return HttpResponseRedirect(build_url('other-people-previous-addresses', get=context))


def postcode_manual(request, context):
    pass


def postcode_submission(request, context):
    if request.method == 'GET':
        selected_address_index = int(context["address"])
        selected_address = address_helper.AddressHelper.get_posted_address(
            selected_address_index, context["postcode"])
        line1 = selected_address['line1']
        line2 = selected_address['line2']
        town = selected_address['townOrCity']
        postcode = selected_address['postcode']
        previous_address_record = PreviousAddress(person_id=context['person_id'],
                                                   person_type=context['person_type'],
                                                   street_line1=line1,
                                                   street_line2=line2,
                                                   town=town,
                                                   county='',
                                                   country='United Kingdom',
                                                   postcode=postcode)
        previous_address_record.save()
        context['state'] = 'entry'
        return HttpResponseRedirect(build_url('other-people-previous-addresses', get=context))


def get_stored_addresses(person_id, person_type):
    address_queryset = PreviousAddress.objects.filter(person_id=person_id, person_type=person_type)
    return address_queryset

def get_context(request):

    if request.method == 'GET':
        app_id = request.GET['id']
        state = request.GET['state']
        person_id = request.GET['person_id']
        person_type = request.GET['person_type']
        try:
            postcode = request.GET['postcode']
        except:
            postcode = None
        try:
            address = request.GET['address']
        except:
            address = None

    if request.method == 'POST':
        app_id = request.POST['id']
        state = request.POST['state']
        person_id = request.POST['person_id']
        person_type = request.POST['person_type']
        try:
            postcode = request.POST['postcode']
        except:
            postcode = None
        try:
            address = request.GET['address']
        except:
            address = None

    context = {
        'id': app_id,
        'state': state,
        'person_id': person_id,
        'person_type': person_type,
        'postcode': postcode,
        'address': address,
        'previous_addresses': get_stored_addresses(person_id, person_type)
    }

    return context
