from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from timeline_logger.models import TimelineLog

from ..summary_page_data import link_dict
from ..models import *


def arc_summary(request):
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        json = load_json(application_id_local)
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
        return HttpResponseRedirect(settings.URL_PREFIX + '/comments?id=' + application_id_local)


def cc_summary(request):
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        json = load_json(application_id_local)
        TimelineLog.objects.create(
            content_object=Application.objects.get(pk=application_id_local),
            user=request.user,
            template='timeline_logger/application_action_contact_center.txt',
            extra_data={'user_type': 'contact center', 'entity': 'application', 'action': "viewed"}
        )

        variables = {
            'json': json,
            'application_id': application_id_local
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
        title_row = table[0]
        id = title_row['id']
        label = link_dict[title_row['title']]
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
                  'dbs_certificate_number', 'dbs_submission_consent',
                  'full_name', 'date_of_birth', 'relationship', 'dbs_certificate_number', 'permission',
                  'adults_in_home',
                  'children_in_home',
                  'full_name', 'relationship', 'time_known', 'address', 'phone_number', 'email_address'

                  ]

    name_list = ['Your email', 'Mobile phone number', 'Alternative phone number', 'Knowledge based question',
                 'Knowledge based answer',
                 'What age groups will you be caring for?', 'Are you providing overnight care?',
                 'Your name', 'Your date of birth', 'Home address', 'Childcare location',
                 'First aid training provider', 'Your first aid certificate', 'Date of first aid certificate',
                 'Provide a Health Declaration Booklet?',
                 'DBS certificate number', 'Do you have any cautions or convictions?',
                 'Name', 'Date of birth', 'Relationship', 'DBS certificate number',
                 'Permission for checks',
                 'Do you live with anyone who is 16 or over?',
                 'Do you live with any children?',
                 'Full name', 'How they know you', 'Known for', 'Address', 'Phone number', 'Email address'
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


def load_json(application_id_local):
    application = Application.objects.get(application_id=application_id_local)

    login_details_table = load_login_details(application)

    childcare_type_table = load_childcare_type(application)

    personal_detail_table = load_personal_detail_table(application)

    first_aid_table = load_first_aid(application)

    criminal_record_table = load_criminal_record(application)

    health_check_table = load_health_check(application)

    first_reference_table = load_reference(application, 1)

    second_reference_table = load_reference(application, 2)

    adult_home_table = load_adult_home(application)

    child_home_table = load_child_home(application)

    table_list = [login_details_table, childcare_type_table, personal_detail_table, first_aid_table, criminal_record_table,
            health_check_table, first_reference_table, second_reference_table, adult_home_table, child_home_table]
    l = []
    for i in table_list:
        if not i:
            pass
        else:
            l.append(i)
    return l


def load_login_details(app):
    if UserDetails.objects.filter(application_id=app).exists():
        login_record = UserDetails.objects.get(application_id=app)
        table = [
            {"title": "Your login details", "id": login_record.pk},
            {"name": "Your email", "value": login_record.email},
            {"name": "Mobile phone number", "value": login_record.mobile_number},
            {"name": "Alternative phone number", "value": login_record.add_phone_number},
            {"name": "Knowledge based question", "value": login_record.security_question},
            {"name": "Knowledge based answer", "value": login_record.security_question}

        ]
        return table
    return False


def load_childcare_type(app):
    if ChildcareType.objects.filter(application_id=app).exists():
        childcare_record = ChildcareType.objects.get(application_id=app)
        zero_to_five = childcare_record.zero_to_five
        five_to_eight = childcare_record.five_to_eight
        eight_plus = childcare_record.eight_plus
        register = ''
        if zero_to_five and five_to_eight or zero_to_five and not five_to_eight and eight_plus:
            register = 'Early Years Register, Childcare Register'
        if not zero_to_five and five_to_eight and eight_plus:
            register = 'Childcare Register (compulsory & voluntary parts)'
        if zero_to_five and not five_to_eight and not eight_plus:
            register = 'Early Years Register'
        if not zero_to_five and five_to_eight and not eight_plus:
            register = 'Childcare Register (compulsory part)'
        if not zero_to_five and not five_to_eight and eight_plus:
            register = 'Childcare Register (voluntary part)'

        table = [
            {"title": "Childcare Type", "id": childcare_record.pk},
            {"name": "Looking after 0 to 5 year olds?", "value": childcare_record.zero_to_five},
            {"name": "Looking after 5 to 7 year olds? ", "value": childcare_record.five_to_eight},
            {"name": "Looking after 8 year olds and older? ", "value": childcare_record.eight_plus},
            {"name": "Registers", "value": register}
        ]
        return table
    return False


def load_personal_detail_table(app):
    if ApplicantName.objects.filter(application_id=app).exists():
        applicant_name_record = ApplicantName.objects.get(application_id=app)

        if ApplicantPersonalDetails.objects.filter(application_id=app).exists():
            applicant_record = ApplicantPersonalDetails.objects.get(application_id=app)

            if ApplicantHomeAddress.objects.filter(application_id=app).exists():
                applicant_home_address_record = ApplicantHomeAddress.objects.get(application_id=app)
                home_address = applicant_home_address_record.street_line1 + ', ' + applicant_home_address_record.street_line2 \
                               + ', ' + applicant_home_address_record.town + ', ' + applicant_home_address_record.postcode

                table = [
                    {"title": "Your personal details", "id": applicant_record.personal_detail_id},
                    {"name": "Your name",
                     "value": applicant_name_record.first_name + ' ' + applicant_name_record.middle_names + ' ' + applicant_name_record.last_name,
                     'pk': applicant_name_record.pk},
                    {"name": "Your date of birth",
                     "value": str(applicant_record.birth_day) + '/' + str(applicant_record.birth_month) + '/' + str(
                         applicant_record.birth_year), 'pk': applicant_record.pk},
                    {"name": "Home address", "value": home_address, 'pk': applicant_home_address_record.pk},
                    {"name": "Childcare location", "value": "Same as home address",
                     'pk': applicant_home_address_record.pk}
                ]
                return table
    return False


def load_first_aid(app):
    if FirstAidTraining.objects.filter(application_id=app).exists():
        first_aid_record = FirstAidTraining.objects.get(application_id=app)

        table = [
            {"title": "Your first aid certificate", "id": first_aid_record.pk},
            {"name": "First aid training provider", "value": first_aid_record.training_organisation},
            {"name": "Title of first aid course", "value": first_aid_record.course_title},
            {"name": "Date of first aid certificate",
             "value": str(first_aid_record.course_day) + '/' + str(first_aid_record.course_month) + '/' + str(
                 first_aid_record.course_year)}
        ]
        return table
    return False


def load_criminal_record(app):
    if CriminalRecordCheck.objects.filter(application_id=app).exists():
        dbs_record = CriminalRecordCheck.objects.get(application_id=app)

        table = [
            {"title": "Criminal record checks", "id": dbs_record.pk},
            {"name": "DBS certificate number", "value": dbs_record.dbs_certificate_number},
            {"name": "Do you have any cautions or convictions?", "value": dbs_record.cautions_convictions}
        ]
        return table
    return False


def load_health_check(app):
    if HealthDeclarationBooklet.objects.filter(application_id=app).exists():
        hdb_record = HealthDeclarationBooklet.objects.get(application_id=app)

        table = [
        {"title": "Health checks", "id": hdb_record.pk},
        {"name": "Provide a Health Declaration Booklet?", "value": hdb_record.send_hdb_declare}
    ]
        return table
    return False


def load_reference(app, num):
    if Reference.objects.filter(application_id=app, reference=num).exists():
        first_reference_record = Reference.objects.get(application_id=app, reference=num)
        ref1_address = first_reference_record.street_line1 + ', ' + first_reference_record.street_line2 + ', ' + first_reference_record.town + ', ' + first_reference_record.postcode
        if num == 1:
            ref_num = 'First'
        if num == 2:
            ref_num = 'Second'
        table = [
        {"title": ref_num +" reference", "id": first_reference_record.pk},
        {"name": "Full name", "value": first_reference_record.first_name + ' ' + first_reference_record.last_name},
        {"name": "How they know you", "value": first_reference_record.relationship},
        {"name": "Known for", "value": str(first_reference_record.months_known) + ' months, ' + str(
            first_reference_record.years_known) + ' years'},
        {"name": "Address", "value": ref1_address},
        {"name": "Phone number", "value": first_reference_record.phone_number},
        {"name": "Email address", "value": first_reference_record.email}

    ]
        return table
    return False


def load_adult_home(app):
    if UserDetails.objects.filter(application_id=app).exists():
        login_record = UserDetails.objects.get(application_id=app)

        table = [
        {"title": "Adults in your home", "id": login_record.pk},
        {"name": "Do you live with anyone who is 16 or over?", "value": app.adults_in_home}
    ]
        return table
    return False


def load_child_home(app):
    if UserDetails.objects.filter(application_id=app).exists():
        login_record = UserDetails.objects.get(application_id=app)

        table = [
        {"title": "Children in your home", "id": login_record.pk},
        {"name": "Do you live with any children?", "value": app.children_in_home}
    ]
        return table
    return False



