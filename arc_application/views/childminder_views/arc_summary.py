from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from timeline_logger.models import TimelineLog

from arc_application.summary_page_data import link_dict
from arc_application.models import *
from .review import review, has_group
from arc_application.decorators import group_required, user_assigned_application

"""
    to merge multiple models inside a table, represent them as a list within the ordered_models list.
    the get_summary_table method for these nested models should contain a key for each row called 'index',
    determining the order of the rows in the merged table
"""

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
    'Do you have children of your own under 16?': 'own_children',
    'Training organisation': 'first_aid_training_organisation',
    'first_aid_training_course': 'title_of_training_course',
    'first_aid_date': 'course_date',
    'eyfs_course_name': 'eyfs_course_name',
    'eyfs_course_date': 'eyfs_course_date',
    'Provide a Health Declaration Booklet?': 'health_submission_consent',
    'DBS certificate number': 'dbs_certificate_number',
    'Do you have any criminal cautions or convictions?': 'cautions_convictions',
    'Health questions status': 'health_check_status',
    'Name': 'full_name',
    'Date of birth': 'date_of_birth',
    'Relationship': 'relationship',
    'Email': 'email',
    'Does anyone aged 16 or over live or work in your home?': 'adults_in_home',
    'Do children under 16 live in the home?': 'children_in_home',
    'Do you have children of your own under 16 who do not live with you?': 'own_children_not_in_home',
    'Full name': 'full_name',
    'How they know you': 'relationship',
    'Known for': 'time_known',
    'address': 'address',
    'Phone number': 'phone_number',
    'Email address': 'email_address',
    'What type of childcare training have you completed?': 'childcare_training',
    'Have you lived outside of the UK in the last 5 years?': 'lived_abroad',
    'Have you lived or worked on a British military base outside of the UK in the last 5 years?': 'military_base',
    'Do you have an Ofsted DBS Check?': 'capita',
    'Are you on the DBS update service?': 'on_update',
    'Which of your children live with you?': 'children_living_with_childminder_selection'
}


@login_required
@group_required(settings.ARC_GROUP)
@user_assigned_application
def arc_summary(request):
    ordered_models = [UserDetails, ChildcareType, [ApplicantPersonalDetails, ApplicantName], ApplicantHomeAddress,
                      FirstAidTraining, ChildcareTraining, CriminalRecordCheck]

    if request.method == 'GET':
        application_id_local = request.GET["id"]
        # Only display People in your Home tables if the applicant does not work in another childminder's home
        application = Application.objects.get(application_id=application_id_local)

        if application.working_in_other_childminder_home is False:
            ordered_models.append(AdultInHome)
            ordered_models.append(Application)
            ordered_models.append(ChildInHome)
            ordered_models.append(Child)
        zero_to_five = ChildcareType.objects.get(application_id=application_id_local).zero_to_five

        if zero_to_five:
            ordered_models.insert(6, HealthDeclarationBooklet)
            ordered_models.append(Reference)
        json = load_json(application_id_local, ordered_models, False)
        json = add_comments(json, application_id_local)
        application_reference = Application.objects.get(pk=application_id_local).application_reference
        variables = {
            'json': json,
            'application_id': application_id_local,
            'application_reference': application_reference
        }
        return render(request, 'childminder_templates/arc-summary.html', variables)

    elif request.method == 'POST':
        application_id_local = request.POST["id"]
        status = Arc.objects.get(pk=application_id_local)
        status.declaration_review = 'COMPLETED'
        status.save()
        return review(request)


@login_required
def cc_summary(request):
    ordered_models = [UserDetails, ChildcareType, [ApplicantPersonalDetails, ApplicantName], ApplicantHomeAddress,
                      FirstAidTraining, ChildcareTraining, CriminalRecordCheck]
    cc_user = has_group(request.user, settings.CONTACT_CENTRE)

    if request.method == 'GET':
        application_id_local = request.GET["id"]
        # Only display People in your Home tables if the applicant does not work in another childminder's home
        application = Application.objects.get(application_id=application_id_local)
        if application.working_in_other_childminder_home is False:
            ordered_models.append(AdultInHome)
            ordered_models.append(Application)
            ordered_models.append(ChildInHome)
            ordered_models.append(Child)
        zero_to_five = ChildcareType.objects.get(application_id=application_id_local).zero_to_five
        if zero_to_five:
            ordered_models.insert(6, HealthDeclarationBooklet)
            ordered_models.append(Reference)
        json = load_json(application_id_local, ordered_models, False)
        json[0][1]['link'] = (reverse('update_email') + '?id=' + str(application_id_local))
        json[0][2]['link'] = (reverse('update_phone_number') + '?id=' + str(application_id_local))
        json[0][3]['link'] = (reverse('update_add_number') + '?id=' + str(application_id_local))
        user_type = 'contact center' if cc_user else 'reviewer'
        TimelineLog.objects.create(
            content_object=application,
            user=request.user,
            template='timeline_logger/application_action_contact_center.txt',
            extra_data={'user_type': user_type, 'entity': 'application', 'action': "viewed"}
        )

        variables = {
            'json': json,
            'application_id': application_id_local,
            'application_reference': application.application_reference or None,
            'cc_user': cc_user
        }
        return render(request, 'childminder_templates/search-summary.html', variables)

    elif request.method == 'POST':
        application_id_local = request.POST["id"]
        status = Arc.objects.get(pk=application_id_local)
        status.declaration_review = 'COMPLETED'
        status.save()
        return HttpResponseRedirect(settings.URL_PREFIX + '/comments?id=' + application_id_local)


def add_comments(json, app_id):
    for table in json:
        if isinstance(table[0], list):
            add_comments(table, app_id)
        else:
            title_row = table[0]
            id = title_row['id']
            title = title_row['title']
            label = link_dict[title] if title in link_dict.keys() else 'other_people_summary'
            if id == 'Child':
                label = 'your_children_summary'
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


def load_json(application_id_local, ordered_models, recurse):
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
                     "index": 5},
                    {"name": "Do you have children of your own under 16?", "value": get_bool_as_string(own_children),
                     'pk': application_id_local, "index": 6}
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

                table_list.append([
                    {"title": "Your children", "id": application_id_local},
                    {"name": "Do you have children of your own under 16?", "value": get_bool_as_string(own_children),
                     'pk': application_id_local, "index": 1}
                ])

                # Create a table for Your children's addresses
                children_living_with_childminder = Child.objects.filter(application_id=application_id_local,
                                                                        lives_with_childminder=True).order_by('child')
                children = []

                for child in children_living_with_childminder:
                    children.append(child.get_full_name())

                children_string = ', '.join(children)

                table_list.append([
                    {"title": "Your children's addresses", "id": application_id_local},
                    {"name": "Which of your children live with you?", "value": children_string,
                     'pk': application_id_local, "index": 1}
                ])
                # Create tables for each child
                all_children = Child.objects.filter(application_id=application_id_local).order_by('child')
                for child in all_children:
                    name = child.get_full_name()
                    if child.birth_day < 10:
                        birth_day = '0' + str(child.birth_day)
                    else:
                        birth_day = str(child.birth_day)
                    if child.birth_month < 10:
                        birth_month = '0' + str(child.birth_month)
                    else:
                        birth_month = str(child.birth_month)
                    date_of_birth = birth_day + ' ' + birth_month + ' ' + str(child.birth_year)

                    child_address_record = ChildAddress.objects.get(application_id=application_id_local,
                                                                    child=child.child)
                    child_address = get_address(child_address_record.street_line1,
                                                child_address_record.street_line2, child_address_record.town,
                                                child_address_record.postcode)

                    table_list.append([
                        {"title": name, "id": "Child"},
                        {"name": "Name", "value": name, 'pk': child.pk, "index": 1},
                        {"name": "Date of birth", "value": date_of_birth, 'pk': child.pk, "index": 2},
                        {"name": "Address", "value": child_address, 'pk': child_address_record.pk, "index": 3}
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

                if application.adults_in_home is True:

                    adults_in_home = 'Yes'

                else:

                    adults_in_home = 'False'

                table_list.append([
                    {"title": "Adults in the home", "id": application_id_local},
                    {"name": "Does anyone aged 16 or over live or work in your home?",
                     "value": adults_in_home}
                ])

        elif model == Application:

            # Only show People in the home tables when applicant is not working in another childminder's home
            if application.working_in_other_childminder_home is False:

                table_list.append(application.get_summary_table_child())

        elif model == Child:

            # Only show People in the home tables when applicant is not working in another childminder's home
            if application.working_in_other_childminder_home is False:

                if application.own_children is False:

                    table_list.append([
                        {"title": "Children not in the home", "id": application_id_local},
                        {"name": "Do you have children of your own under 16 who do not live with you?",
                         "value": application.own_children_not_in_home}
                    ])

                    children_not_in_home = Child.objects.filter(application_id=application_id_local,
                                                                lives_with_childminder=False)

                    for child in children_not_in_home:

                        if child.birth_day < 10:
                            birth_day = '0' + str(child.birth_day)
                        else:
                            birth_day = str(child.birth_day)

                        if child.birth_month < 10:
                            birth_month = '0' + str(child.birth_month)
                        else:
                            birth_month = str(child.birth_month)

                        date_of_birth = birth_day + ' ' + birth_month + ' ' + str(child.birth_year)

                        child_address_record = ChildAddress.objects.get(application_id=application_id_local,
                                                                        child=child.child)

                        child_address = get_address(child_address_record.street_line1,
                                                    child_address_record.street_line2, child_address_record.town,
                                                    child_address_record.postcode)

                        table_list.append([
                            {"title": child.get_full_name(), "id": child.pk},
                            {"name": "Name", "value": child.get_full_name()},
                            {"name": "Date of birth", "value": date_of_birth},
                            {"name": "Address", "value": child_address}
                        ])

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
