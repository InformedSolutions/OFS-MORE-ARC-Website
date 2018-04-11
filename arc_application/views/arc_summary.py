from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from ..summary_page_data import link_dict
from ..models import *


def arc_summary(request):
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        json = load_json(application_id_local)
        json = add_comments(json, application_id_local)
        variables = {
            'json': json,
            'application_id':application_id_local
        }
        return render(request, 'arc-summary.html', variables)
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
                 'First aid training provider', 'Your first aid certificate','Date of first aid certificate',
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
    login_record = UserDetails.objects.get(application_id=application)
    login_detail_id = login_record.pk
    childcare_record = ChildcareType.objects.get(application_id=application_id_local)
    applicant_record = ApplicantPersonalDetails.objects.get(application_id=application_id_local)
    personal_detail_id = applicant_record.personal_detail_id
    applicant_name_record = ApplicantName.objects.get(personal_detail_id=personal_detail_id)
    applicant_home_address_record = ApplicantHomeAddress.objects.get(personal_detail_id=personal_detail_id,
                                                                     current_address=True)
    applicant_childcare_address_record = ApplicantHomeAddress.objects.get(personal_detail_id=personal_detail_id,
                                                                          childcare_address=True)
    first_aid_record = FirstAidTraining.objects.get(application_id=application_id_local)
    dbs_record = CriminalRecordCheck.objects.get(application_id=application_id_local)
    hdb_record = HealthDeclarationBooklet.objects.get(application_id=application_id_local)
    first_reference_record = Reference.objects.get(application_id=application_id_local, reference=1)
    second_reference_record = Reference.objects.get(application_id=application_id_local, reference=2)
    # Retrieve lists of adults and children, ordered by adult/child number for iteration by the HTML
    adults_list = AdultInHome.objects.filter(application_id=application_id_local).order_by('adult')
    children_list = ChildInHome.objects.filter(application_id=application_id_local).order_by('child')
    # Generate lists of data for adults in your home, to be iteratively displayed on the summary page
    # The HTML will then parse through each list simultaneously, to display the correct data for each adult
    adult_name_list = []
    adult_birth_day_list = []
    adult_birth_month_list = []
    adult_birth_year_list = []
    adult_relationship_list = []
    adult_dbs_list = []
    adult_permission_list = []
    application = Application.objects.get(pk=application_id_local)
    for adult in adults_list:
        # For each adult, append the correct attribute (e.g. name, relationship) to the relevant list
        # Concatenate the adult's name for display, displaying any middle names if present
        if adult.middle_names != '':
            name = adult.first_name + ' ' + adult.middle_names + ' ' + adult.last_name
        elif adult.middle_names == '':
            name = adult.first_name + ' ' + adult.last_name
        adult_name_list.append(name)
        adult_birth_day_list.append(adult.birth_day)
        adult_birth_month_list.append(adult.birth_month)
        adult_birth_year_list.append(adult.birth_year)
        adult_relationship_list.append(adult.relationship)
        adult_dbs_list.append(adult.dbs_certificate_number)
        adult_permission_list.append(adult.permission_declare)
    # Zip the appended lists together for the HTML to simultaneously parse
    adult_lists = zip(adult_name_list, adult_birth_day_list, adult_birth_month_list, adult_birth_year_list,
                      adult_relationship_list, adult_dbs_list, adult_permission_list)
    # Generate lists of data for adults in your home, to be iteratively displayed on the summary page
    # The HTML will then parse through each list simultaneously, to display the correct data for each adult
    child_name_list = []
    child_birth_day_list = []
    child_birth_month_list = []
    child_birth_year_list = []
    child_relationship_list = []

    for child in children_list:
        # For each child, append the correct attribute (e.g. name, relationship) to the relevant list
        # Concatenate the child's name for display, displaying any middle names if present
        if child.middle_names != '':
            name = child.first_name + ' ' + child.middle_names + ' ' + child.last_name
        elif child.middle_names == '':
            name = child.first_name + ' ' + child.last_name
        child_name_list.append(name)
        child_birth_day_list.append(child.birth_day)
        child_birth_month_list.append(child.birth_month)
        child_birth_year_list.append(child.birth_year)
        child_relationship_list.append(child.relationship)
    # Zip the appended lists together for the HTML to simultaneously parse
    child_lists = zip(child_name_list, child_birth_day_list, child_birth_month_list, child_birth_year_list,
                      child_relationship_list)

    home_address = applicant_home_address_record.street_line1 +', ' +applicant_home_address_record.street_line2 + ', ' +applicant_home_address_record.town +', ' +applicant_home_address_record.postcode
    ref1_address =first_reference_record.street_line1 +', ' + first_reference_record.street_line2 +', ' +first_reference_record.town +', ' +first_reference_record.postcode
    ref2_address =second_reference_record.street_line1 +', ' + second_reference_record.street_line2 +', ' +second_reference_record.town +', ' +second_reference_record.postcode
    z = childcare_record.zero_to_five
    f = childcare_record.five_to_eight
    e = childcare_record.eight_plus
    register = ''
    if z and f or z and not f and e:
        register = 'Early Years Register, Childcare Register'
    if not z and f and e:
        register = 'Childcare Register (compulsory & voluntary parts)'
    if z and not f and not e:
        register = 'Early Years Register'
    if not z and f and not e:
        register = 'Childcare Register (compulsory part)'
    if not z and not f and e:
        register = 'Childcare Register (voluntary part)'




    ### Create Json
    login_details_table = [
        {"title": "Your login details", "id": login_detail_id},
        {"name": "Your email", "value": login_record.email},
        {"name": "Mobile phone number", "value": login_record.mobile_number},
        {"name": "Alternative phone number", "value": login_record.add_phone_number},
        {"name": "Knowledge based question", "value": login_record.security_question},
        {"name": "Knowledge based answer", "value": login_record.security_question}

    ]

    childcare_type_table = [
        {"title": "Childcare Type", "id": childcare_record.pk},
        {"name": "Looking after 0 to 5 year olds?", "value": childcare_record.zero_to_five},
        {"name": "Looking after 5 to 7 year olds? ", "value": childcare_record.five_to_eight},
        {"name": "Looking after 8 year olds and older? ", "value": childcare_record.eight_plus},
        {"name": "Registers", "value": register}
    ]

    personal_detail_table = [
        {"title": "Your personal details",  "id": personal_detail_id},
        {"name": "Your name",
         "value": applicant_name_record.first_name + ' ' + applicant_name_record.middle_names + ' ' + applicant_name_record.last_name,
         'pk': applicant_name_record.pk},
        {"name": "Your date of birth",
         "value": str(applicant_record.birth_day) + '/' + str(applicant_record.birth_month) + '/' + str(
             applicant_record.birth_year), 'pk': applicant_record.pk},
        {"name": "Home address", "value": home_address, 'pk': applicant_home_address_record.pk},
        {"name": "Childcare location", "value": "Same as home address", 'pk': applicant_home_address_record.pk}
    ]

    first_aid_table = [
        {"title": "Your first aid certificate", "id": first_aid_record.pk},
        {"name": "First aid training provider", "value": first_aid_record.training_organisation},
        {"name": "Title of first aid course", "value": first_aid_record.course_title},
        {"name": "Date of first aid certificate",
         "value": str(first_aid_record.course_day) + '/' + str(first_aid_record.course_month) + '/' + str(first_aid_record.course_year)}
    ]

    criminal_record_table = [
        {"title": "Criminal record checks", "id": dbs_record.pk},
        {"name": "DBS certificate number", "value": dbs_record.dbs_certificate_number},
        {"name": "Do you have any cautions or convictions?", "value": dbs_record.cautions_convictions}
    ]

    health_check_table = [
        {"title": "Health checks", "id": hdb_record.pk},
        {"name": "Provide a Health Declaration Booklet?", "value": hdb_record.send_hdb_declare}
    ]

    first_reference_table = [
        {"title": "First reference", "id": first_reference_record.pk},
        {"name": "Full name", "value": first_reference_record.first_name + ' ' + first_reference_record.last_name},
        {"name": "How they know you", "value": first_reference_record.relationship},
        {"name": "Known for", "value":str(first_reference_record.months_known) + ' months, ' +str(first_reference_record.years_known) +' years'},
        {"name": "Address", "value": ref1_address},
        {"name": "Phone number", "value": first_reference_record.phone_number},
        {"name": "Email address", "value": first_reference_record.email}

    ]

    second_reference_table = [
        {"title": "Second reference", "id": second_reference_record.pk},
        {"name": "Full name", "value": second_reference_record.first_name + ' ' + second_reference_record.last_name},
        {"name": "How they know you", "value": second_reference_record.relationship},
        {"name": "Known for", "value":str(second_reference_record.months_known) + ' months, ' +str(second_reference_record.years_known) +' years'},
        {"name": "Address", "value": ref2_address},
        {"name": "Phone number", "value": second_reference_record.phone_number},
        {"name": "Email address", "value": second_reference_record.email}

    ]

    adult_home_table = [
        {"title": "Adults in your home", "id": login_record.login_id},
        {"name": "Do you live with anyone who is 16 or over?", "value": application.adults_in_home}
    ]
    child_home_table = [
        {"title": "Children in your home", "id": login_record.login_id},
        {"name": "Do you live with any children?", "value": application.children_in_home}
    ]
    return [login_details_table, childcare_type_table, personal_detail_table, first_aid_table, criminal_record_table,
            health_check_table, first_reference_table, second_reference_table, adult_home_table, child_home_table]
