import datetime

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.forms import formset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render
import logging
from ...childminder_task_util import get_show_references
from ...decorators import group_required, user_assigned_application
from ...forms.childminder_forms.form import AdultInYourHomeForm, ChildInYourHomeForm, OtherPeopleInYourHomeForm, \
    ChildForm, ChildAddressForm
from ...models import ChildInHome, AdultInHome, Arc, Application, PreviousAddress, ChildAddress, \
    OtherPersonPreviousRegistrationDetails, HealthCheckCurrent, HealthCheckSerious, HealthCheckHospital, \
    ChildcareType, Child, ApplicantHomeAddress
from ...models.previous_name import PreviousName
from ...review_util import request_to_comment, save_comments, redirect_selection
from .review import other_people_initial_population, children_initial_population, children_address_initial_population

# Initiate logging
log = logging.getLogger('')

@login_required
@group_required(settings.ARC_GROUP)
@user_assigned_application
def other_people_summary(request):
    """
    Method returning the template for the People in your home: summary page (for a given application)
    displaying entered data for this task and navigating to the task list when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered People in your home: summary template
    """

    # Defines the formset using formset factory
    AdultFormSet = formset_factory(AdultInYourHomeForm, extra=0)
    ChildInHomeFormSet = formset_factory(ChildInYourHomeForm, extra=0)
    ChildNotInHomeFormSet = formset_factory(ChildForm, extra=0)
    ChildNotInHomeAddressFormSet = formset_factory(ChildAddressForm, extra=0)

    application_id_local = request.GET.get('id') or request.POST.get('id')
    application = Application.objects.get(pk=application_id_local)

    form = OtherPeopleInYourHomeForm(table_keys=[application_id_local], prefix='static')

    # Adult data
    adults = AdultInHome.objects.filter(application_id=application_id_local).order_by('adult')
    adult_record_list = []
    adult_id_list = []
    adult_health_check_status_list = []
    adult_title_list = []
    adult_name_list = []
    adult_birth_day_list = []
    adult_birth_month_list = []
    adult_birth_year_list = []
    adult_relationship_list = []
    adult_email_list = []
    adult_mobile_number_list = []
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
    adult_previous_registrations = []
    adult_enhanced_checks = []
    adult_previous_name_lists_list = []
    adult_previous_address_lists_list = []

    # Children in the home data
    children = ChildInHome.objects.filter(application_id=application_id_local).order_by('child')
    child_id_list = []
    child_name_list = []
    child_birth_day_list = []
    child_birth_month_list = []
    child_birth_year_list = []
    child_relationship_list = []

    # Only show 'Own children not in the home' if applicant is providing care in their own home.
    # Both applicant home address and applicant childcare address are stored in the APPLICANT_HOME_ADDRESS table.
    # If the current_address is also the childcare_address, we know they are providing care in their own home.

    home_address = ApplicantHomeAddress.objects.get(application_id=application_id_local, current_address=True)
    providing_care_in_own_home = home_address.childcare_address

    # Own children not in the home
    own_children = Child.objects.filter(application_id=application_id_local, lives_with_childminder=False).order_by(
        'child')
    own_child_name_list = []
    own_child_address_list = [
        ChildAddress.objects.get(application_id=application_id_local, child=child.child) for child in own_children
    ]

    # Set up bool to track whether linking has been completed for all adults in this application
    linking_complete = True

    for adult in adults:

        if adult.middle_names and adult.middle_names != '':
            name = adult.first_name + ' ' + adult.middle_names + ' ' + adult.last_name
        else:
            name = adult.first_name + ' ' + adult.last_name

        adult_record_list.append(adult)
        adult_id_list.append(adult.adult_id)
        adult_health_check_status_list.append(adult.health_check_status)
        adult_title_list.append(adult.title)
        adult_name_list.append(name)
        adult_birth_day_list.append(adult.birth_day)
        adult_birth_month_list.append(adult.birth_month)
        adult_birth_year_list.append(adult.birth_year)
        adult_relationship_list.append(adult.relationship)
        adult_email_list.append(adult.email)
        adult_mobile_number_list.append(adult.PITH_mobile_number)
        adult_dbs_cert_numbers.append(adult.dbs_certificate_number)
        adult_dbs_on_capitas.append(adult.capita)
        adult_dbs_is_recents.append(adult.within_three_months)
        adult_dbs_is_enhanceds.append(adult.enhanced_check if adult.show_enhanced_check() else None)
        adult_dbs_on_updates.append(adult.on_update if adult.show_on_update() else None)
        adult_lived_abroad.append(adult.lived_abroad)
        adult_military_base.append(adult.military_base)
        current_illnesses.append(HealthCheckCurrent.objects.filter(person_id=adult.pk))
        serious_illnesses.append(HealthCheckSerious.objects.filter(person_id=adult.pk))
        hospital_admissions.append(HealthCheckHospital.objects.filter(person_id=adult.pk))
        local_authorities.append(adult.reasons_known_to_council_health_check)
        adult_enhanced_checks.append(adult.enhanced_check)
        adult_previous_name_lists_list.append(
            PreviousName.objects.filter(person_id=adult.pk, other_person_type='ADULT').order_by('order'))
        adult_previous_address_lists_list.append(
            PreviousAddress.objects.filter(person_id=adult.pk, person_type='ADULT'))
        if OtherPersonPreviousRegistrationDetails.objects.filter(person_id=adult.pk).exists():
            adult_prev_reg = OtherPersonPreviousRegistrationDetails.objects.get(person_id=adult.pk)
        else:
            linking_complete = False
            adult_prev_reg = {'individual_id': None}
        adult_previous_registrations.append({'adult_id': adult.adult_id, 'prev_reg': adult_prev_reg})


    for child in children:
        if child.middle_names and child.middle_names != '':
            name = child.first_name + ' ' + child.middle_names + ' ' + child.last_name
        else:
            name = child.first_name + ' ' + child.last_name
        child_id_list.append(child.child_id)
        child_name_list.append(name)
        child_birth_day_list.append(child.birth_day)
        child_birth_month_list.append(child.birth_month)
        child_birth_year_list.append(child.birth_year)
        child_relationship_list.append(child.relationship)

    for child in own_children:
        if child.middle_names and child.middle_names != '':
            name = child.first_name + ' ' + child.middle_names + ' ' + child.last_name
        else:
            name = child.first_name + ' ' + child.last_name
        own_child_name_list.append(name)



    form.error_summary_title = 'There was a problem'

    if request.method == 'GET':
        # Defines the static form at the top of the page

        initial_adult_data = other_people_initial_population(True, adults)

        # Instantiates the formset with the management data defined above, forcing a set amount of forms
        formset_adult = AdultFormSet(initial=initial_adult_data, prefix='adult')

        # Zips the formset into the list of adults
        # Converts it to a list, there was trouble parsing the form objects when it was in a zip object
        adult_lists = list(
            zip(adult_record_list, adult_id_list, adult_health_check_status_list, adult_title_list, adult_name_list, adult_birth_day_list,
                adult_birth_month_list, adult_birth_year_list, adult_relationship_list, adult_email_list, adult_mobile_number_list,
                adult_dbs_cert_numbers, adult_dbs_on_capitas, adult_dbs_is_recents, adult_dbs_is_enhanceds,
                adult_dbs_on_updates, adult_lived_abroad, adult_military_base, formset_adult, current_illnesses,
                serious_illnesses, hospital_admissions, local_authorities, adult_enhanced_checks,
                adult_previous_name_lists_list, adult_previous_address_lists_list))

        initial_child_data = other_people_initial_population(False, children)

        formset_child = ChildInHomeFormSet(initial=initial_child_data, prefix='child')

        child_lists = zip(child_id_list, child_name_list, child_birth_day_list, child_birth_month_list,
                          child_birth_year_list,
                          child_relationship_list, formset_child)

        initial_own_child_data = children_initial_population(own_children)

        formset_own_child = ChildNotInHomeFormSet(initial=initial_own_child_data, prefix='own_child_not_in_home')

        formset_own_child_address = ChildNotInHomeAddressFormSet(
            initial=children_address_initial_population(own_child_address_list), prefix='own_child_not_in_home_address')

        own_child_lists = zip(own_children, own_child_address_list, formset_own_child, formset_own_child_address)

        childcare_type = ChildcareType.objects.get(application_id=application_id_local)

        variables = {
            'form': form,
            'formset_adult': formset_adult,
            'formset_child': formset_child,
            'formset_own_child': formset_own_child,
            'formset_own_child_address': formset_own_child_address,
            'application_id': application_id_local,
            'adults_in_home': application.adults_in_home,
            'children_in_home': application.children_in_home,
            'known_to_social_services_pith': application.known_to_social_services_pith,
            'reasons_known_to_social_services_pith': application.reasons_known_to_social_services_pith,
            'adult_lists': adult_lists,
            'child_lists': child_lists,
            'own_child_lists': own_child_lists,
            'previous_registration_lists': adult_previous_registrations,
            'providing_care_in_own_home': providing_care_in_own_home,
            'childcare_type_zero_to_five': childcare_type.zero_to_five,
        }
        log.debug("Rendering people in the home page")
        return render(request, 'childminder_templates/other-people-summary.html', variables)

    elif request.method == 'POST':
        form = OtherPeopleInYourHomeForm(request.POST, table_keys=[application_id_local], prefix='static')
        child_formset = ChildInHomeFormSet(request.POST, prefix='child')
        adult_formset = AdultFormSet(request.POST, prefix='adult')
        own_child_formset = ChildNotInHomeFormSet(request.POST, prefix='own_child_not_in_home')
        own_child_address_formset = ChildNotInHomeAddressFormSet(request.POST, prefix='own_child_not_in_home_address')

        if all([form.is_valid(), child_formset.is_valid(), adult_formset.is_valid(), own_child_formset.is_valid(),
                own_child_address_formset.is_valid()]):
            child_data_list = child_formset.cleaned_data
            adult_data_list = adult_formset.cleaned_data
            own_child_data_list = own_child_formset.cleaned_data
            own_child_address_data_list = own_child_address_formset.cleaned_data

            section_status = 'COMPLETED' if linking_complete else 'IN PROGRESS'

            # ======================================================================================================== #
            # To explain the below:
            # - Each section has at least one associated formset.
            # - Each formset has a list of data from the POST request.
            # - Each element in these lists of data is a dictionary and is associated with a single model.
            # - The code saves the comments stored in these dictionaries in an ARC_COMMENT using the pk from the model
            #   with which it corresponds.
            # - The correspondence is that data for a person stored at adult_data_list[1]
            #   maps to the model stored at adults[1]
            #  ======================================================================================================= #

            review_sections_to_process = {
                'adults_in_home': {
                    'POST_data': adult_data_list,
                    'models': adults
                },
                'children_in_home': {
                    'POST_data': child_data_list,
                    'models': children
                },
            }

            # Only add comments for known_to_social_services_pith if questions are applicable.
            if providing_care_in_own_home:
                log.debug("Add known to social services questions")
                review_sections_to_process.update(
                    {
                        'known_to_social_services_pith': {
                            'POST_data': own_child_data_list,
                            'models': own_children
                        },
                        'own_children_not_in_home_address': {
                            'POST_data': own_child_address_data_list,
                            'models': own_child_address_list
                        }
                    }
                )

            for section in review_sections_to_process.values():
                for person_post_data, person_model in zip(section['POST_data'], section['models']):
                    person_comments = request_to_comment(person_model.pk, person_model._meta.db_table, person_post_data)
                    save_comments(request, person_comments)

                    # Save cygnum relationship type equivalent to person object being iterated
                    if type(person_model) is AdultInHome:
                        person_model.cygnum_relationship_to_childminder = person_post_data['cygnum_relationship']

                    person_model.save()

                    if person_comments:
                        section_status = 'FLAGGED'
                        application = Application.objects.get(pk=application_id_local)
                        application.people_in_home_status = section_status
                        application.people_in_home_arc_flagged = True
                        application.save()

            static_form_comments = request_to_comment(application_id_local, 'APPLICATION', form.cleaned_data)
            if static_form_comments:
                section_status = 'FLAGGED'
                application = Application.objects.get(pk=application_id_local)
                application.people_in_home_arc_flagged = True
                application.people_in_home_status = section_status
                application.save()
            successful = save_comments(request, static_form_comments)
            log.debug("Handling submissions for people in the home page - save successful")
            if not successful:
                log.debug("Handling submissions for people in the home page - save unsuccessful")
                return render(request, '500.html')

            # calculate start and end dates for each adult's current name
            for adult in AdultInHome.objects.filter(application_id=application_id_local):
                # find most recent previous name
                try:
                    # fetch previous name with most recent end date (must actually have an end date)
                    prev_name = PreviousName.objects.filter(person_id=adult.pk, other_person_type='ADULT',
                                                            end_day__isnull=False, end_month__isnull=False,
                                                            end_year__isnull=False)\
                                    .order_by('-end_year', '-end_month', '-end_day')[0]
                except IndexError:
                    prev_name = None

                today = datetime.date.today()
                adult.name_start_day = prev_name.end_day if prev_name else adult.birth_day
                adult.name_start_month = prev_name.end_month if prev_name else adult.birth_month
                adult.name_start_year = prev_name.end_year if prev_name else adult.birth_year
                adult.name_end_day = today.day
                adult.name_end_month = today.month
                adult.name_end_year = today.year
                adult.save()

            status = Arc.objects.get(pk=application_id_local)
            status.people_in_home_review = section_status
            status.save()

            show_references = get_show_references(application_id_local)

            default = '/references/summary/' if show_references else '/review/'
            log.debug("Redirect to references or review")
            redirect_link = redirect_selection(request, default)
            log.debug("Handling submissions for people in the home page")
            return HttpResponseRedirect(settings.URL_PREFIX + redirect_link + '?id=' + application_id_local)

        else:

            # Zips the formset into the list of adults
            # Converts it to a list, there was trouble parsing the form objects when it was in a zip object
            adult_lists = list(zip(adult_record_list, adult_id_list, adult_health_check_status_list, adult_title_list, adult_name_list,
                                   adult_birth_day_list, adult_birth_month_list, adult_birth_year_list,
                                   adult_relationship_list, adult_email_list, adult_mobile_number_list, adult_dbs_cert_numbers,
                                   adult_dbs_on_capitas, adult_dbs_is_recents, adult_dbs_is_enhanceds,
                                   adult_dbs_on_updates, adult_lived_abroad, adult_military_base, adult_formset,
                                   current_illnesses, serious_illnesses, hospital_admissions, local_authorities,
                                   adult_enhanced_checks, adult_previous_name_lists_list,
                                   adult_previous_address_lists_list))

            child_lists = zip(child_id_list, child_name_list, child_birth_day_list, child_birth_month_list,
                              child_birth_year_list,
                              child_relationship_list, child_formset)

            own_child_lists = zip(own_children, own_child_address_list, own_child_formset, own_child_address_formset)

            for adult_form, adult_name in zip(adult_formset, adult_name_list):
                adult_form.error_summary_title = 'There was a problem (' + adult_name + ')'

            for child_form, child_name in zip(child_formset, child_name_list):
                child_form.error_summary_title = 'There was a problem (' + child_name + ')'

            for child_form, child_address_form, child_name in zip(own_child_formset, own_child_address_formset,
                                                                  own_child_name_list):
                child_form.error_summary_title = 'There was a problem (' + child_name + ')'
                child_address_form.error_summary_title = 'There was a problem (' + child_name + ')'

            childcare_type = ChildcareType.objects.get(application_id=application_id_local)

            variables = {
                'form': form,
                'formset_adult': adult_formset,
                'formset_child': child_formset,
                'formset_own_child': own_child_formset,
                'formset_own_child_address': own_child_address_formset,
                'application_id': application_id_local,
                'adults_in_home': application.adults_in_home,
                'children_in_home': application.children_in_home,
                'known_to_social_services_pith': application.known_to_social_services_pith,
                'adult_lists': adult_lists,
                'child_lists': child_lists,
                'own_child_lists': own_child_lists,
                'previous_registration_lists': adult_previous_registrations,
                'providing_care_in_own_home': providing_care_in_own_home,
                'childcare_type_zero_to_five': childcare_type.zero_to_five,
            }
            log.debug("Render people in the home page")
            return render(request, 'childminder_templates/other-people-summary.html', variables)


