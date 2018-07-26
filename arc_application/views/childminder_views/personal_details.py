from uuid import UUID

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render

from ...forms.childminder_forms.form import PersonalDetailsForm, OtherPersonPreviousNames, PreviousRegistrationDetails
from arc_application.models import ApplicantPersonalDetails, ApplicantName, ApplicantHomeAddress, Arc, Application, \
    PreviousName, uuid4
from arc_application.review_util import request_to_comment, save_comments, redirect_selection, build_url
from arc_application.views.childminder_views.personal_details_addresses import get_stored_addresses
from arc_application.decorators import group_required, user_assigned_application


@login_required
@group_required(settings.ARC_GROUP, raise_exception=True)
@user_assigned_application
def personal_details_summary(request):
    """
    Method returning the template for the Your personal details: summary page (for a given application)
    displaying entered data for this task and navigating to the task list when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your personal details: summary template
    """
    application_id_local = request.GET["id"]
    personal_detail_id = (ApplicantPersonalDetails.objects.get(application_id=application_id_local)).personal_detail_id
    applicant_name_id = (ApplicantName.objects.get(personal_detail_id=personal_detail_id)).name_id
    applicant_home_address_id = (ApplicantHomeAddress.objects.get(personal_detail_id=personal_detail_id,
                                                                  current_address=True)).home_address_id

    TABLE_NAMES = ['APPLICANT_PERSONAL_DETAILS', 'APPLICANT_NAME', 'APPLICANT_HOME_ADDRESS']
    PERSONAL_DETAIL_FIELDS = ['date_of_birth_declare', 'date_of_birth_comments']
    NAME_FIELDS = ['name_declare', 'name_comments']
    HOME_ADDRESS_FIELDS = ['home_address_declare', 'home_address_comments',
                           'childcare_location_declare', 'childcare_location_comments']
    PERSON_TYPE = 'APPLICANT'

    if request.method == 'GET':
        # Collect required ids
        application_id_local = request.GET["id"]
        personal_detail_id = (
            ApplicantPersonalDetails.objects.get(application_id=application_id_local)).personal_detail_id
        applicant_name_id = (ApplicantName.objects.get(personal_detail_id=personal_detail_id)).name_id
        applicant_home_address_id = (ApplicantHomeAddress.objects.get(personal_detail_id=personal_detail_id,
                                                                      current_address=True)).home_address_id

        form = PersonalDetailsForm(table_keys=[personal_detail_id, applicant_name_id, applicant_home_address_id])

    elif request.method == 'POST':
        birthdate_dict = {}
        name_dict = {}
        address_dict = {}

        form = PersonalDetailsForm(request.POST,
                                   table_keys=[personal_detail_id, applicant_name_id, applicant_home_address_id])
        application_id_local = request.POST["id"]
        personal_detail_id = (
            ApplicantPersonalDetails.objects.get(application_id=application_id_local)).personal_detail_id
        applicant_name_id = (ApplicantName.objects.get(personal_detail_id=personal_detail_id)).name_id
        applicant_home_address_id = (ApplicantHomeAddress.objects.get(personal_detail_id=personal_detail_id,
                                                                      current_address=True)).home_address_id
        if form.is_valid():
            # Populate field dictionaries for use in request to comment funciton
            # As the data required on this form is stored in three different tables, these must be sorted by table
            for field in form.cleaned_data:
                if field in PERSONAL_DETAIL_FIELDS:
                    birthdate_dict[field] = form.cleaned_data[field]
                if field in NAME_FIELDS:
                    name_dict[field] = form.cleaned_data[field]
                if field in HOME_ADDRESS_FIELDS:
                    address_dict[field] = form.cleaned_data[field]

            # Populate below lists with comments by table
            birthdate_comments = request_to_comment(personal_detail_id, TABLE_NAMES[0], birthdate_dict)
            name_comments = request_to_comment(applicant_name_id, TABLE_NAMES[1], name_dict)
            address_comments = request_to_comment(applicant_home_address_id, TABLE_NAMES[2], address_dict)

            birthdate_save_successful = save_comments(request, birthdate_comments)
            name_save_successful = save_comments(request, name_comments)
            address_save_successful = save_comments(request, address_comments)

            application = Application.objects.get(pk=application_id_local)

            if not birthdate_comments and not name_comments and not address_comments:
                section_status = 'COMPLETED'
                application.personal_details_arc_flagged = False
            else:
                section_status = 'FLAGGED'
                application.personal_details_arc_flagged = True

            application.save()

            if birthdate_save_successful and name_save_successful and address_save_successful:

                status = Arc.objects.get(pk=application_id_local)
                status.personal_details_review = section_status
                status.save()
                default = '/first-aid/summary'
                redirect_link = redirect_selection(request, default)

                return HttpResponseRedirect(settings.URL_PREFIX + redirect_link + '?id=' + application_id_local)

            else:
                return render(request, '500.html')

    application_id_local = request.GET["id"]
    personal_detail_id = ApplicantPersonalDetails.objects.get(application_id=application_id_local)
    birth_day = personal_detail_id.birth_day
    birth_month = personal_detail_id.birth_month
    birth_year = personal_detail_id.birth_year
    applicant_name_record = ApplicantName.objects.get(personal_detail_id=personal_detail_id)
    first_name = applicant_name_record.first_name
    middle_names = applicant_name_record.middle_names
    last_name = applicant_name_record.last_name
    applicant_home_address_record = ApplicantHomeAddress.objects.get(personal_detail_id=personal_detail_id,
                                                                     current_address=True)
    street_line1 = applicant_home_address_record.street_line1
    street_line2 = applicant_home_address_record.street_line2
    town = applicant_home_address_record.town
    county = applicant_home_address_record.county
    postcode = applicant_home_address_record.postcode
    location_of_childcare = applicant_home_address_record.childcare_address
    applicant_childcare_address_record = ApplicantHomeAddress.objects.get(personal_detail_id=personal_detail_id,
                                                                          childcare_address=True)
    childcare_street_line1 = applicant_childcare_address_record.street_line1
    childcare_street_line2 = applicant_childcare_address_record.street_line2
    childcare_town = applicant_childcare_address_record.town
    childcare_county = applicant_childcare_address_record.county
    childcare_postcode = applicant_childcare_address_record.postcode
    application = Application.objects.get(pk=application_id_local)

    previous_names = PreviousName.objects.filter(other_person_type=PERSON_TYPE, person_id=application_id_local)
    previous_addresses = get_stored_addresses(application_id_local, PERSON_TYPE)

    variables = {
        'form': form,
        'application_id': application_id_local,
        'first_name': first_name,
        'middle_names': middle_names,
        'last_name': last_name,
        'birth_day': birth_day,
        'birth_month': birth_month,
        'birth_year': birth_year,
        'street_line1': street_line1,
        'street_line2': street_line2,
        'town': town,
        'county': county,
        'postcode': postcode,
        'location_of_childcare': location_of_childcare,
        'childcare_street_line1': childcare_street_line1,
        'childcare_street_line2': childcare_street_line2,
        'childcare_town': childcare_town,
        'childcare_county': childcare_county,
        'childcare_postcode': childcare_postcode,
        'personal_details_status': application.personal_details_status,
        'previous_names': previous_names,
        'previous_addresses': previous_addresses,
    }

    try:
        previous_reg_details = PreviousRegistrationDetails.objects.get(application_id=application_id_local)
        variables['has_previously_applied'] = True
        variables['previous_registration'] = previous_reg_details.previous_registration
        variables['individual_id'] = str(previous_reg_details.individual_id)
        variables['five_years_in_UK'] = previous_reg_details.five_years_in_UK
    except:
        pass

    return render(request, 'childminder_templates/personal-details-summary.html', variables)


def add_applicant_previous_name(request):
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
            PreviousNamesFormset = modelformset_factory(PreviousName, form=OtherPersonPreviousNames)

            # Instantiate and populate it with post request details
            formset = PreviousNamesFormset(request.POST)
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
            # This scans the request post dictionary for a key submitted by clicking remove person
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
            PreviousNamesFormset = modelformset_factory(PreviousName, form=OtherPersonPreviousNames)
            formset = PreviousNamesFormset(request.POST)
            if formset.is_valid():
                formset.save()
                if referrer == 'None':
                    # If they've come from the 'add ebulk' button
                    return HttpResponseRedirect(build_url('personal_details_summary', get={'id': app_id}))
                else:
                    # If they've come from the summary page (using a change link)
                    return HttpResponseRedirect(build_url('personal_details_summary', get={'id': app_id}))
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
    if person_type == 'APPLICANT':
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
    PreviousNamesFormset = modelformset_factory(PreviousName, form=OtherPersonPreviousNames, extra=extra)
    formset = PreviousNamesFormset(initial=initial, queryset=initial_data)

    context = {
        'formset': formset,
        'application_id': app_id,
        'person_id': person_id,
        'person_type': person_type,
        'extra': extra,
        'referrer': referrer
    }

    return render(request, 'childminder_templates/add-previous-names.html', context)