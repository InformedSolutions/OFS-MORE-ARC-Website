import datetime
import logging

from django.conf import settings
from django.forms import formset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render

from ...decorators import group_required, user_assigned_application
from ...forms.previous_names import PersonPreviousNameForm
from ...models import PreviousName
from ...review_util import build_url

# Initiate logging
log = logging.getLogger('')

@group_required(settings.ARC_GROUP)
@user_assigned_application
def add_previous_name(request):
    """
    View to handle previous name formset for the either the applicant or adults/children in the home
    """
    if request.method == 'POST':

        app_id = request.POST["id"]
        person_id = request.POST["person_id"]
        person_type = request.POST["type"]

        # Create formset and populate from post data
        formset = _previous_names_page_formset(data=request.POST)

        # Delete is a special case that should be done without validating the rest of the form.
        # Look for parameter name starting with 'delete' from special submit button
        delete_action = ([k for k, v in request.POST.items() if k.startswith('delete-')]+[None])[0]
        if delete_action is not None:

            # param name in the form 'delete-[id]'
            delete_id = delete_action[len('delete-'):]

            # id will be blank if user is removing the new, empty form. Can safely ignore
            if delete_id != '':
                PreviousName.objects.filter(previous_name_id=delete_id).delete()

            # redirect back to page
            return _previous_names_page_redirect(app_id, person_id, person_type)

        # other operation require validation of form to update list of previous names
        if not formset.is_valid():
            # If invalid, render same page with errors and stop
            return _previous_names_page_render(request, app_id, person_id, person_type, formset)

        # save the posted names and continue
        _replace_previous_names(person_id, person_type, formset)

        # perform appropriate redirect according to action and person type
        if request.POST['action'] == "Add another name":
            log.debug("Redirect to Add another name")
            # redirect back to page, with 'show_extra' parameter so that empty form is displayed
            return _previous_names_page_redirect(app_id, person_id, person_type, show_extra=True)

        elif person_type in ('ADULT', 'CHILD'):
            log.debug("Conditional logic: Redirect to other people summary")
            return HttpResponseRedirect(build_url('other_people_summary', get={'id': app_id}))

        else:
            log.debug("Conditional logic: Redirect to personal details summary")
            return HttpResponseRedirect(build_url('personal_details_summary', get={'id': app_id}))

    elif request.method == "GET":

        app_id = request.GET['id']
        person_id = request.GET['person_id']
        person_type = request.GET['type']
        show_extra = request.GET.get('show_extra', None)
        if show_extra is not None:
            show_extra = bool(show_extra)

        return _previous_names_page_render(request, app_id, person_id, person_type, show_extra=show_extra)


def _previous_names_page_render(request, app_id, person_id, person_type, formset=None, show_extra=None):

    # if form data not provided from request, populate new form set from database
    if formset is None:
        formset = _fetch_previous_names(person_id, person_type, show_extra)

    context = {
        'formset': formset,
        'application_id': app_id,
        'person_id': person_id,
        'person_type': person_type,
    }
    log.debug("Render previous name page")
    return render(request, 'childminder_templates/add-previous-names.html', context)


def _previous_names_page_redirect(app_id, person_id, person_type, show_extra=None):

    params = {'id': app_id, 'person_id': person_id, 'type': person_type}
    if show_extra:
        params['show_extra'] = True
    return HttpResponseRedirect(build_url(add_previous_name, get=params))


def _previous_names_page_formset(data=None, initial=None, show_extra=False):

    # create formset type and instantiate
    PreviousNameFormset = formset_factory(PersonPreviousNameForm, extra=1 if show_extra else 0)
    formset = PreviousNameFormset(data=data, initial=initial)

    # ensure extra forms are required to be filled, as they're not by default
    for form in formset:
        form.empty_permitted = False

    return formset


def _fetch_previous_names(person_id, person_type, show_extra=None):

    # Grab data already in table for the passed in person_id of the right person_type
    models = PreviousName.objects.filter(other_person_type=person_type, person_id=person_id).order_by('order')

    # Determine whether to show additional empty form in formset
    if show_extra is None:
        show_extra = len(models) == 0

    # prepare form data
    initial_data = [{
        'previous_name_id': m.previous_name_id,
        'first_name': m.first_name,
        'middle_names': m.middle_names,
        'last_name': m.last_name,
        'start_date': m.start_date,
        'end_date': m.end_date,
    } for m in models]

    # create and return formset
    return _previous_names_page_formset(initial=initial_data, show_extra=show_extra)


def _replace_previous_names(person_id, person_type, formset):

    # remove existing names
    PreviousName.objects.filter(person_id=person_id, other_person_type=person_type).delete()

    # save new names
    for i, form in enumerate(formset):
        PreviousName.objects.create(
            person_id=person_id,
            other_person_type=person_type,
            first_name=form.cleaned_data['first_name'],
            middle_names=form.cleaned_data['middle_names'],
            last_name=form.cleaned_data['last_name'],
            start_day=form.cleaned_data['start_date'].day,
            start_month=form.cleaned_data['start_date'].month,
            start_year=form.cleaned_data['start_date'].year,
            end_day=form.cleaned_data['end_date'].day,
            end_month=form.cleaned_data['end_date'].month,
            end_year=form.cleaned_data['end_date'].year,
            order=i,
        )
