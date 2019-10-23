import logging
import datetime

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render

from ...decorators import group_required, user_assigned_application
from ...models import ApplicantPersonalDetails, ApplicantName, ApplicantHomeAddress, Arc, Application, PreviousName
from ...review_util import request_to_comment, save_comments, redirect_selection
from ...views.childminder_views.personal_details_addresses import get_stored_addresses, update_applicant_current_address
from ...forms.childminder_forms.form import PersonalDetailsForm, PreviousRegistrationDetails

log = logging.getLogger()


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

    def show_your_children_table(home_record, childcare_record):
        return home_record != childcare_record

    application_id_local = request.GET["id"]
    application_record = Application.objects.get(application_id=application_id_local)
    personal_details_record = ApplicantPersonalDetails.objects.get(application_id=application_id_local)
    name_record = ApplicantName.objects.get(personal_detail_id=personal_details_record)
    home_address_record = ApplicantHomeAddress.objects.get(personal_detail_id=personal_details_record,
                                                           current_address=True)
    childcare_address_record = ApplicantHomeAddress.objects.get(personal_detail_id=personal_details_record,
                                                                childcare_address=True)

    TABLE_NAMES = ['APPLICANT_PERSONAL_DETAILS', 'APPLICANT_NAME', 'APPLICANT_HOME_ADDRESS', 'APPLICATION']
    PERSONAL_DETAIL_FIELDS = ['date_of_birth_declare', 'date_of_birth_comments']
    NAME_FIELDS = ['name_declare', 'name_comments']
    HOME_ADDRESS_FIELDS = ['home_address_declare', 'home_address_comments']
    CHILDCARE_ADDRESS_FIELDS = ['childcare_address_declare', 'childcare_address_comments']
    WORKING_IN_OTHER_CHILDMINDER_HOME_FIELDS = ['working_in_other_childminder_home_declare',
                                                'working_in_other_childminder_home_comments']
    OWN_CHILDREN_FIELDS = ['own_children_declare', 'own_children_comments', 'reasons_known_to_social_services_declare',
                           'reasons_known_to_social_services_comments']
    REASONS_KNOWN_TO_SOCIAL_SERVICES_FIELDS = ['reasons_known_to_social_services_declare',
                                               'reasons_known_to_social_services_comments']
    PERSON_TYPE = 'APPLICANT'

    if request.method == 'GET':

        form = PersonalDetailsForm(table_keys=[personal_details_record.pk, name_record.pk, home_address_record.pk,
                                               childcare_address_record.pk, application_id_local])

    elif request.method == 'POST':

        form = PersonalDetailsForm(request.POST,
                                   table_keys=[personal_details_record.pk, name_record.pk, home_address_record.pk,
                                               childcare_address_record.pk, application_id_local])
        if form.is_valid():

            birthdate_dict = {}
            name_dict = {}
            home_address_dict = {}
            childcare_address_dict = {}
            working_in_other_childminder_home_dict = {}
            own_children_dict = {}
            reasons_known_to_social_services_dict = {}

            # Populate field dictionaries for use in request to comment function
            # As the data required on this form is stored in different tables, these must be sorted by table
            for field in form.cleaned_data:
                if field in PERSONAL_DETAIL_FIELDS:
                    birthdate_dict[field] = form.cleaned_data[field]
                if field in NAME_FIELDS:
                    name_dict[field] = form.cleaned_data[field]
                if field in HOME_ADDRESS_FIELDS:
                    home_address_dict[field] = form.cleaned_data[field]
                if field in CHILDCARE_ADDRESS_FIELDS:
                    childcare_address_dict[field] = form.cleaned_data[field]
                if field in WORKING_IN_OTHER_CHILDMINDER_HOME_FIELDS:
                    working_in_other_childminder_home_dict[field] = form.cleaned_data[field]
                if field in OWN_CHILDREN_FIELDS:
                    own_children_dict[field] = form.cleaned_data[field]
                if field in REASONS_KNOWN_TO_SOCIAL_SERVICES_FIELDS:
                    reasons_known_to_social_services_dict[field] = form.cleaned_data[field]

            # Populate below lists with comments by table
            birthdate_comments = request_to_comment(personal_details_record.pk, TABLE_NAMES[0], birthdate_dict)
            name_comments = request_to_comment(name_record.pk, TABLE_NAMES[1], name_dict)
            home_address_comments = request_to_comment(home_address_record.pk, TABLE_NAMES[2], home_address_dict)
            childcare_address_comments = request_to_comment(childcare_address_record.pk, TABLE_NAMES[2],
                                                            childcare_address_dict)
            working_in_other_childminder_home_comments = request_to_comment(application_id_local, TABLE_NAMES[3],
                                                                            working_in_other_childminder_home_dict)
            own_children_comments = request_to_comment(application_id_local, TABLE_NAMES[3], own_children_dict)
            reasons_known_to_social_services_comments = request_to_comment(application_id_local, TABLE_NAMES[3],
                                                                           own_children_dict)

            birthdate_save_successful = save_comments(request, birthdate_comments)
            name_save_successful = save_comments(request, name_comments)
            home_address_save_successful = save_comments(request, home_address_comments)
            childcare_address_save_successful = save_comments(request, childcare_address_comments)
            working_in_other_childminder_home_save_successful = save_comments(
                request, working_in_other_childminder_home_comments)
            own_children_save_successful = save_comments(request, own_children_comments)
            reasons_known_to_social_services_save_successful = save_comments(
                request, reasons_known_to_social_services_comments)

            if not all((birthdate_save_successful, name_save_successful, home_address_save_successful,
                        childcare_address_save_successful, working_in_other_childminder_home_save_successful,
                        own_children_save_successful, reasons_known_to_social_services_save_successful)):
                log.debug("Handling submissions for personal details - save unsuccessful")
                return render(request, '500.html')

            # update application status
            if not any((birthdate_comments, name_comments, home_address_comments, childcare_address_comments,
                        working_in_other_childminder_home_comments, own_children_comments,
                        reasons_known_to_social_services_comments)):
                section_status = 'COMPLETED'
                application_record.personal_details_arc_flagged = False
            else:
                section_status = 'FLAGGED'
                application_record.personal_details_arc_flagged = True

            application_record.save()

            # calculate start and end dates of applicant's current name
            try:
                # fetch previous name with most recent end date (must actually have an end date)
                last_prv_name = PreviousName.objects.filter(
                                        person_id=application_id_local, other_person_type=PERSON_TYPE,
                                        end_day__isnull=False, end_month__isnull=False, end_year__isnull=False)\
                                        .order_by('-end_year', '-end_month', '-end_day')[0]
            except IndexError:
                last_prv_name = None

            name_record.start_day = last_prv_name.end_day if last_prv_name else personal_details_record.birth_day
            name_record.start_month = last_prv_name.end_month if last_prv_name else personal_details_record.birth_month
            name_record.start_year = last_prv_name.end_year if last_prv_name else personal_details_record.birth_year
            today = datetime.date.today()
            name_record.end_day = today.day
            name_record.end_month = today.month
            name_record.end_year = today.year
            name_record.save()

            update_applicant_current_address(application_id_local)

            # update arc status
            arc_record = Arc.objects.get(pk=application_id_local)
            arc_record.personal_details_review = section_status
            arc_record.save()

            redirect_link = redirect_selection(request, '/first-aid/summary/')
            log.debug("Handling submissions for personal details - save successful")
            return HttpResponseRedirect(settings.URL_PREFIX + redirect_link + '?id=' + application_id_local)

    previous_names = PreviousName.objects.filter(other_person_type=PERSON_TYPE, person_id=application_id_local)\
                                 .order_by('order')
    previous_addresses = get_stored_addresses(application_id_local, PERSON_TYPE)
    try:
        previous_reg_details = PreviousRegistrationDetails.objects.get(application_id=application_id_local)
    except PreviousRegistrationDetails.DoesNotExist:
        previous_reg_details = None

    form.error_summary_title = 'There was a problem'

    variables = {
        'form': form,
        'application_id': application_id_local,
        'full_name': name_record.full_name,
        'date_of_birth': personal_details_record.date_of_birth,
        'street_line1': home_address_record.street_line1,
        'street_line2': home_address_record.street_line2,
        'town': home_address_record.town,
        'county': home_address_record.county,
        'postcode': home_address_record.postcode,
        'location_of_childcare': childcare_address_record.current_address,
        'childcare_street_line1': childcare_address_record.street_line1,
        'childcare_street_line2': childcare_address_record.street_line2,
        'childcare_town': childcare_address_record.town,
        'childcare_county': childcare_address_record.county,
        'childcare_postcode': childcare_address_record.postcode,
        'personal_details_status': application_record.personal_details_status,
        'previous_names': previous_names,
        'previous_addresses': previous_addresses,
        'own_children': application_record.own_children,
        'reasons_known_to_social_services': application_record.reasons_known_to_social_services,
        'working_in_other_childminder_home': application_record.working_in_other_childminder_home,
        'show_your_children_table': show_your_children_table(home_address_record, childcare_address_record),
    }

    if name_record.title != '':
        variables.update({'title': name_record.title})

    if previous_reg_details is not None:
        log.debug("Conditional logic: Show previous registration details")
        variables.update({
            'has_previously_applied': True,
            'previous_registration': previous_reg_details.previous_registration,
            'individual_id': previous_reg_details.individual_id,
            'five_years_in_UK': previous_reg_details.five_years_in_UK,
        })

    log.debug("Render personal details page")
    return render(request, 'childminder_templates/personal-details-summary.html', variables)
