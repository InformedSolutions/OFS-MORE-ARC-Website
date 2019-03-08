from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponseRedirect

from arc_application.forms.nanny_forms.nanny_previous_registration_form import PreviousRegistrationDetailsForm
from arc_application.services.db_gateways import NannyGatewayActions
from .nanny_form_view import FormView


class NannyPreviousRegistrationView(FormView):

        def get(self, request, *args, **kwargs):
            self.application_id = request.GET["id"]
            form = PreviousRegistrationDetailsForm
            variables = {
                'form': form,
                'application_id': self.application_id,
            }

            return render(request, 'nanny_add_previous_registration.html', variables)

        def post(self, request, *args, **kwargs):
            application_id = request.POST["id"]
            form = PreviousRegistrationDetailsForm(request.POST)

            if form.is_valid():
                previous_registration = form.cleaned_data.get('previous_registration')
                individual_id = form.cleaned_data.get('individual_id')
                five_years_in_uk = form.cleaned_data.get('five_years_in_UK')

                api_response = NannyGatewayActions().read('nanny-previous-registration-details',
                                                          params={'application_id': application_id})

                if api_response.status_code == 200:
                    previous_registration_record = api_response.record
                    previous_registration_record['previous_registration'] = self.request.POST['previous_registration']
                    previous_registration_record['individual_id'] = self.request.POST['individual_id']
                    previous_registration_record['five_years_in_UK'] = self.request.POST['five_years_in_UK']

                    NannyGatewayActions().put('nanny-previous-registration-details', params=previous_registration_record)
                else:
                    previous_registration_new = {}
                    previous_registration_new['application_id'] = application_id
                    previous_registration_new['previous_registration'] = self.request.POST['previous_registration']
                    previous_registration_new['individual_id'] = self.request.POST['individual_id']
                    previous_registration_new['five_years_in_UK'] = self.request.POST['five_years_in_UK']

                    response = NannyGatewayActions().create('nanny-previous-registration-details', params=previous_registration_new)

                redirect_link = '/nanny/personal-details/'
                return HttpResponseRedirect(settings.URL_PREFIX + redirect_link + '?id=' + application_id)

            else:
                variables = {
                    'form': form,
                    'application_id': application_id,
                }

                return render(request, 'nanny_add_previous_registration.html', context=variables)

        def get_initial(self):
            initial = super().get_initial()
            api_response = NannyGatewayActions().read('nanny-previous-registration-details', params={'application_id': self.application_id})
            if api_response.status_code == 200:
                previous_response = api_response.record
                initial['previous_registration'] = previous_response['previous_registration']
                initial['individual_id'] = previous_response['individual_id']
                initial['five_years_in_UK'] = previous_response['five_years_in_UK']
            return initial