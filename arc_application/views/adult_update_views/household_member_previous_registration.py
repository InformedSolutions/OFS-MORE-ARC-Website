import logging
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required


from ...services.db_gateways import HMGatewayActions
from ...decorators import group_required, user_assigned_application
from ...forms.adult_update_forms.household_member_previous_registration_form import HMPreviousRegistrationDetailsForm

# Initiate logging
log = logging.getLogger()


@method_decorator((never_cache, login_required, group_required(settings.ARC_GROUP), user_assigned_application),
                  name='dispatch')
def household_member_previous_registration_view(request):

    if request.method == 'GET':
        application_id = request.GET["id"]
        person_id = request.GET["person_id"]
        form = HMPreviousRegistrationDetailsForm
        variables = {
            'form': form,
            'application_id': application_id,
            'person_id': person_id,
        }
        log.debug("Render household member previous registration page")
        return render(request, 'adult_update_templates/household-members-add-previous-registration.html', context=variables)

    if request.method == 'POST':
        application_id = request.POST["id"]
        person_id = request.POST["person_id"]
        adult_response = HMGatewayActions().read('adult', params={'person_id': person_id})
        form = HMPreviousRegistrationDetailsForm(request.POST, id=person_id)

        if adult_response.status_code == 200:
            if form.is_valid():
                previous_registration = form.cleaned_data.get('previous_registration')
                individual_id = form.cleaned_data.get('individual_id')
                five_years_in_uk = form.cleaned_data.get('five_years_in_UK')

                #if HMPreviousRegistrationDetailsForm.objects.filter(person_id=person_record).exists():
                #    previous_reg_details = HMPreviousRegistrationDetailsForm.objects.get(person_id=person_record)
                #else:
                #    previous_reg_details = HMPreviousRegistrationDetailsForm(person_id=person_record)

                #previous_reg_details.previous_registration = previous_registration
                #previous_reg_details.individual_id = individual_id
                #previous_reg_details.five_years_in_UK = five_years_in_uk
                #previous_reg_details.save()

                redirect_link = 'review/new-adult-summary'
                log.debug("Handling submissions for other people previous registration page")
                return HttpResponseRedirect(settings.URL_PREFIX + redirect_link + '?id=' + application_id)

        else:
            variables = {
                'form': form,
                'application_id': application_id,
                'person_id': person_id,
            }
            log.debug("Render other people previous registration page")
            return render(request, 'adult_update_templates/household-members-add-previous-registration.html', context=variables)
