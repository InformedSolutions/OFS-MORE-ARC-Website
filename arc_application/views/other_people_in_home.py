from uuid import uuid4, UUID

from django.conf import settings
from django.forms import formset_factory, modelformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render

from arc_application.models.previous_name import PreviousName
from ..forms import AdultInYourHomeForm, ChildInYourHomeForm, OtherPeopleInYourHomeForm, OtherPersonPreviousNames
from arc_application.models import ChildInHome, AdultInHome, Arc, Application
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
    AdultFormSet = formset_factory(AdultInYourHomeForm)
    ChildFormSet = formset_factory(ChildInYourHomeForm)
    TABLE_NAMES = ['ADULT_IN_HOME', 'CHILD_IN_HOME']

    if request.method == 'GET':
        # Defines the static form at the top of the page

        application_id_local = request.GET["id"]
        form = OtherPeopleInYourHomeForm(table_keys=[application_id_local], prefix='static')

    elif request.method == 'POST':
        application_id_local = request.POST["id"]
        form = OtherPeopleInYourHomeForm(request.POST, prefix='static', table_keys=[application_id_local])
        child_formset = ChildFormSet(request.POST, prefix='child')
        adult_formset = AdultFormSet(request.POST, prefix='adult')

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
                    person_comments = request_to_comment(person_id, TABLE_NAMES[object_index], person)
                    if person_comments:
                        section_status = 'FLAGGED'
                    successful = save_comments(person_comments)
                    if not successful:
                        return render(request, '500.html')

            static_form_comments = request_to_comment(application_id_local, 'APPLICATION', form.cleaned_data)
            if static_form_comments:
                section_status = 'FLAGGED'
            successful = save_comments(static_form_comments)
            if not successful:
                return render(request, '500.html')

            status = Arc.objects.get(pk=application_id_local)
            status.people_in_home_review = section_status
            status.save()
            default = '/review'
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
    adult_permission_list = []
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
        adult_permission_list.append(adult.permission_declare)
    # Defines the data required for rendering the amount of forms in the below formset
    amount_of_adults = str(len(adult_name_list))
    data = {
        'adult-TOTAL_FORMS': amount_of_adults,
        'adult-INITIAL_FORMS': amount_of_adults,
        'adult-MAX_NUM_FORMS': '',
    }

    initial_adult_data = other_people_initial_population(True, adults_list)

    # Instantiates the formset with the management data defined above, forcing a set amount of forms
    formset_adult = AdultFormSet(initial=initial_adult_data, prefix='adult')

    # Zips the formset into the list of adults
    adult_lists = zip(adult_id_list, adult_name_list, adult_birth_day_list, adult_birth_month_list, adult_birth_year_list,
                      adult_relationship_list, adult_dbs_list, adult_permission_list, formset_adult)

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

    formset_child = ChildFormSet(initial=initial_child_data, prefix='child')

    child_lists = zip(child_id_list, child_name_list, child_birth_day_list, child_birth_month_list, child_birth_year_list,
                      child_relationship_list, formset_child)

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

    if request.method == 'POST':

        app_id = request.POST["id"]
        person_id = request.POST["person_id"]
        person_type = request.POST["type"]

        if request.POST['action'] == "Add another name":
            PreviousNamesFormset = modelformset_factory(PreviousName, form=OtherPersonPreviousNames)
            formset = PreviousNamesFormset(request.POST)
            if formset.is_valid():
                formset.save()
                extra = 1
            else:
                extra = int(float(request.POST['extra']))
                context = {
                    'formset': formset,
                    'application_id': app_id,
                    'person_id': person_id,
                    'person_type': person_type,
                    'extra': extra
                }
                extra = int(float(request.POST['extra']))
                return render(request, 'add-previous-names.html', context)


        if request.POST['action'] == 'delete':
            for key in request.POST.keys():
                try:
                    test_val = UUID(key, version=4)
                    if request.POST[key] == 'Remove this person':
                        test = PreviousName.objects.filter(pk=key)
                        if len(PreviousName.objects.filter(pk=key)) == 1:
                            PreviousName.objects.filter(pk=key).delete()
                            extra = int(float(request.POST['extra']))
                        elif not PreviousName.objects.filter(pk=key):
                            extra = int(float(request.POST['extra'])) - 1
                except ValueError:
                    pass



        if request.POST['action'] == "Confirm and continue":
            PreviousNamesFormset = modelformset_factory(PreviousName, form=OtherPersonPreviousNames)
            formset = PreviousNamesFormset(request.POST)
            if formset.is_valid():
                formset.save()
                return HttpResponseRedirect(build_url('other_people_summary', get={"id": app_id}))
            else:
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

        app_id = request.GET["id"]
        person_id = request.GET["person_id"]
        person_type = request.GET["type"]
        extra = 0


    initial = []
    if person_type == 'ADULT':
        key_dict = {"adult_id": person_id}
        initial_data = PreviousName.objects.filter(other_person_type=person_type, adult_id=person_id)
    elif person_type == 'CHILD':
        key_dict = {"child_id": person_id}
        initial_data = PreviousName.objects.filter(other_person_type=person_type, child_id=person_id)

    if request.method == "GET" and not initial_data:
        extra = extra + 1

    for extra_form in range(0, extra):
        temp_initial_dict = {
            "previous_name_id": uuid4(),
            "other_person_type": person_type,
        }
        initial.append({**temp_initial_dict, **key_dict})

    PreviousNamesFormset = modelformset_factory(PreviousName, form=OtherPersonPreviousNames, extra=extra)
    formset = PreviousNamesFormset(initial=initial, queryset=initial_data)



    context = {
        'formset': formset,
        'application_id': app_id,
        'person_id': person_id,
        'person_type': person_type,
        'extra': extra
    }

    return render(request, 'add-previous-names.html', context)




