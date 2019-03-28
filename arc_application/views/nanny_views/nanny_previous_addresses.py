import datetime
import logging
from urllib.parse import urlencode

from django.http import HttpResponseRedirect
from django.urls import reverse

from .nanny_form_view import FormView
from ...forms.previous_addresses import PreviousAddressEntryForm, PreviousAddressSelectForm, PreviousAddressManualForm
from ...services.db_gateways import NannyGatewayActions
from ...address_helper import AddressHelper

# Initiate logging
log = logging.getLogger()

# noinspection PyMethodMayBeStatic
class _NannyPreviousAddressViewMixin:

    # noinspection SpellCheckingInspection
    def _addr_record_to_context_data(self, rec):
        return {
            'previous_address_id': rec['previous_address_id'],
            'street_line1': rec['street_line1'],
            'street_line2': rec['street_line2'],
            'town': rec['town'],
            'county': rec['county'],
            'postcode': rec['postcode'],
            'moved_in_date': datetime.datetime.strptime(rec['moved_in_date'], '%Y-%m-%d').date(),
            'moved_out_date': datetime.datetime.strptime(rec['moved_out_date'], '%Y-%m-%d').date(),
        }

    # noinspection SpellCheckingInspection
    def _post_data_to_addr_record(self, data, rec=None, person_id=None, person_type=None, order=None):
        if rec is None:
            rec = {}
        rec['street_line1'] = data['street_line1']
        rec['street_line2'] = data['street_line2']
        rec['town'] = data['town']
        rec['county'] = data['county']
        rec['postcode'] = data['postcode']
        rec['moved_in_date'] = data['moved_in_date'].strftime('%Y-%m-%d')
        rec['moved_out_date'] = data['moved_out_date'].strftime('%Y-%m-%d')
        if person_id is not None:
            rec['person_id'] = person_id
        if person_type is not None:
            rec['person_type'] = person_type
        if order is not None:
            rec['order'] = order
        return rec

    def _fetch_address_list(self, person_id, person_type):
        api_response = NannyGatewayActions().list('previous-address',
                                                  params={'person_id': person_id, 'person_type': person_type})
        if api_response.status_code == 200 and hasattr(api_response, 'record'):
            return [self._addr_record_to_context_data(r) for r in api_response.record]
        elif api_response.status_code == 404:
            return []
        else:
            return None

    def _fetch_single_address(self, previous_address_id):
        api_response = NannyGatewayActions().read('previous-address',
                                                  params={'previous_address_id': previous_address_id})
        if api_response.status_code == 200 and hasattr(api_response, 'record'):
            return self._addr_record_to_context_data(api_response.record)
        else:
            return None

    def _update_address(self, previous_address_id, data):
        actions = NannyGatewayActions()
        api_response = actions.read('previous-address', params={'previous_address_id': previous_address_id})
        rec = None
        if api_response.status_code == 200 and hasattr(api_response, 'record'):
            rec = api_response.record
        rec = self._post_data_to_addr_record(data, rec)
        actions.put('previous-address', rec)

    def _add_address(self, person_id, person_type, data):
        actions = NannyGatewayActions()

        # find out what next order value should be
        api_response = actions.list('previous-address', params={'person_id': person_id, 'person_type': person_type})
        if api_response.status_code == 200 and hasattr(api_response, 'record'):
            order = api_response.record[-1]['order'] + 1
        else:
            order = 0

        rec = self._post_data_to_addr_record(data, person_id=person_id, person_type=person_type, order=order)
        actions.create('previous-address', rec)

    def _remove_address(self, previous_address_id):
        NannyGatewayActions().delete('previous-address', {'previous_address_id': previous_address_id})


class NannyChangePreviousAddressView(FormView, _NannyPreviousAddressViewMixin):

    form_class = PreviousAddressManualForm
    template_name = 'nanny_change_previous_address.html'

    def post(self, request, *args, **kwargs):

        if request.POST.get('delete', None):
            return self._do_delete()
        log.debug("Handling submissions for nanny previous address - address view - delete address")
        return super().post(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        address_id = self.request.GET['previous_address_id']
        initial.update(self._fetch_single_address(address_id))
        return initial

    def get_context_data(self, **kwargs):
        application_id = self.request.GET['id']
        previous_address_id = self.request.GET['previous_address_id']
        context = {
            'application_id': application_id,
            'previous_address_id': previous_address_id,
        }
        return super().get_context_data(**context)

    def form_valid(self, form):
        address_id = self.request.GET['previous_address_id']
        self._update_address(address_id, form.cleaned_data)
        return super().form_valid(form)

    def get_success_url(self):
        application_id = self.request.GET['id']
        return reverse('nanny_personal_details_summary') + '?' + urlencode({'id': application_id})

    def _do_delete(self):
        address_id = self.request.GET['previous_address_id']
        self._remove_address(address_id)
        return HttpResponseRedirect(self.get_success_url())


class NannyAddPreviousAddressSearchView(FormView, _NannyPreviousAddressViewMixin):

    form_class = PreviousAddressEntryForm
    template_name = 'nanny_add_previous_address_search.html'

    def post(self, request, *args, **kwargs):

        delete = ([k for k in request.POST.keys() if k.startswith('delete-')]+[None])[0]
        if delete:
            delete_id = delete[len('delete-'):]
            self._remove_address(delete_id)
            log.debug("Handling submissions for nanny previous address - search view - delete address")
            return HttpResponseRedirect(reverse('nanny_add_previous_address_search') + '?' + self._redirect_params())

        elif request.POST.get('manual', None):
            log.debug("Handling submissions for nanny previous address - search view - manual entry")
            return HttpResponseRedirect(reverse('nanny_add_previous_address_manual') + '?' + self._redirect_params())

        return super().post(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        postcode = self.request.GET.get('postcode', None)
        if postcode:
            initial['postcode'] = postcode
        return initial

    def get_context_data(self, **kwargs):
        application_id = self.request.GET['id']
        person_id = self.request.GET['person_id']
        person_type = self.request.GET['type']

        context = {
            'application_id': application_id,
            'person_id': person_id,
            'person_type': person_type,
            'previous_addresses': self._fetch_address_list(person_id, person_type),
        }
        return super().get_context_data(**context)

    def get_success_url(self):
        return reverse('nanny_add_previous_address_select') + '?' + self._redirect_params()

    def _redirect_params(self):
        application_id = self.request.GET['id']
        person_id = self.request.GET['person_id']
        person_type = self.request.GET['type']
        postcode = self.request.POST['postcode']
        return urlencode({'id': application_id, 'person_id': person_id, 'type': person_type, 'postcode': postcode})


class NannyAddPreviousAddressSelectView(FormView, _NannyPreviousAddressViewMixin):

    form_class = PreviousAddressSelectForm
    template_name = 'nanny_add_previous_address_select.html'

    def post(self, request, *args, **kwargs):

        delete = ([k for k in request.POST.keys() if k.startswith('delete-')]+[None])[0]
        if delete:
            delete_id = delete[len('delete-'):]
            self._remove_address(delete_id)
            log.debug("Handling submissions for nanny previous address - select view - delete address")
            return HttpResponseRedirect(reverse('nanny_add_previous_address_select') + '?'
                                        + self._preserve_form_redirect_params())

        elif request.POST.get('manual', None):
            log.debug("Handling submissions for nanny previous address - select view - manual entry")
            return HttpResponseRedirect(reverse('nanny_add_previous_address_manual') + '?'
                                        + self._preserve_form_redirect_params())

        return super().post(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        postcode = self.request.GET['postcode']
        kwargs['choices'] = AddressHelper.create_address_lookup_list(postcode)
        return kwargs

    def get_context_data(self, **kwargs):
        application_id = self.request.GET['id']
        person_id = self.request.GET['person_id']
        person_type = self.request.GET['type']
        postcode = self.request.GET['postcode']

        context = {
            'application_id': application_id,
            'person_id': person_id,
            'person_type': person_type,
            'postcode': postcode,
            'previous_addresses': self._fetch_address_list(person_id, person_type),
        }
        return super().get_context_data(**context)

    def form_valid(self, form):

        person_id = self.request.GET['person_id']
        person_type = self.request.GET['type']
        postcode = self.request.GET['postcode']

        addr_index = int(form.cleaned_data['address'])
        address = AddressHelper.get_posted_address(addr_index, postcode)

        data = dict(form.cleaned_data)
        data['street_line1'] = address.get('line1', '')
        data['street_line2'] = address.get('line2', '')
        data['town'] = address.get('townOrCity', '')
        data['county'] = address.get('county', '')
        data['postcode'] = address.get('postcode', '')

        self._add_address(person_id, person_type, data)

        return super().form_valid(form)

    def get_success_url(self):

        application_id = self.request.GET['id']
        person_id = self.request.GET['person_id']
        person_type = self.request.GET['type']

        if self.request.POST.get('another', None):
            return reverse('nanny_add_previous_address_search') + '?' + urlencode(
                {'id': application_id, 'person_id': person_id, 'type': person_type})
        else:
            return reverse('nanny_personal_details_summary') + '?' + urlencode(
                {'id': application_id})

    def _preserve_form_redirect_params(self):

        application_id = self.request.GET['id']
        person_id = self.request.GET['person_id']
        person_type = self.request.GET['type']
        postcode = self.request.GET['postcode']
        params = {'id': application_id, 'person_id': person_id, 'type': person_type, 'postcode': postcode}

        for p in ('moved_in_date_0', 'moved_in_date_1', 'moved_in_date_2',
                  'moved_out_date_0', 'moved_out_date_1', 'moved_out_date_2'):
            params[p] = self.request.POST[p]

        return urlencode(params)


class NannyAddPreviousAddressManualView(FormView, _NannyPreviousAddressViewMixin):

    form_class = PreviousAddressManualForm
    template_name = 'nanny_add_previous_address_manual.html'

    def post(self, request, *args, **kwargs):

        delete = ([k for k in request.POST.keys() if k.startswith('delete-')]+[None])[0]
        if delete:
            delete_id = delete[len('delete-'):]
            self._remove_address(delete_id)
            log.debug("Handling submissions for nanny previous address manual view - delete address")
            return HttpResponseRedirect(reverse('nanny_add_previous_address_manual') + '?'
                                        + self._preserve_form_redirect_params())

        elif request.POST.get('search', None):
            log.debug("Handling submissions for nanny previous address manual view - search address")
            return HttpResponseRedirect(reverse('nanny_add_previous_address_search') + '?'
                                        + self._preserve_form_redirect_params())

        return super().post(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()

        for p in ('street_line1', 'street_line2', 'town', 'county', 'postcode'):
            val = self.request.GET.get(p, None)
            if val:
                initial[p] = val

        move_in_day = self._int_or_none(self.request.GET.get('moved_in_date_0', None))
        move_in_month = self._int_or_none(self.request.GET.get('moved_in_date_1', None))
        move_in_year = self._int_or_none(self.request.GET.get('moved_in_date_2', None))
        if all((move_in_day, move_in_month, move_in_year)):
            initial['moved_in_date'] = datetime.date(move_in_year, move_in_month, move_in_day)

        move_out_day = self._int_or_none(self.request.GET.get('moved_out_date_0', None))
        move_out_month = self._int_or_none(self.request.GET.get('moved_out_date_1', None))
        move_out_year = self._int_or_none(self.request.GET.get('moved_out_date_2', None))
        if all((move_out_day, move_out_month, move_out_year)):
            initial['moved_out_date'] = datetime.date(move_out_year, move_out_month, move_out_day)

        return initial

    def get_context_data(self, **kwargs):
        application_id = self.request.GET['id']
        person_id = self.request.GET['person_id']
        person_type = self.request.GET['type']
        postcode = self.request.GET.get('postcode', None)
        context = {
            'application_id': application_id,
            'person_id': person_id,
            'person_type': person_type,
            'postcode': postcode,
            'previous_addresses': self._fetch_address_list(person_id, person_type),
        }
        return super().get_context_data(**context)

    def form_valid(self, form):

        person_id = self.request.GET['person_id']
        person_type = self.request.GET['type']

        self._add_address(person_id, person_type, form.cleaned_data)

        return super().form_valid(form)

    def get_success_url(self):

        application_id = self.request.GET['id']
        person_id = self.request.GET['person_id']
        person_type = self.request.GET['type']

        if self.request.POST.get('another', None):
            return reverse('nanny_add_previous_address_manual') + '?' + urlencode(
                {'id': application_id, 'person_id': person_id, 'type': person_type})
        else:
            return reverse('nanny_personal_details_summary') + '?' + urlencode(
                {'id': application_id})

    # noinspection PyMethodMayBeStatic
    def _int_or_none(self, val):
        try:
            return int(val)
        except (ValueError, TypeError):
            return None

    def _preserve_form_redirect_params(self):

        application_id = self.request.GET['id']
        person_id = self.request.GET['person_id']
        person_type = self.request.GET['type']
        params = {'id': application_id, 'person_id': person_id, 'type': person_type}

        for p in ('street_line1', 'street_line2', 'town', 'county', 'postcode',
                  'moved_in_date_0', 'moved_in_date_1', 'moved_in_date_2',
                  'moved_out_date_0', 'moved_out_date_1', 'moved_out_date_2'):
            params[p] = self.request.POST[p]

        return urlencode(params)
