from django.urls import reverse
import logging

from ...models import *
from ...summary_page_data import link_dict

# Initiate logging
log = logging.getLogger('')

name_field_dict = {
    'Your email': 'email_address',
    'Your mobile number': 'mobile_number',
    'Other phone number': 'add_phone_number',
    'Knowledge based question': 'security_question',
    'Knowledge based answer': 'security_answer',
    'What age groups will you be caring for?': 'childcare_age_groups',
    'Are you providing overnight care?': 'overnight_care',
    'Your name': 'name',
    'Your date of birth': 'date_of_birth',
    'Your home address': 'home_address',
    'Childcare address': 'childcare_address',
    'Is this another childminder\'s home?': 'working_in_other_childminder_home',
    'Known to council social services?': 'own_children',
    'Training organisation': 'first_aid_training_organisation',
    'first_aid_training_course': 'title_of_training_course',
    'first_aid_date': 'course_date',
    'eyfs_course_name': 'eyfs_course_name',
    'eyfs_course_date': 'eyfs_course_date',
    'Provide a Health Declaration Booklet?': 'health_submission_consent',
    'DBS certificate number': 'dbs_certificate_number',
    'Known to council social services in regards to their own children?': 'known_to_council',
    'reasons_known_health_check': 'reasons_known_to_council_health_check',
    'Do you have any criminal cautions or convictions?': 'cautions_convictions',
    'Does anyone aged 16 or over live or work in your home?': 'adults_in_home',
    'Do children under 16 live in the home?': 'children_in_home',
    'known_personal_details': 'known_to_social_services',
    'reasons_known_personal_details': 'reasons_known_to_social_services',
    'Full name': 'full_name',
    'How they know you': 'relationship',
    'Known for': 'time_known',
    'address': 'address',
    'Phone number': 'phone_number',
    'Email address': 'email_address',
    'What type of childcare training have you completed?': 'childcare_training',
    'Have you lived outside of the UK in the last 5 years?': 'lived_abroad',
    'Have you lived or worked on a British military base outside of the UK in the last 5 years?': 'military_base',
    'British Military Base': 'military_base',
    'Ofsted DBS': 'capita',
    'Is it dated within the last 3 months?': 'within_three_months',
    'Is it an enhanced DBS check for home-based childcare?': 'enhanced_check',
    'Known to council social Services?': 'known_to_social_services',

    # PITH
    'Health questions status': 'health_check_status',
    'Name': 'full_name',
    'Date of birth': 'date_of_birth',
    'Relationship': 'relationship',
    'Email': 'email',
    'Phone number': 'PITH_mobile_number',
    'Lived abroad in the last 5 years?': 'lived_abroad',
    'Lived or worked in British military base in the last 5 years?': 'military_base',
    'Did they get their DBS check from the Ofsted DBS application website?': 'capita',
    'Enhanced DBS check for home-based childcare?': 'enhanced_check',
    'On the DBS Update Service?': 'on_update',
    'known_pith': 'known_to_social_services_pith',
    'reasons_known_pith': 'reasons_known_to_social_services_pith',

}

"""
    to merge multiple models inside a table, represent them as a list within the ordered_models list.
    the get_summary_table method for these nested models should contain a key for each row called 'index',
    determining the order of the rows in the merged table
"""


def add_comments(json, app_id):
    for table in json:
        if isinstance(table[0], list):
            add_comments(table, app_id)
        else:
            title_row = table[0]
            id = title_row['id']
            title = title_row['title']
            label = link_dict[title] if title in link_dict.keys() else 'other_people_summary'
            for row in table[1:]:
                if 'pk' in row:
                    id = row['pk']
                name = row['name']

                # This check is added because the following phrases appear twice in rows (not unique).
                if name == 'Title of training course':
                    if "Childcare training" in title:
                        field = name_field_dict.get('eyfs_course_name', '')
                    elif "First aid" in title:
                        field = name_field_dict.get('first_aid_training_course', '')

                elif name == 'Date you completed course':
                    if "Childcare training" in title:
                        field = name_field_dict.get('eyfs_course_date', '')
                    elif "First aid" in title:
                        field = name_field_dict.get('first_aid_date', '')

                elif name == 'Address':
                    if "reference" in title or title_row['id'] == 'Child':
                        field = name_field_dict.get('address', '')
                    else:
                        field = 'address' + str(id)

                elif name == 'Known to council social services in regards to your own children?':
                    if 'Your children' in title:
                        field = name_field_dict.get('known_personal_details', '')
                    elif "Your own children" in title:
                        field = name_field_dict.get('known_pith', '')

                elif name == 'Tell us why':
                    if 'Your children' in title:
                        field = name_field_dict.get('reasons_known_personal_details', '')
                    elif "Your own children" in title:
                        field = name_field_dict.get('reasons_known_pith', '')
                    else:
                        field = name_field_dict.get('reasons_known_health_check', '')

                else:
                    field = name_field_dict.get(name, '')

                row['comment'] = get_comment(id, field)
                row['link'] = reverse(label) + '?id=' + app_id
            row = row
    return json


def get_comment(pk, field):
    if ArcComments.objects.filter(table_pk=pk, field_name=field).exists():
        arc = ArcComments.objects.get(table_pk=pk, field_name=field)
        return arc.comment
    else:
        return ''


def get_bool_as_string(bool_field):
    if bool_field:
        return 'Yes'
    else:
        return 'No'


def get_address(street_line1, street_line2, town, postcode):
    return street_line1 + ', ' + street_line2 + ', ' + town + ', ' + postcode


def load_json(application_id_local, ordered_models, recurse, apply_filtering_for_eyc=False):
    """
    Dynamically builds a JSON to be consumed by the HTML summary page
    :param application_id_local: the id of the application being handled
    :param ordered_models: the models to be built for the summary page
    :param recurse: flag to indicate whether the method is currently recursing
    """

    application = Application.objects.get(application_id=application_id_local)
    table_list = []

    for model in ordered_models:

        if isinstance(model, list):

            table_list.append(load_json(application_id_local, model, True))

        elif model == ApplicantHomeAddress:

            # If personal address has not yet been supplied by the applicant, continue loop to avoid exception being
            # raised when fetching record
            if not ApplicantHomeAddress.objects.filter(application_id=application_id_local,
                                                       current_address=True).exists():
                continue

            home_address_record = ApplicantHomeAddress.objects.get(application_id=application_id_local,
                                                                   current_address=True)
            home_address_street_line1 = home_address_record.street_line1
            home_address_street_line2 = home_address_record.street_line2
            home_address_town = home_address_record.town
            home_address_postcode = home_address_record.postcode
            childcare_address_record = ApplicantHomeAddress.objects.get(application_id=application_id_local,
                                                                        childcare_address=True)
            childcare_address_street_line1 = childcare_address_record.street_line1
            childcare_address_street_line2 = childcare_address_record.street_line2
            childcare_address_town = childcare_address_record.town
            childcare_address_postcode = childcare_address_record.postcode
            working_in_other_childminder_home = Application.objects.get(
                application_id=application_id_local).working_in_other_childminder_home
            own_children = Application.objects.get(application_id=application_id_local).own_children
            reasons_known_to_social_services = Application.objects.get(
                application_id=application_id_local).reasons_known_to_social_services

            # If the home address is the same as the childcare address
            if home_address_record == childcare_address_record:
                home_address = get_address(home_address_street_line1, home_address_street_line2, home_address_town,
                                           home_address_postcode)
                childcare_address = 'Same as home address'
                table_list.append([
                    {"title": "Your home and childcare address", "id": application_id_local},
                    {"name": "Your home address", "value": home_address, 'pk': home_address_record.pk, "index": 1},
                    {"name": "Childcare address", "value": childcare_address, 'pk': childcare_address_record.pk,
                     "index": 2},
                    {"name": "Is this another childminder's home?",
                     "value": get_bool_as_string(working_in_other_childminder_home), 'pk': application_id_local,
                     "index": 5}
                ])

            # If the address is only a home address
            if home_address_record != childcare_address_record:
                home_address = get_address(home_address_street_line1, home_address_street_line2, home_address_town,
                                           home_address_postcode)
                childcare_address = get_address(childcare_address_street_line1, childcare_address_street_line2,
                                                childcare_address_town, childcare_address_postcode)
                table_list.append([
                    {"title": "Your home and childcare address", "id": application_id_local},
                    {"name": "Your home address", "value": home_address, 'pk': home_address_record.pk, "index": 1},
                    {"name": "Childcare address", "value": childcare_address, 'pk': childcare_address_record.pk,
                     "index": 2},
                    {"name": "Is this another childminder's home?",
                     "value": get_bool_as_string(working_in_other_childminder_home), 'pk': application_id_local,
                     "index": 3}
                ])

                if own_children:
                    log.debug("Add known to social services questions")
                    table_list.append([
                        {"title": "Your children", "id": application_id_local},
                        {"name": "Known to council social services?", "value": get_bool_as_string(own_children),
                         'pk': application_id_local, "index": 1},
                        {"name": "Tell us why", "value": reasons_known_to_social_services,
                         'pk': application_id_local, "index": 2}
                    ])
                else:
                    log.debug("Add known to social services question - not including tell us why")
                    table_list.append([
                        {"title": "Your children", "id": application_id_local},
                        {"name": "Known to council social services?", "value": get_bool_as_string(own_children),
                         'pk': application_id_local, "index": 1},
                    ])

        elif model == CriminalRecordCheck:

            # If criminal record details have not yet been supplied by the applicant, continue loop to avoid exception
            # being raised when fetching record
            if not CriminalRecordCheck.objects.filter(application_id=application_id_local).exists():
                continue

            criminal_record_check = CriminalRecordCheck.objects.get(application_id=application_id_local)
            table_list.append(criminal_record_check.get_summary_table())

            # Only show People in the home tables when applicant is not working in another childminder's home
            if application.working_in_other_childminder_home is False:
                log.debug("Conditional logic: Show people in the home table")
                table_list.append([
                    {"title": "Adults in the home", "id": application_id_local},
                    {"name": "Does anyone aged 16 or over live or work in your home?",
                     "value": 'Yes' if application.adults_in_home else 'No'}
                ])

        elif model == Application:

            # Only show People in the home tables when applicant is not working in another childminder's home
            if application.working_in_other_childminder_home is False:
                log.debug("Conditional logic: Show people in the home table")
                table_list.append(application.get_summary_table_child())

            # Only show People in the home tables when applicant is not working in another childminder's home
            if application.working_in_other_childminder_home is False:
                log.debug("Conditional logic: Show people in the home table")
                reasons_known_to_social_services_pith = Application.objects.get(
                    application_id=application_id_local).reasons_known_to_social_services_pith
                known_to_social_services_pith = Application.objects.get(
                    application_id=application_id_local).known_to_social_services_pith
                if application.own_children is False:
                    if known_to_social_services_pith is True:
                        log.debug("Add known to social services questions")
                        table_list.append([
                            {"title": "Your own children", "id": application_id_local},
                            {"name": "Known to council social services in regards to your own children?",
                             "value": get_bool_as_string(known_to_social_services_pith), "index": 1},
                            {"name": "Tell us why", "value": reasons_known_to_social_services_pith,
                             'pk': application_id_local, "index": 2}
                        ])
                    else:
                        log.debug("Add known to social services question - not tell us why")
                        table_list.append([
                            {"title": "Your own children", "id": application_id_local},
                            {"name": "Known to council social services in regards to your own children?",
                             "value": get_bool_as_string(known_to_social_services_pith)}
                        ])

        elif model == PreviousName:
            records = model.objects.filter(person_id=application.pk, other_person_type='APPLICANT')
            if len(records) != 0:
                log.debug("Conditional logic: Show previous names")
                previous_names = [{"title": "Previous names", "id": application_id_local}]
                for i, record in enumerate(records):
                    previous_names.extend(render_previous_name(record, i + 1))
                table_list.append(previous_names)

        elif model == PreviousAddress:
            unsorted_addresses = model.objects.filter(person_id=application.pk)
            records = sorted(unsorted_addresses, key=lambda addr: addr.order if addr.order else 0)

            if len(records) != 0:
                log.debug("Conditional logic: Show previous addresses")
                previous_addresses = [{"title": "Previous addresses", "id": application_id_local}]
                for index, record in enumerate(records):
                    previous_addresses.extend(render_previous_address(record, index + 1))

                table_list.append(previous_addresses)

        elif model == AdultInHome:
            records = model.objects.filter(application_id=application.pk)
            for record in records:
                table = record.get_summary_table(apply_filtering_for_eyc=apply_filtering_for_eyc)
                if recurse:
                    table_list = table_list + table
                else:
                    table_list.append(table)

                prev_names_addresses_table = record.get_previous_names_and_addresses_summary_table()
                if prev_names_addresses_table is not None:
                    if recurse:
                        table_list = table_list + prev_names_addresses_table
                    else:
                        table_list.append(prev_names_addresses_table)

        elif model.objects.filter(application_id=application.pk).exists():
            records = model.objects.filter(application_id=application.pk)
            for record in records:
                table = record.get_summary_table()
                if recurse:
                    table_list = table_list + table
                else:
                    table_list.append(table)

    if recurse:
        table_list = sorted(table_list, key=lambda k: k['index'])
    return table_list


def render_previous_name(previous_name_record, index):
    return [
        {"name": "Previous name {}".format(index),
         "value": previous_name_record.get_name()},
        {"name": "Start date",
         "value": previous_name_record.start_date.strftime('%d %B %Y') if previous_name_record.start_date else ''},
        {"name": "End date",
         "value": previous_name_record.end_date.strftime('%d %B %Y') if previous_name_record.end_date else ''},
    ]


def render_previous_address(previous_address_record, index):
    address = get_address(previous_address_record.street_line1,
                          previous_address_record.street_line2, previous_address_record.town,
                          previous_address_record.postcode)
    return [
        {"name": "Previous address {}".format(index),
         "value": address},
        {"name": "Moved in date",
         "value": previous_address_record.moved_in_date.strftime(
             '%d %B %Y') if previous_address_record.moved_in_date else ''},
        {"name": "Moved out date",
         "value": previous_address_record.moved_out_date.strftime('%d %B %Y') if previous_address_record.moved_out_date else ''},
    ]


def get_application_summary_variables(application_id, apply_filtering_for_eyc=False):
    """
    A function for generating the summary page contents in the ARC view. Note that this is re-used by the
    document generation function so changes will be applied in both the UI and PDF exports.
    :param application_id: the unique identifier of the application
    :param apply_filtering_for_eyc: a filter flag to exclude fields that should not appear in an EYC form
    :return: a variables object for use in Django templates including all application information
    (and similarly EYC form contents).
    """

    ordered_models = [UserDetails, ChildcareType, [ApplicantPersonalDetails, ApplicantName], PreviousName,
                      ApplicantHomeAddress, PreviousAddress, PreviousRegistrationDetails,
                      FirstAidTraining, ChildcareTraining, CriminalRecordCheck]

    # Only display People in your Home tables if the applicant does not work in another childminder's home
    application = Application.objects.get(application_id=application_id)

    if application.working_in_other_childminder_home is False:
        log.debug("Conditional logic: Show people in the home tables")
        ordered_models.append(AdultInHome)
        ordered_models.append(Application)
        ordered_models.append(ChildInHome)
    zero_to_five = ChildcareType.objects.get(application_id=application_id).zero_to_five

    if zero_to_five:
        log.debug("Conditional logic: Show health declaration and reference")
        ordered_models.insert(7, HealthDeclarationBooklet)
        ordered_models.append(Reference)
    json = load_json(application_id, ordered_models, False, apply_filtering_for_eyc=apply_filtering_for_eyc)
    json = add_comments(json, application_id)

    application_reference = application.application_reference
    publish_details = application.publish_details

    variables = {
        'json': json,
        'application_id': application_id,
        'application_reference': application_reference,
        'publish_details': publish_details
    }

    return variables
