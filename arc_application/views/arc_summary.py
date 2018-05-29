from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from timeline_logger.models import TimelineLog

from ..summary_page_data import link_dict
from ..models import *
from .review import review, has_group

"""
    to merge multiple models inside a table, represent them as a list within the ordered_models list.
    the get_summary_table method for these nested models should contain a key for each row called 'index',
    determining the order of the rows in the merged table
"""
ordered_models = [UserDetails, ChildcareType, [ApplicantPersonalDetails, ApplicantName, ApplicantHomeAddress],
                  FirstAidTraining, EYFS, HealthDeclarationBooklet, CriminalRecordCheck, Application,
                  AdultInHome, ChildInHome, Reference]


def arc_summary(request):
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        json = load_json(application_id_local, ordered_models, False)
        json = add_comments(json, application_id_local)
        variables = {
            'json': json,
            'application_id': application_id_local
        }
        return render(request, 'arc-summary.html', variables)
    elif request.method == 'POST':
        application_id_local = request.POST["id"]
        status = Arc.objects.get(pk=application_id_local)
        status.declaration_review = 'COMPLETED'
        status.save()
        return review(request)


def cc_summary(request):
    cc_user = has_group(request.user, settings.CONTACT_CENTRE)
    arc_user = has_group(request.user, settings.ARC_GROUP)

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
                field = name_converter(name)
                row['comment'] = get_comment(id, field)
                # row['comment'] = load_comment(lookup, id, name)
                row['link'] = reverse(label) + '?id=' + app_id
            row = row
    return json


def name_converter(name):
    field_list = ['email_address', 'mobile_number', 'add_phone_number', 'security_question', 'security_answer',
                  'childcare_age_groups', 'overnight_care',
                  'name', 'date_of_birth', 'home_address', 'childcare_location',
                  'first_aid_training_organisation', 'title_of_training_course', 'course_date',
                  'health_submission_consent',
                  'dbs_certificate_number', 'cautions_convictions',
                  'full_name', 'date_of_birth', 'relationship', 'dbs_certificate_number', 'permission',
                  'adults_in_home',
                  'children_in_home',
                  'full_name', 'relationship', 'time_known', 'address', 'phone_number', 'email_address',
                  'eyfs_course_name', 'eyfs_course_date'
                  ]

    name_list = ['Your email', 'Your mobile number', 'Other phone number', 'Knowledge based question',
                 'Knowledge based answer',
                 'What age groups will you be caring for?', 'Are you providing overnight care?',
                 'Your name', 'Your date of birth', 'Home address', 'Childcare location',
                 'First aid training provider', 'Title of first aid course', 'Date of first aid certificate',
                 'Provide a Health Declaration Booklet?',
                 'DBS certificate number', 'Do you have any cautions or convictions?',
                 'Name', 'Date of birth', 'Relationship', 'DBS certificate number',
                 'Permission for checks',
                 'Do you live with anyone who is 16 or over?',
                 'Do you live with any children?',
                 'Full name', 'How they know you', 'Known for', 'Address', 'Phone number', 'Email address',
                 'Title of training course', 'Date you completed course'
                 ]
    for i in range(len(name_list)):
        if name in name_list[i]:
            return field_list[i]


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
