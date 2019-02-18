from uuid import uuid4

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.forms import formset_factory, modelformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render

from arc_application.childminder_task_util import get_show_references
from ...decorators import group_required, user_assigned_application
from ...forms.childminder_forms.form import AdultInYourHomeForm, ChildInYourHomeForm, OtherPeopleInYourHomeForm, \
    OtherPersonPreviousNames, \
    ChildForm, ChildAddressForm
from ...models import ChildInHome, AdultInHome, Arc, Application, PreviousAddress, ChildAddress, \
    OtherPersonPreviousRegistrationDetails, HealthCheckCurrent, HealthCheckSerious, HealthCheckHospital, ChildcareType, \
    Child, ApplicantHomeAddress
from ...models.previous_name import PreviousName
from ...review_util import request_to_comment, save_comments, redirect_selection, build_url
from ...views import other_people_initial_population, children_initial_population, children_address_initial_population


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
    adult_name_list = []
    adult_birth_day_list = []
    adult_birth_month_list = []
    adult_birth_year_list = []
    adult_relationship_list = []
    adult_email_list = []
    adult_dbs_cert_numbers = []
    adult_dbs_on_capitas = []
    adult_dbs_is_recents = []
    adult_dbs_is_capitas = []
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
    adult_enhanced_checks = []

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

    for adult in adults:

        # TODO replace dbs lookup with references to stored results in database, when implemented
        dbs_record = None  # getattr(dbs.read(adult.dbs_certificate_number), 'record', None)

        dbs_on_capita = adult.capita
        dbs_is_recent = adult.within_three_months
        asked_capita = adult.capita
        asked_on_update = (dbs_on_capita and not dbs_is_recent) or not dbs_on_capita

        if adult.middle_names and adult.middle_names != '':
            name = adult.first_name + ' ' + adult.middle_names + ' ' + adult.last_name
        else:
            name = adult.first_name + ' ' + adult.last_name

        adult_record_list.append(adult)
        adult_id_list.append(adult.adult_id)
        adult_health_check_status_list.append(adult.health_check_status)
        adult_name_list.append(name)
        adult_birth_day_list.append(adult.birth_day)
        adult_birth_month_list.append(adult.birth_month)
        adult_birth_year_list.append(adult.birth_year)
        adult_relationship_list.append(adult.relationship)
        adult_email_list.append(adult.email)
        adult_dbs_cert_numbers.append(adult.dbs_certificate_number)
        adult_dbs_on_capitas.append(dbs_on_capita)
        adult_dbs_is_recents.append(dbs_is_recent)
        adult_dbs_is_capitas.append(adult.capita if asked_capita else None)
        adult_dbs_on_updates.append(adult.on_update if asked_on_update else None)
        #
        adult_lived_abroad.append(adult.lived_abroad)
        adult_military_base.append(adult.military_base)
        current_illnesses.append(HealthCheckCurrent.objects.filter(person_id=adult.pk))
        serious_illnesses.append(HealthCheckSerious.objects.filter(person_id=adult.pk))
        hospital_admissions.append(HealthCheckHospital.objects.filter(person_id=adult.pk))
        local_authorities.append(adult.reasons_known_to_council_health_check)
        adult_enhanced_checks.append(adult.enhanced_check)

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

    for adult_id, adult_name in zip(adult_id_list, adult_name_list):
        adult_name_querysets.append(PreviousName.objects.filter(person_id=adult_id, other_person_type='ADULT'))
        adult_address_querysets.append(PreviousAddress.objects.filter(person_id=adult_id, person_type='ADULT'))
        previous_registration_querysets.append(
            OtherPersonPreviousRegistrationDetails.objects.filter(person_id_id=adult_id))

    adult_ebulk_lists = list(zip(adult_id_list, adult_name_list, adult_name_querysets, adult_address_querysets))
    previous_registration_lists = list(zip(adult_id_list, adult_name_list, previous_registration_querysets))

    form.error_summary_title = 'There was a problem'

    if request.method == 'GET':
        # Defines the static form at the top of the page

        initial_adult_data = other_people_initial_population(True, adults)

        # Instantiates the formset with the management data defined above, forcing a set amount of forms
        formset_adult = AdultFormSet(initial=initial_adult_data, prefix='adult')

        # Zips the formset into the list of adults
        # Converts it to a list, there was trouble parsing the form objects when it was in a zip object
        adult_lists = list(
            zip(adult_record_list, adult_id_list, adult_health_check_status_list, adult_name_list, adult_birth_day_list,
                adult_birth_month_list, adult_birth_year_list, adult_relationship_list, adult_email_list,
                adult_dbs_cert_numbers, adult_dbs_on_capitas, adult_dbs_is_recents, adult_dbs_is_capitas,
                adult_dbs_on_updates, adult_lived_abroad, adult_military_base, formset_adult, current_illnesses,
                serious_illnesses, hospital_admissions, local_authorities, adult_enhanced_checks))

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

        zero_to_five_list = ChildcareType.objects.get(application_id=application_id_local)

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
            'adult_ebulk_lists': adult_ebulk_lists,
            'previous_registration_lists': previous_registration_lists,
            'providing_care_in_own_home': providing_care_in_own_home,
            'childcare_type_zero_to_five': zero_to_five_list,
        }
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

            section_status = 'COMPLETED'

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
            if not successful:
                return render(request, '500.html')

            status = Arc.objects.get(pk=application_id_local)
            status.people_in_home_review = section_status
            status.save()
            childcare_type = ChildcareType.objects.get(application_id=application_id_local)

            show_references = get_show_references(application_id_local)

            default = '/references/summary' if show_references else '/review'
            redirect_link = redirect_selection(request, default)

            return HttpResponseRedirect(settings.URL_PREFIX + redirect_link + '?id=' + application_id_local)

        else:

            # Zips the formset into the list of adults
            # Converts it to a list, there was trouble parsing the form objects when it was in a zip object
            adult_lists = list(zip(adult_record_list, adult_id_list, adult_health_check_status_list, adult_name_list,
                                   adult_birth_day_list, adult_birth_month_list, adult_birth_year_list,
                                   adult_relationship_list, adult_email_list, adult_dbs_cert_numbers,
                                   adult_dbs_on_capitas, adult_dbs_is_recents, adult_dbs_is_capitas,
                                   adult_dbs_on_updates, adult_lived_abroad, adult_military_base, adult_formset,
                                   current_illnesses, serious_illnesses, hospital_admissions, local_authorities,
                                   adult_enhanced_checks))

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

            zero_to_five_list = ChildcareType.objects.get(application_id=application_id_local)

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
                'adult_ebulk_lists': adult_ebulk_lists,
                'previous_registration_lists': previous_registration_lists,
                'providing_care_in_own_home': providing_care_in_own_home,
                'childcare_type_zero_to_five': zero_to_five_list,
            }
            return render(request, 'childminder_templates/other-people-summary.html', variables)


@group_required(settings.ARC_GROUP)
@user_assigned_application
def add_previous_name(request):
    """
    View to handle previous name formset for the either adults or children in the home
    :param request:
    :return:
    """

    if request.method == 'POST':

        app_id = request.POST["id"]
        person_id = request.POST["person_id"]
        person_type = request.POST["type"]
        # If the user is updating from the summary page, referrer is set to let the update now to redirect back to
        # summary
        try:
            referrer = request.POST["referrer"]
        except:
            # If it doesn't exist, just set it to none
            referrer = None

        # If the action (set in the submit buttons on previous names html) is add another name, do the following
        if request.POST['action'] == "Add another name":
            # Create an empty model formset object
            previous_names_formset = modelformset_factory(PreviousName, form=OtherPersonPreviousNames)

            # Instantiate and populate it with post request details
            formset = previous_names_formset(request.POST)
            if formset.is_valid():
                # If its valid, save it
                formset.save()

                # Set extra to 1, so that an extra empty form appears when rendered (see bottom of function)
                extra = 1
            else:
                # If invalid, keep extra the same and return the same page
                extra = int(float(request.POST['extra']))
                context = {
                    'formset': formset,
                    'application_id': app_id,
                    'person_id': person_id,
                    'person_type': person_type,
                    'extra': extra
                }
                return render(request, 'childminder_templates/add-previous-names.html', context)

        if request.POST['action'] == 'delete':
            # This scans the request poost dictionary for a key submitted by clicking remove person
            for key in request.POST.keys():
                try:
                    # This trys to cast each key as a uuid, dismisses it if this fails
                    if request.POST[key] == 'Remove this name':
                        # If the associated value in the POST dict is 'Remove this person'

                        # If the key exists in the database, delete it
                        if len(PreviousName.objects.filter(pk=key)) == 1:
                            PreviousName.objects.filter(pk=key).delete()
                            extra = int(float(request.POST['extra']))

                        # If it doesnt exist (clicked remove on an empty form)
                        elif not PreviousName.objects.filter(pk=key):
                            # Reduce the extra value, in effect removing the extra form
                            extra = int(float(request.POST['extra'])) - 1
                except ValueError:
                    pass

        if request.POST['action'] == "Confirm and continue":
            # If we're saving, instantiate the formset with the POST data
            previous_names_formset = modelformset_factory(PreviousName, form=OtherPersonPreviousNames)
            formset = previous_names_formset(request.POST)
            if formset.is_valid():
                formset.save()
                if referrer == 'None':
                    # If they've come from the 'add ebulk' button
                    return HttpResponseRedirect(build_url('other_people_summary', get={'id': app_id}))
                else:
                    # If they've come from the summary page (using a change link)
                    return HttpResponseRedirect(build_url('other_people_summary', get={'id': app_id}))
            else:
                # If errors, re render the page with them
                extra = int(float(request.POST['extra']))
                context = {
                    'formset': formset,
                    'application_id': app_id,
                    'person_id': person_id,
                    'person_type': person_type,
                    'extra': extra
                }

                return render(request, 'childminder_templates/add-previous-names.html', context)

    if request.method == "GET":

        # General context defintion on get request
        app_id = request.GET["id"]
        person_id = request.GET["person_id"]
        person_type = request.GET["type"]
        # Attempt to grab referrer, as explained in post request
        try:
            referrer = request.GET["referrer"]
        except:
            referrer = None
        extra = 0

    initial = []
    # Grab data already in table for the passed in person_id of the right person_type
    if person_type == 'ADULT':
        key_dict = {"person_id": person_id}
        initial_data = PreviousName.objects.filter(other_person_type=person_type, person_id=person_id)
    elif person_type == 'CHILD':
        key_dict = {"person_id": person_id}
        initial_data = PreviousName.objects.filter(other_person_type=person_type, person_id=person_id)

    if request.method == "GET" and len(initial_data) == 0:
        extra = extra + 1

    # Extra forms need their primary key and person type, as these are hidden values (see form definition)
    for extra_form in range(0, extra):
        temp_initial_dict = {
            "previous_name_id": uuid4(),
            "other_person_type": person_type,
        }
        # Merge this blank initial form into the initial data dictionary
        initial.append({**temp_initial_dict, **key_dict})

    # Instantiate and populate formset, queryset will find any data in the database
    previous_names_formset = modelformset_factory(PreviousName, form=OtherPersonPreviousNames, extra=extra)
    formset = previous_names_formset(initial=initial, queryset=initial_data)

    context = {
        'formset': formset,
        'application_id': app_id,
        'person_id': person_id,
        'person_type': person_type,
        'extra': extra,
        'referrer': referrer
    }

    return render(request, 'childminder_templates/add-previous-names.html', context)
