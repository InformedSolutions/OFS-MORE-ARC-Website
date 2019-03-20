import datetime
from urllib.parse import urlencode

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import View

from .nanny_form_view import FormView
from ...forms.previous_addresses import PreviousAddressEntryForm, PreviousAddressSelectForm, PreviousAddressManualForm
from ...services.db_gateways import NannyGatewayActions


class NannyChangePreviousAddressView(FormView):

    form_class = PreviousAddressManualForm
    template_name = 'nanny_change_previous_address.html'

    def post(self, request, *args, **kwargs):

        if request.POST.get('delete', None):
            return self._do_delete()

        return super().post(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()

        rec = self._read_address()
        if rec is not None:
            initial['street_line1'] = rec['street_line1']
            initial['street_line2'] = rec['street_line2']
            initial['town'] = rec['town']
            initial['county'] = rec['county']
            initial['postcode'] = rec['postcode']
            initial['moved_in_date'] = datetime.datetime.strptime(rec['moved_in_date'], '%Y-%m-%d').date()
            initial['moved_out_date'] = datetime.datetime.strptime(rec['moved_out_date'], '%Y-%m-%d').date()

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
        self._write_address(form.cleaned_data)
        return super().form_valid(form)

    def get_success_url(self):
        application_id = self.request.GET['id']
        return reverse('nanny_personal_details_summary') + '?' + urlencode({'id': application_id})

    def _do_delete(self):
        address_id = self.request.GET['previous_address_id']
        NannyGatewayActions().delete('previous-address', params={'previous_address_id': address_id})
        return HttpResponseRedirect(self.get_success_url())

    def _read_address(self):
        addr_id = self.request.GET['previous_address_id']
        api_response = NannyGatewayActions().read('previous-address', params={'previous_address_id': addr_id})
        if api_response.status_code != 200 or not hasattr(api_response, 'record'):
            return None
        return api_response.record

    def _write_address(self, data):
        rec = self._read_address()
        if rec is None:
            return
        rec['street_line1'] = data['street_line1']
        rec['street_line2'] = data['street_line2']
        rec['town'] = data['town']
        rec['county'] = data['county']
        rec['postcode'] = data['postcode']
        rec['moved_in_date'] = data['moved_in_date'].strftime('%Y-%m-%d')
        rec['moved_out_date'] = data['moved_out_date'].strftime('%Y-%m-%d')
        NannyGatewayActions().put('previous-address', rec)


class NannyPreviousAddressesView(FormView):
    # form_class = PreviousRegistrationDetailsForm
    # template_name = 'nanny_add_previous_registration.html'
    #
    # def get_initial(self):
    #     initial = super().get_initial()
    #     application_id = self.request.GET["id"]
    #
    #     api_response = NannyGatewayActions().read('previous-registration-details',
    #                                               params={'application_id': application_id})
    #     if api_response.status_code == 200:
    #         previous_response = api_response.record
    #         initial['previous_registration'] = previous_response['previous_registration']
    #         initial['individual_id'] = previous_response['individual_id']
    #         initial['five_years_in_UK'] = previous_response['five_years_in_UK']
    #     return initial
    #
    # def get_context_data(self, **kwargs):
    #     application_id = self.request.GET["id"]
    #     context = {
    #         'application_id': application_id,
    #     }
    #
    #     return super(NannyPreviousRegistrationView, self).get_context_data(**context)
    #
    # def post(self, request, *args, **kwargs):
    #     application_id = request.POST["id"]
    #     form = PreviousRegistrationDetailsForm(request.POST)
    #
    #     if form.is_valid():
    #         previous_registration = form.cleaned_data.get('previous_registration')
    #         individual_id = form.cleaned_data.get('individual_id')
    #         five_years_in_uk = form.cleaned_data.get('five_years_in_UK')
    #
    #         api_response = NannyGatewayActions().read('previous-registration-details',
    #                                                   params={'application_id': application_id})
    #
    #         if api_response.status_code == 200:
    #             previous_registration_record = api_response.record
    #             previous_registration_record['previous_registration'] = self.request.POST['previous_registration']
    #             previous_registration_record['individual_id'] = self.request.POST['individual_id']
    #             previous_registration_record['five_years_in_UK'] = self.request.POST['five_years_in_UK']
    #
    #             NannyGatewayActions().put('previous-registration-details', params=previous_registration_record)
    #         else:
    #             previous_registration_new = {}
    #             previous_registration_new['application_id'] = application_id
    #             previous_registration_new['previous_registration'] = self.request.POST['previous_registration']
    #             previous_registration_new['individual_id'] = self.request.POST['individual_id']
    #             previous_registration_new['five_years_in_UK'] = self.request.POST['five_years_in_UK']
    #
    #             NannyGatewayActions().create('previous-registration-details',
    #                                                     params=previous_registration_new)
    #
    #         redirect_link = '/nanny/personal-details/review/'
    #         return HttpResponseRedirect(settings.URL_PREFIX + redirect_link + '?id=' + application_id)
    #
    #     else:
    #         variables = {
    #             'form': form,
    #             'application_id': application_id,
    #         }
    #
    #         return render(request, 'nanny_add_previous_registration.html', context=variables)

    pass