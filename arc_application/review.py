import datetime

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.shortcuts import render

from .models import ApplicantHomeAddress, ApplicantName, ApplicantPersonalDetails, Application, ChildcareType, \
    FirstAidTraining, UserDetails, Eyfs, CriminalRecordCheck, Reference, ChildInHome, AdultInHome, \
    HealthDeclarationBooklet


@login_required()
def task_list(request):
    if has_group(request.user, 'arc'):
        if request.method == 'GET':
            application_id = request.GET['id']
            application = Application.objects.get(pk=application_id)
            childcare_record = ChildcareType.objects.get(application_id=application_id)

            application_status_context = dict({
                'application_id': application_id,
                'login_details_status': application.login_details_status,
                'personal_details_status': application.personal_details_status,
                'childcare_type_status': application.childcare_type_status,
                'first_aid_training_status': application.first_aid_training_status,
                'eyfs_training_status': application.eyfs_training_status,
                'criminal_record_check_status': application.criminal_record_check_status,
                'health_status': application.health_status,
                'reference_status': application.references_status,
                'people_in_home_status': application.people_in_home_status,
                'declaration_status': application.declarations_status,
                'all_complete': False,
                'confirm_details': False,
            })
            temp_context = application_status_context
            del temp_context['declaration_status']
            # Enable/disable Declarations and Confirm your details tasks depending on task completion
            if ('NOT_STARTED' in temp_context.values()) or ('IN_PROGRESS' in temp_context.values()):
                application_status_context['all_complete'] = False
            else:
                application_status_context['all_complete'] = True
                application_status_context['declaration_status'] = application.declarations_status
                if application_status_context['declaration_status'] == 'COMPLETED':
                    application_status_context['confirm_details'] = True
                else:
                    application_status_context['confirm_details'] = False
        return render(request, 'task-list.html', application_status_context)


def contact_summary(request):
    """
    Method returning the template for the Your login and contact details: summary page (for a given application)
    displaying entered data for this task and navigating to the Type of childcare page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your login and contact details: summary template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        application = Application.objects.get(pk=application_id_local)
        login_id = application.login_id
        user_details = UserDetails.objects.get(login_id=login_id)
        email = user_details.email
        mobile_number = user_details.mobile_number
        add_phone_number = user_details.add_phone_number
        security_question = user_details.security_question
        security_answer = user_details.security_answer
        variables = {
            'application_id': application_id_local,
            'email': email,
            'mobile_number': mobile_number,
            'add_phone_number': add_phone_number,
            'security_question': security_question,
            'security_answer': security_answer,
            'login_details_status': application.login_details_status,
            'childcare_type_status': application.childcare_type_status
        }
        return render(request, 'contact-summary.html', variables)


def type_of_childcare_age_groups(request):
    """
    Method returning the template for the Type of childcare: age groups page (for a given application) and navigating
    to the task list when successfully completed; business logic is applied to either create or update the
    associated Childcare_Type record
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Type of childcare: age groups template
    """
    current_date = datetime.datetime.today()
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        application = ChildcareType.objects.get(application_id=application_id_local)

        variables = {
            'application_id': str(application_id_local),
            'zero': application.zero_to_five,
            'five': application.five_to_eight,
            'eight': application.eight_plus,
        }
        return render(request, 'childcare-age-groups.html', variables)


def personal_details_summary(request):
    """
    Method returning the template for the Your personal details: summary page (for a given application)
    displaying entered data for this task and navigating to the task list when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your personal details: summary template
    """
    if request.method == 'GET':
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
        variables = {
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
            'personal_details_status': application.personal_details_status
        }
        return render(request, 'personal-details-summary.html', variables)


def first_aid_training_summary(request):
    """
    Method returning the template for the First aid training: summary page (for a given application)
    displaying entered data for this task and navigating to the task list when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered First aid training: summary template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        training_organisation = FirstAidTraining.objects.get(application_id=application_id_local).training_organisation
        training_course = FirstAidTraining.objects.get(application_id=application_id_local).course_title
        certificate_day = FirstAidTraining.objects.get(application_id=application_id_local).course_day
        certificate_month = FirstAidTraining.objects.get(application_id=application_id_local).course_month
        certificate_year = FirstAidTraining.objects.get(application_id=application_id_local).course_year
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'application_id': application_id_local,
            'training_organisation': training_organisation,
            'training_course': training_course,
            'certificate_day': certificate_day,
            'certificate_month': certificate_month,
            'certificate_year': certificate_year,
            'first_aid_training_status': application.first_aid_training_status
        }
        return render(request, 'first-aid-summary.html', variables)


def eyfs_summary(request):
    """
    Method returning the template for the Early Years knowledge: summary page (for a given application)
    displaying entered data for this task and navigating to the task list when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Early years knowledge: summary template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        eyfs_record = Eyfs.objects.get(application_id=application_id_local)
        eyfs_understand = eyfs_record.eyfs_understand
        eyfs_training_declare = eyfs_record.eyfs_training_declare
        eyfs_questions_declare = eyfs_record.eyfs_questions_declare
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'application_id': application_id_local,
            'eyfs_understand': eyfs_understand,
            'eyfs_training_declare': eyfs_training_declare,
            'eyfs_questions_declare': eyfs_questions_declare,
            'eyfs_training_status': application.eyfs_training_status,
        }
        return render(request, 'eyfs-summary.html', variables)


def dbs_check_summary(request):
    """
    Method returning the template for the Your criminal record (DBS) check: summary page (for a given application)
    displaying entered data for this task and navigating to the task list when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your criminal record (DBS) check: summary template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        criminal_record_check = CriminalRecordCheck.objects.get(application_id=application_id_local)
        dbs_certificate_number = criminal_record_check.dbs_certificate_number
        cautions_convictions = criminal_record_check.cautions_convictions
        send_certificate_declare = criminal_record_check.send_certificate_declare
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'application_id': application_id_local,
            'dbs_certificate_number': dbs_certificate_number,
            'cautions_convictions': cautions_convictions,
            'criminal_record_check_status': application.criminal_record_check_status,
            'declaration': send_certificate_declare
        }
        return render(request, 'dbs-check-summary.html', variables)


def references_summary(request):
    """
    Method returning the template for the 2 references: summary page (for a given application)
    displaying entered data for this task and navigating to the task list when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered 2 references: summary template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        first_reference_record = Reference.objects.get(application_id=application_id_local, reference=1)
        second_reference_record = Reference.objects.get(application_id=application_id_local, reference=2)
        first_reference_first_name = first_reference_record.first_name
        first_reference_last_name = first_reference_record.last_name
        first_reference_relationship = first_reference_record.relationship
        first_reference_years_known = first_reference_record.years_known
        first_reference_months_known = first_reference_record.months_known
        first_reference_street_line1 = first_reference_record.street_line1
        first_reference_street_line2 = first_reference_record.street_line2
        first_reference_town = first_reference_record.town
        first_reference_county = first_reference_record.county
        first_reference_country = first_reference_record.country
        first_reference_postcode = first_reference_record.postcode
        first_reference_phone_number = first_reference_record.phone_number
        first_reference_email = first_reference_record.email
        second_reference_first_name = second_reference_record.first_name
        second_reference_last_name = second_reference_record.last_name
        second_reference_relationship = second_reference_record.relationship
        second_reference_years_known = second_reference_record.years_known
        second_reference_months_known = second_reference_record.months_known
        second_reference_street_line1 = second_reference_record.street_line1
        second_reference_street_line2 = second_reference_record.street_line2
        second_reference_town = second_reference_record.town
        second_reference_county = second_reference_record.county
        second_reference_country = second_reference_record.country
        second_reference_postcode = second_reference_record.postcode
        second_reference_phone_number = second_reference_record.phone_number
        second_reference_email = second_reference_record.email
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'application_id': application_id_local,
            'first_reference_first_name': first_reference_first_name,
            'first_reference_last_name': first_reference_last_name,
            'first_reference_relationship': first_reference_relationship,
            'first_reference_years_known': first_reference_years_known,
            'first_reference_months_known': first_reference_months_known,
            'first_reference_street_line1': first_reference_street_line1,
            'first_reference_street_line2': first_reference_street_line2,
            'first_reference_town': first_reference_town,
            'first_reference_county': first_reference_county,
            'first_reference_country': first_reference_country,
            'first_reference_postcode': first_reference_postcode,
            'first_reference_phone_number': first_reference_phone_number,
            'first_reference_email': first_reference_email,
            'second_reference_first_name': second_reference_first_name,
            'second_reference_last_name': second_reference_last_name,
            'second_reference_relationship': second_reference_relationship,
            'second_reference_years_known': second_reference_years_known,
            'second_reference_months_known': second_reference_months_known,
            'second_reference_street_line1': second_reference_street_line1,
            'second_reference_street_line2': second_reference_street_line2,
            'second_reference_town': second_reference_town,
            'second_reference_county': second_reference_county,
            'second_reference_country': second_reference_country,
            'second_reference_postcode': second_reference_postcode,
            'second_reference_phone_number': second_reference_phone_number,
            'second_reference_email': second_reference_email,
            'references_status': application.references_status
        }
        return render(request, 'references-summary.html', variables)


def other_people_summary(request):
    """
    Method returning the template for the People in your home: summary page (for a given application)
    displaying entered data for this task and navigating to the task list when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered People in your home: summary template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        adults_list = AdultInHome.objects.filter(application_id=application_id_local).order_by('adult')
        adult_name_list = []
        adult_birth_day_list = []
        adult_birth_month_list = []
        adult_birth_year_list = []
        adult_relationship_list = []
        adult_dbs_list = []
        adult_permission_list = []
        children_list = ChildInHome.objects.filter(application_id=application_id_local).order_by('child')
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
            adult_name_list.append(name)
            adult_birth_day_list.append(adult.birth_day)
            adult_birth_month_list.append(adult.birth_month)
            adult_birth_year_list.append(adult.birth_year)
            adult_relationship_list.append(adult.relationship)
            adult_dbs_list.append(adult.dbs_certificate_number)
            adult_permission_list.append(adult.permission_declare)
        adult_lists = zip(adult_name_list, adult_birth_day_list, adult_birth_month_list, adult_birth_year_list,
                          adult_relationship_list, adult_dbs_list, adult_permission_list)
        for child in children_list:
            if child.middle_names != '':
                name = child.first_name + ' ' + child.middle_names + ' ' + child.last_name
            elif child.middle_names == '':
                name = child.first_name + ' ' + child.last_name
            child_name_list.append(name)
            child_birth_day_list.append(child.birth_day)
            child_birth_month_list.append(child.birth_month)
            child_birth_year_list.append(child.birth_year)
            child_relationship_list.append(child.relationship)
        child_lists = zip(child_name_list, child_birth_day_list, child_birth_month_list, child_birth_year_list,
                          child_relationship_list)
        variables = {
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


def health_check_answers(request):
    """
    Method returning the template for the Your health: answers page (for a given application)
    displaying entered data for this task and navigating to the task list when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your health: answers template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        send_hdb_declare = HealthDeclarationBooklet.objects.get(application_id=application_id_local).send_hdb_declare
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'application_id': application_id_local,
            'send_hdb_declare': send_hdb_declare,
            'health_status': application.health_status,
        }
        return render(request, 'health-check-answers.html', variables)


def declaration(request):
    application_id_local = request.GET["id"]
    variables = {
        'application_id': application_id_local,
    }
    return render(request, 'review-confirmation.html', variables)


def has_group(user, group_name):
    group = Group.objects.get(name=group_name)
    return True if group in user.groups.all() else False
