from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponseRedirect

from ...forms.nanny_forms.nanny_form_builder import PreviousRegistrationForm
from arc_application.services.db_gateways import NannyGatewayActions
from arc_application.models import Application
from .nanny_form_view import FormView


class NannyPreviousRegistrationView(FormView):

        def get(self, request, *args, **kwargs):
            application_id_local = request.GET["id"]
            form = PreviousRegistrationForm()
            variables = {
                'form': form,
                'application_id': application_id_local,
            }

            return render(request, 'nanny_add_previous_registration.html', variables)

        def post(self, request, *args, **kwargs):
            application_id_local = request.POST["id"]
            form = PreviousRegistrationForm(request.POST, id=application_id_local)

            if form.is_valid():
                app = Application.objects.get(pk=application_id_local)
                previous_registration = form.cleaned_data.get('previous_registration')
                individual_id = form.cleaned_data.get('individual_id')
                five_years_in_uk = form.cleaned_data.get('five_years_in_UK')

                if PreviousRegistrationForm.objects.filter(application_id=app).exists():
                    previous_reg_details = PreviousRegistrationForm.objects.get(application_id=app)
                else:
                    previous_reg_details = PreviousRegistrationForm(application_id=app)

                previous_reg_details.previous_registration = previous_registration
                previous_reg_details.individual_id = individual_id
                previous_reg_details.five_years_in_UK = five_years_in_uk
                previous_reg_details.save()

                redirect_link = '/nanny/personal-details/summary'
                return HttpResponseRedirect(settings.URL_PREFIX + redirect_link + '?id=' + application_id_local)

            else:
                variables = {
                    'form': form,
                    'application_id': application_id_local,
                }

                return render(request, 'nanny_add_previous_registration.html', context=variables)