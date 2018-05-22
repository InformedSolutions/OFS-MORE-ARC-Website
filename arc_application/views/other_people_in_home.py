from uuid import uuid4, UUID

from django.conf import settings
from django.forms import formset_factory, modelformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render

from arc_application.models.previous_name import PreviousName
from ..forms.form import AdultInYourHomeForm, ChildInYourHomeForm, OtherPeopleInYourHomeForm, OtherPersonPreviousNames
from arc_application.models import ChildInHome, AdultInHome, Arc, Application, PreviousAddress
from arc_application.review_util import request_to_comment, save_comments, redirect_selection, build_url
from arc_application.views import other_people_initial_population


def other_people_summary(request):
    """
    Method returning the template for the People in your home: summary page (for a given application)
    displaying entered data for this task and navigating to the task list when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered People in your home: summary template
    """
    # Defines the formset using formset factory
    adult_form_set = formset_factory(AdultInYourHomeForm)
    child_form_set = formset_factory(ChildInYourHomeForm)
    table_names = ['ADULT_IN_HOME', 'CHILD_IN_HOME']

    if request.method == 'GET':
        # Defines the static form at the top of the page

        application_id_local = request.GET["id"]
        form = OtherPeopleInYourHomeForm(table_keys=[application_id_local], prefix='static')

    elif request.method == 'POST':
        application_id_local = request.POST["id"]
        form = OtherPeopleInYourHomeForm(request.POST, prefix='static', table_keys=[application_id_local])
        child_formset = child_form_set(request.POST, prefix='child')
        adult_formset = adult_form_set(request.POST, prefix='adult')

        application_id_local = request.POST["id"]

        if all([form.is_valid(), child_formset.is_valid(), adult_formset.is_valid()]):
            child_objects = ChildInHome.objects.filter(application_id=application_id_local).order_by('child')
            adult_objects = AdultInHome.objects.filter(application_id=application_id_local).order_by('adult')

            child_data_list = child_formset.cleaned_data
            adult_data_list = adult_formset.cleaned_data

            child_data_list.pop()
            adult_data_list.pop()

            request_list = [adult_data_list, child_data_list]
            object_list = [adult_objects, child_objects]
            attr_list = ['adult_id', 'child_id']

            section_status = 'COMPLETED'

            for dictionary in request_list:
                object_index = request_list.index(dictionary)
                for person in dictionary:
                    request_index = dictionary.index(person)
                    person_object_list = object_list[object_index]
                    person_object = person_object_list[request_index]
                    person_id = getattr(person_object, attr_list[object_index])
                    person_comments = request_to_comment(person_id, table_names[object_index], person)
                    if person_comments:
                        section_status = 'FLAGGED'
                        application = Application.objects.get(pk=application_id_local)
                        application.people_in_home_arc_flagged = True
                        application.save()
                    successful = save_comments(request, person_comments)
                    if not successful:
                        return render(request, '500.html')

            static_form_comments = request_to_comment(application_id_local, 'APPLICATION', form.cleaned_data)
            if static_form_comments:
                section_status = 'FLAGGED'
                application = Application.objects.get(pk=application_id_local)
                application.people_in_home_arc_flagged = True
                application.save()
            successful = save_comments(request, static_form_comments)
            if not successful:
                return render(request, '500.html')

            status = Arc.objects.get(pk=application_id_local)
            status.people_in_home_review = section_status
            status.save()
            default = '/references/summary'
            redirect_link = redirect_selection(request, default)

            return HttpResponseRedirect(settings.URL_PREFIX + redirect_link + '?id=' + application_id_local)

    adults_list = AdultInHome.objects.filter(application_id=application_id_local).order_by('adult')
    adult_id_list = []
    adult_name_list = []
    adult_birth_day_list = []
    adult_birth_month_list = []
    adult_birth_year_list = []
    adult_relationship_list = []
    adult_dbs_list = []
    children_list = ChildInHome.objects.filter(application_id=application_id_local).order_by('child')
    child_id_list = []
    child_name_list = []
    child_birth_day_list = []
    child_birth_month_list = []
    child_birth_year_list = []
    child_relationship_list = []
    application = Application.objects.get(pk=application_id_local)
    for adult in adults_list:
        if adult.middle_names != '':
            name = adult.first_name + ' ' + adult.middle_names + ' ' + adult.last_name
        elif adult.middle_names == '':
            name = adult.first_name + ' ' + adult.last_name
        adult_id_list.append(adult.adult_id)
        adult_name_list.append(name)
        adult_birth_day_list.append(adult.birth_day)
        adult_birth_month_list.append(adult.birth_month)
        adult_birth_year_list.append(adult.birth_year)
        adult_relationship_list.append(adult.relationship)
        adult_dbs_list.append(adult.dbs_certificate_number)
    # Defines the data required for rendering the amount of forms in the below formset
    amount_of_adults = str(len(adult_name_list))
    data = {
        'adult-TOTAL_FORMS': amount_of_adults,
        'adult-INITIAL_FORMS': amount_of_adults,
        'adult-MAX_NUM_FORMS': '',
    }

    initial_adult_data = other_people_initial_population(True, adults_list)

    # Instantiates the formset with the management data defined above, forcing a set amount of forms
    formset_adult = adult_form_set(initial=initial_adult_data, prefix='adult')

    # Zips the formset into the list of adults
    adult_lists = zip(adult_id_list, adult_name_list, adult_birth_day_list, adult_birth_month_list,
                      adult_birth_year_list,
                      adult_relationship_list, adult_dbs_list, formset_adult)

    # Converts it to a list, there was trouble parsing the form objects when it was in a zip object
    adult_lists = list(adult_lists)

    for child in children_list:
        if child.middle_names != '':
            name = child.first_name + ' ' + child.middle_names + ' ' + child.last_name
        elif child.middle_names == '':
            name = child.first_name + ' ' + child.last_name
        child_id_list.append(child.child_id)
        child_name_list.append(name)
        child_birth_day_list.append(child.birth_day)
        child_birth_month_list.append(child.birth_month)
        child_birth_year_list.append(child.birth_year)
        child_relationship_list.append(child.relationship)

    initial_child_data = other_people_initial_population(False, children_list)

    formset_child = child_form_set(initial=initial_child_data, prefix='child')

    child_lists = zip(child_id_list, child_name_list, child_birth_day_list, child_birth_month_list,
                      child_birth_year_list,
                      child_relationship_list, formset_child)

    adult_ids = []
    adult_names = []
    name_querysets = []
    address_querysets = []

    for adult_id, adult_name in zip(adult_id_list, adult_name_list):
        adult_ids.append(adult_id)
        adult_names.append(adult_name)
        name_querysets.append(PreviousName.objects.filter(person_id=adult_id, other_person_type='ADULT'))
        address_querysets.append(PreviousAddress.objects.filter(person_id=adult_id, person_type='ADULT'))

    adult_ebulk_lists = list(zip(adult_ids, adult_names, name_querysets, address_querysets))

    child_ids = []
    child_names = []
    name_querysets = []
    address_querysets = []

    for child_id, child_name in zip(child_id_list, child_name_list):
        child_ids.append(child_id)
        child_names.append(child_name)
        name_querysets.append(PreviousName.objects.filter(person_id=child_id, other_person_type='CHILD'))
        address_querysets.append(PreviousAddress.objects.filter(person_id=child_id, person_type='CHILD'))

    child_ebulk_lists = zip(child_ids, child_names, name_querysets, address_querysets)

    variables = {
        'form': form,
        'formset_adult': formset_adult,
        'formset_child': formset_child,
        'application_id': application_id_local,
        'adults_in_home': application.adults_in_home,
        'children_in_home': application.children_in_home,
        'number_of_adults': adults_list.count(),
        'number_of_children': children_list.count(),
        'adult_lists': adult_lists,
        'child_lists': child_lists,
        'adult_ebulk_lists': adult_ebulk_lists,
        'child_ebulk_lists': child_ebulk_lists,
        'turning_16': application.children_turning_16,
        'people_in_home_status': application.people_in_home_status
    }
    return render(request, 'other-people-summary.html', variables)


def person_data_selector(request):
    pass


def add_previous_address(request):
    if request.method == "GET":
        app_id = request.GET["id"]
        person_id = request.GET["person_id"]


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
        # If the user is updating from the summary page, referrer is set to let the update now to redirect back to summary
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
                return render(request, 'add-previous-names.html', context)

        if request.POST['action'] == 'delete':
            # This scans the request poost dictionary for a key submitted by clicking remove person
            for key in request.POST.keys():
                try:
                    # This trys to cast each key as a uuid, dismisses it if this fails
                    test_val = UUID(key, version=4)
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
                    return HttpResponseRedirect(build_url('other-people-previous-addresses', get={"id": app_id,
                                                                                                  "person_id": person_id,
                                                                                                  "person_type": person_type,
                                                                                                  "state": "entry"}))
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

                return render(request, 'add-previous-names.html', context)

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

    return render(request, 'add-previous-names.html', context)
