import logging
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required

from ...forms.nanny_forms.nanny_previous_registration_form import PreviousRegistrationDetailsForm
from ...services.db_gateways import NannyGatewayActions
from .nanny_form_view import FormView
from ...decorators import group_required, user_assigned_application

# Initiate logging
log = logging.getLogger()

@method_decorator((never_cache, login_required, group_required(settings.ARC_GROUP), user_assigned_application),
                  name='dispatch')
class NannyPreviousRegistrationView(FormView):

    form_class = PreviousRegistrationDetailsForm
    template_name = 'nanny_add_previous_registration.html'

    def get_initial(self):
        initial = super().get_initial()
        application_id = self.request.GET["id"]

        api_response = NannyGatewayActions().read('previous-registration-details',
                                                  params={'application_id': application_id})
        if api_response.status_code == 200:
            previous_response = api_response.record
            initial['previous_registration'] = previous_response['previous_registration']
            initial['individual_id'] = previous_response['individual_id']
            initial['five_years_in_UK'] = previous_response['five_years_in_UK']
        return initial

    def get_context_data(self, **kwargs):
        application_id = self.request.GET["id"]
        context = {
            'application_id': application_id,
        }

        return super(NannyPreviousRegistrationView, self).get_context_data(**context)

    def post(self, request, *args, **kwargs):
        application_id = request.POST["id"]
        form = PreviousRegistrationDetailsForm(request.POST)

        if form.is_valid():
            previous_registration = form.cleaned_data.get('previous_registration')
            individual_id = form.cleaned_data.get('individual_id')
            five_years_in_uk = form.cleaned_data.get('five_years_in_UK')

            api_response = NannyGatewayActions().read('previous-registration-details',
                                                      params={'application_id': application_id})

            if api_response.status_code == 200:
                previous_registration_record = api_response.record
                previous_registration_record['previous_registration'] = self.request.POST['previous_registration']
                previous_registration_record['individual_id'] = self.request.POST['individual_id']
                previous_registration_record['five_years_in_UK'] = self.request.POST['five_years_in_UK']

                NannyGatewayActions().put('previous-registration-details', params=previous_registration_record)
                log.debug("Handling submissions for nanny previous registration page - updating details")
            else:
                previous_registration_new = {}
                previous_registration_new['application_id'] = application_id
                previous_registration_new['previous_registration'] = self.request.POST['previous_registration']
                previous_registration_new['individual_id'] = self.request.POST['individual_id']
                previous_registration_new['five_years_in_UK'] = self.request.POST['five_years_in_UK']

                NannyGatewayActions().create('previous-registration-details',
                                                        params=previous_registration_new)
                log.debug("Handling submissions for nanny previous registration page - new details")

            redirect_link = '/nanny/personal-details/review/'
            return HttpResponseRedirect(settings.URL_PREFIX + redirect_link + '?id=' + application_id)

        else:
            variables = {
                'form': form,
                'application_id': application_id,
            }
            log.debug("Rendering nanny previous registration page")
            return render(request, 'nanny_add_previous_registration.html', context=variables)
