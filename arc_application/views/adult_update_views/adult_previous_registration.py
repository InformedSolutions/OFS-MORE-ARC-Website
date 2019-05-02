import logging
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required


from ...services.db_gateways import HMGatewayActions
from ...decorators import group_required, user_assigned_application
from ...forms.adult_update_forms.household_member_previous_registration_form import AdultPreviousRegistrationDetailsForm

# Initiate logging
log = logging.getLogger()


#@never_cache
#@login_required
#@group_required(settings.ARC_GROUP)
#@user_assigned_application
def adult_previous_registration_view(request):

    template_name = 'adult_update_templates/adult-add-previous-registration.html'
    success_url = 'new_adults'
    form_class = AdultPreviousRegistrationDetailsForm

    if request.method == 'GET':
        adult_id = request.GET["id"]
        previous_registration_response = HMGatewayActions().read('previous-registration', params={'adult_id': adult_id})

        if previous_registration_response.status_code == 200:
            previous_registration_record = previous_registration_response.record
            initial = {'previous_registration': previous_registration_record['previous_registration'],
                       'individual_id': previous_registration_record['individual_id'],
                       'five_years_in_UK': previous_registration_record['five_years_in_UK']
            }

            form = form_class(initial=initial)
        else:
            initial = {'previous_registration': None,
                       'individual_id': None,
                       'five_years_in_uk': None
                       }
            form = form_class(initial=initial)

        variables = {
            'form': form,
            'adult_id': adult_id,
        }
        log.debug("Render household member previous registration page")
        return render(request, template_name, context=variables)

    if request.method == 'POST':
        adult_id = request.GET.get('id')
        adult_response = HMGatewayActions().read('adult', params={'adult_id': adult_id})
        form = AdultPreviousRegistrationDetailsForm(request.POST)

        if adult_response.status_code == 200:
            if form.is_valid():
                previous_registration = form.cleaned_data.get('previous_registration')
                individual_id = form.cleaned_data.get('individual_id')
                five_years_in_UK = form.cleaned_data.get('five_years_in_UK')

                previous_registration_response = HMGatewayActions().list('previous-registration', params={'adult_id': adult_id})

                if previous_registration_response.status_code == 200:
                    previous_registration_record = {
                        'previous_registration': previous_registration,
                        'individual_id': individual_id,
                        'five_years_in_UK': five_years_in_UK}

                    patch_record = {
                        'adult_id': adult_id,
                    }

                    patch_record.update(previous_registration_record)
                    HMGatewayActions().put('previous-registration', params=patch_record)
                else:
                    previous_registration_record = {
                        'previous_registration': previous_registration,
                        'individual_id': individual_id,
                        'five_years_in_UK': five_years_in_UK,
                        'adult_id': adult_id}

                    HMGatewayActions().create('previous-registration', params=previous_registration_record)

                variables = {
                    'form': form,
                    'person_id': adult_id,
                }
                log.debug("Handling submissions for household members previous registration page")
                return HttpResponseRedirect(reverse(success_url) + '?id=' + adult_id, variables)

            else:
                variables = {
                    'form': form,
                    'person_id': adult_id,
                }
                log.debug("Render household members previous registration page")
                return render(request, template_name, context=variables)
