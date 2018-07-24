from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from timeline_logger.models import TimelineLog

from ..summary_page_data import link_dict
from ..models import *
from .review import review, has_group
from ..decorators import group_required, user_assigned_application

"""
    to merge multiple models inside a table, represent them as a list within the ordered_models list.
    the get_summary_table method for these nested models should contain a key for each row called 'index',
    determining the order of the rows in the merged table
"""
ordered_models = [UserDetails, ChildcareType, [ApplicantPersonalDetails, ApplicantName, ApplicantHomeAddress],
                  FirstAidTraining, EYFS, HealthDeclarationBooklet, CriminalRecordCheck, Application,
                  AdultInHome, ChildInHome, Reference]

name_field_dict = {'Your email': 'email_address',
                   'Your mobile number': 'mobile_number',
                   'Other phone number': 'add_phone_number',
                   'Looking after 0 to 5 year olds?': None,
                   'Looking after 5 to 7 year olds? ': None,
                   'Looking after 8 year olds and older? ': None,
                   'Registers': None,
                   'Looking after children overnight?': None,
                   'Knowledge based question': 'security_question',
                   'Knowledge based answer': 'security_answer',
                   'What age groups will you be caring for?': 'childcare_age_groups',
                   'Are you providing overnight care?': 'overnight_care',
                   'Your name': 'name',
                   'Your date of birth': 'date_of_birth',
                   'Your home address': 'home_address',
                   'Childcare location': 'childcare_location',
                   'Training organisation': 'first_aid_training_organisation',
                   'first_aid_title': 'title_of_training_course',
                   'first_aid_date': 'course_date',
                   'Provide a Health Declaration Booklet?': 'health_submission_consent',
                   'DBS certificate number': 'dbs_certificate_number',
                   'Do you have any cautions or convictions?': 'cautions_convictions',
                   'Health check status': 'health_check_status',
                   'Name': 'full_name',
                   'Date of birth': 'date_of_birth',
                   'Relationship': 'relationship',
                   'Email': 'email',
                   #'Do you live with anyone who is 16 or over?': 'adults_in_home',
                   'Do you live with any children?': 'children_in_home',
                   'Full name': 'full_name',
                   'How they know you': 'relationship',
                   'Known for': 'time_known',
                   'Address': 'address',
                   'Phone number': 'phone_number',
                   'Email address': 'email_address',
                   'eyfs_title': 'eyfs_course_name',
                   'eyfs_date': 'eyfs_course_date',
                   'I will post a completed booklet to Ofsted': None,
                   'Do you have any criminal cautions or convictions?': 'cautions_convictions',
                   'Does anyone aged 16 or over live or work in your home?': 'adults_in_home',
                   }

@login_required
@group_required(settings.ARC_GROUP)
@user_assigned_application
def arc_summary(request):
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        json = load_json(application_id_local, ordered_models, False)
        json = add_comments(json, application_id_local)
        application_reference = Application.objects.get(pk=application_id_local).application_reference
        variables = {
            'json': json,
            'application_id': application_id_local,
            'application_reference': application_reference
        }
        return render(request, 'arc-summary.html', variables)
    elif request.method == 'POST':
        application_id_local = request.POST["id"]
        status = Arc.objects.get(pk=application_id_local)
        status.declaration_review = 'COMPLETED'
        status.save()
        return review(request)


@login_required
def cc_summary(request):
    cc_user = has_group(request.user, settings.CONTACT_CENTRE)

    if request.method == 'GET':
        application_id_local = request.GET["id"]
        application = Application.objects.get(pk=application_id_local)
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
        return render(request, 'search-summary.html', variables)
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
            for row in table[1:]:
                if 'pk' in row:
                    id = row['pk']
                name = row['name']

                #This check is added because the following phrases appear twice in rows (not unique).
                if name == 'Title of training course':
                    if "Early" in title:
                        field = name_field_dict['eyfs_title']
                    elif "First aid" in title:
                        field = name_field_dict['first_aid_title']
                    else:
                        field = None
                elif name == 'Date you completed course':
                    if "Early" in title:
                        field = name_field_dict['eyfs_date']
                    elif "First aid" in title:
                        field = name_field_dict['first_aid_date']
                    else:
                        field = None
                else:
                    field = name_field_dict[name]

                row['comment'] = get_comment(id, field)
                # row['comment'] = load_comment(lookup, id, name)
                row['link'] = reverse(label) + '?id=' + app_id
            row = row
    return json


def get_comment(pk, field):
    if ArcComments.objects.filter(table_pk=pk, field_name=field):
        arc = ArcComments.objects.get(table_pk=pk, field_name=field)
        if arc.flagged:
            return arc.comment
        else:
            return 'unflagged'
    else:
        return '    '


def load_json(application_id_local, ordered_models, recurse):
    """
    Dynamically builds a JSON to be consumed by the HTML summary page
    :param application_id_local: the id of the application being handled
    :param ordered_models: the models to be built for the summary page
    :param recurse: flag to indicate whether the method is currently recursing
    :return:
    """
    application = Application.objects.get(application_id=application_id_local)
    table_list = []
    for model in ordered_models:
        if isinstance(model, list):
            table_list.append(load_json(application_id_local, model, True))
        elif model == Application:
            table_list.append(application.get_summary_table_adult())
            table_list.append(application.get_summary_table_child())
        elif model.objects.filter(application_id=application).exists():
            records = model.objects.filter(application_id=application)
            for record in records:
                table = record.get_summary_table()
                if recurse:
                    table_list = table_list + table
                else:
                    table_list.append(table)

    if recurse:
        table_list = sorted(table_list, key=lambda k: k['index'])
    return table_list
