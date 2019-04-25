import datetime

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.forms import formset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render
import logging
#from ...childminder_task_util import get_show_references
from ...decorators import group_required, user_assigned_application
from ...forms.adult_update_forms.adult_update_form import NewAdultForm
from .review import new_adults_initial_population, request_to_comment, save_comments
from ...services.db_gateways import HMGatewayActions

# Initiate logging
log = logging.getLogger('')

@login_required
@group_required(settings.ARC_GROUP)
@user_assigned_application
def new_adults_summary(request):
    """
    Method returning the template for the People in your home: summary page (for a given application)
    displaying entered data for this task and navigating to the task list when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered People in your home: summary template
    """

    # Defines the formset using formset factory
    AdultFormSet = formset_factory(NewAdultForm, extra=0)

    application_id_local = request.GET.get('id') or request.POST.get('id')
    application = HMGatewayActions().read('application', {'token_id': application_id_local})

    # Adult data
    adults = HMGatewayActions().list('adult', {'token_id': application_id_local}).record
    adult_record_list = []
    adult_id_list = []
    adult_health_check_status_list = []
    adult_name_list = []
    adult_birth_day_list = []
    adult_birth_month_list = []
    adult_birth_year_list = []
    adult_relationship_list = []
    adult_email_list = []
    adult_dbs_cert_numbers = []
    adult_dbs_on_capitas = []
    adult_dbs_is_recents = []
    adult_dbs_is_enhanceds = []
    adult_dbs_on_updates = []
    current_illnesses = []
    serious_illnesses = []
    hospital_admissions = []
    local_authorities = []
    adult_lived_abroad = []
    adult_military_base = []
    adult_name_querysets = []
    adult_address_querysets = []
    previous_registration_querysets = []
    adult_previous_name_lists_list = []
    adult_previous_address_lists_list = []

    for adult in adults:

        if adult['middle_names'] is not None and adult['middle_names'] != '':
            name = adult['first_name'] + ' ' + adult['middle_names'] + ' ' + adult['last_name']
        else:
            name = adult['first_name'] + ' ' + adult['last_name']

        adult_id = adult['adult_id']

        adult_record_list.append(adult)
        adult_id_list.append(adult['adult_id'])
        adult_health_check_status_list.append(adult['health_check_status'])
        adult_name_list.append(name)
        adult_birth_day_list.append(adult['birth_day'])
        adult_birth_month_list.append(adult['birth_month'])
        adult_birth_year_list.append(adult['birth_year'])
        adult_relationship_list.append(adult['relationship'])
        adult_email_list.append(adult['email'])
        adult_dbs_is_enhanceds.append(adult['enhanced_check'])
        adult_dbs_cert_numbers.append(adult['dbs_certificate_number'] if adult['enhanced_check'] else None)
        adult_dbs_on_capitas.append(adult['is_ofsted_dbs'] if adult['enhanced_check'] else None)
        adult_dbs_is_recents.append(adult['within_three_months'] if adult['enhanced_check'] else None)
        adult_dbs_on_updates.append(adult['on_update'] if not adult['within_three_months'] else None)
        adult_lived_abroad.append(adult['lived_abroad'])
        adult_military_base.append(adult['military_base'])
        #health check fields
        #if adult['currently_being_treated']:
           # current_illnesses.append(adult)
        # serious_illnesses_response = HMGatewayActions().list('adult_serious_illness',{'adult_id':adult_id})
        # if serious_illnesses_response.status_code == 200:
        #     serious_illnesses.append(serious_illnesses_response.record)
        # hospital_admissions_response = HMGatewayActions().list('adult_hospital_admission', {'adult_id': adult_id})
        # if hospital_admissions_response.status_code == 200:
        #    hospital_admissions.append(hospital_admissions_response.record)
        local_authorities.append(adult['reasons_known_to_council_health_check'])

        #previous_registration_querysets.append(
         #   OtherPersonPreviousRegistrationDetails.objects.filter(person_id_id=adult.pk))
        #adult_previous_name_lists_list.append(
         #   PreviousName.objects.filter(person_id=adult.pk, other_person_type='ADULT').order_by('order'))
        #adult_previous_address_lists_list.append(
         #   PreviousAddress.objects.filter(person_id=adult.pk, person_type='ADULT'))

    #previous_registration_lists = list(zip(adult_id_list, adult_name_list, previous_registration_querysets))

    if request.method == 'GET':
        # Defines the static form at the top of the page

        initial_adult_data = new_adults_initial_population(adults)

        # Instantiates the formset with the management data defined above, forcing a set amount of forms
        formset_adult = AdultFormSet(initial=initial_adult_data, prefix='adult')

        # Zips the formset into the list of adults
        # Converts it to a list, there was trouble parsing the form objects when it was in a zip object
        adult_lists = list(zip(adult_record_list, adult_id_list, adult_health_check_status_list, adult_name_list, adult_birth_day_list,\
                      adult_birth_month_list, adult_birth_year_list, adult_relationship_list, adult_email_list,\
                      adult_dbs_cert_numbers, adult_dbs_on_capitas, adult_dbs_is_recents, adult_dbs_is_enhanceds,\
                      adult_dbs_on_updates, adult_lived_abroad, adult_military_base, formset_adult, local_authorities))
                #current_illnesses, serious_illnesses, hospital_admissions, adult_previous_name_lists_list, adult_previous_address_lists_list))


        variables = {
            'formset_adult': formset_adult,
            'application_id': application_id_local,
            'adult_lists': adult_lists
        }
        log.debug("Rendering new adults in the home page")
        return render(request, 'adult_update_templates/new-adults-summary.html', variables)

    elif request.method == 'POST':

        adult_formset = AdultFormSet(request.POST, prefix='adult')
        #
        if adult_formset.is_valid():
            adult_data_list = adult_formset.cleaned_data

            section_status = 'COMPLETED'
        #
        #     # ======================================================================================================== #
        #     # To explain the below:
        #     # - Each section has at least one associated formset.
        #     # - Each formset has a list of data from the POST request.
        #     # - Each element in these lists of data is a dictionary and is associated with a single model.
        #     # - The code saves the comments stored in these dictionaries in an ARC_COMMENT using the pk from the model
        #     #   with which it corresponds.
        #     # - The correspondence is that data for a person stored at adult_data_list[1]
        #     #   maps to the model stored at adults[1]
        #     #  ======================================================================================================= #
        #
            review_sections_to_process = {
                    'adults_in_home': {
                    'POST_data': adult_data_list,
                    'models': adults
                 }
            }

            for section in review_sections_to_process.values():
                for adult_post_data, adult in zip(section['POST_data'], section['models']):
                    adult_comments = request_to_comment(adult_id, '', adult_post_data)
                    save_comments(request, person_comments)

                    adult['cygnum_relationship_to_childminder'] = adult_post_data['cygnum_relationship']
                    HMGatewayActions().put('adult', params=adult)

                    #do we get a field to say if anything flagged?
                  # if adult_comments:
                   #    application = HMGatewayActions

            successful = save_comments(request, static_form_comments)
            log.debug("Handling submissions for new adults in the home page - save successful")
            if not successful:
                log.debug("Handling submissions for people in the home page - save unsuccessful")
                return render(request, '500.html')

            # # calculate start and end dates for each adult's current name
            # for adult in AdultInHome.objects.filter(application_id=application_id_local):
            #     # find most recent previous name
            #     try:
            #         # fetch previous name with most recent end date (must actually have an end date)
            #         prev_name = PreviousName.objects.filter(person_id=adult.pk, other_person_type='ADULT',
            #                                                 end_day__isnull=False, end_month__isnull=False,
            #                                                 end_year__isnull=False)\
            #                         .order_by('-end_year', '-end_month', '-end_day')[0]
            #     except IndexError:
            #         prev_name = None
            #
            #     today = datetime.date.today()
            #     adult.name_start_day = prev_name.end_day if prev_name else adult.birth_day
            #     adult.name_start_month = prev_name.end_month if prev_name else adult.birth_month
            #     adult.name_start_year = prev_name.end_year if prev_name else adult.birth_year
            #     adult.name_end_day = today.day
            #     adult.name_end_month = today.month
            #     adult.name_end_year = today.year
            #     adult.save()
            #
            # status = Arc.objects.get(pk=application_id_local)
            # status.people_in_home_review = section_status
            # status.save()
            #
            # show_references = get_show_references(application_id_local)
            #
            # default = '/references/summary/' if show_references else '/review/'
            # log.debug("Redirect to references or review")
            # redirect_link = redirect_selection(request, default)
            # log.debug("Handling submissions for people in the home page")
            # return HttpResponseRedirect(settings.URL_PREFIX + redirect_link + '?id=' + application_id_local)

        # else:
        #
        #     # Zips the formset into the list of adults
        #     # Converts it to a list, there was trouble parsing the form objects when it was in a zip object
        #     adult_lists = list(zip(adult_record_list, adult_id_list, adult_health_check_status_list, adult_name_list,
        #                            adult_birth_day_list, adult_birth_month_list, adult_birth_year_list,
        #                            adult_relationship_list, adult_email_list, adult_dbs_cert_numbers,
        #                            adult_dbs_on_capitas, adult_dbs_is_recents, adult_dbs_is_enhanceds,
        #                            adult_dbs_on_updates, adult_lived_abroad, adult_military_base, adult_formset,
        #                            current_illnesses, serious_illnesses, hospital_admissions, local_authorities,
        #                            adult_enhanced_checks, adult_previous_name_lists_list,
        #                            adult_previous_address_lists_list))
        #
        #     for adult_form, adult_name in zip(adult_formset, adult_name_list):
        #         adult_form.error_summary_title = 'There was a problem (' + adult_name + ')'
        #
        #     variables = {
        #         'formset_adult': adult_formset,
        #         'application_id': application_id_local,
        #         'adults_in_home': application.adults_in_home,
        #         'children_in_home': application.children_in_home,
        #         'known_to_social_services_pith': application.known_to_social_services_pith,
        #         'adult_lists': adult_lists}
        #         #'previous_registration_lists': previous_registration_lists,
        #
        #     log.debug("Render people in the home page")
        #     return render(request, 'adult_update_templates/new-adults-summary.html', variables)


