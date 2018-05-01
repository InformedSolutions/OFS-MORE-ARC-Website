import json
import time

import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View

from ..forms.form import AdultInYourHomeForm, CheckBox, ChildInYourHomeForm, CommentsForm, DBSCheckForm, FirstAidTrainingForm, \
    HealthForm, LogInDetailsForm, OtherPeopleInYourHomeForm, PersonalDetailsForm, ReferencesForm, ReferencesForm2, PreviousRegistrationDetailsForm
from ..forms.form import AdultInYourHomeForm, ChildInYourHomeForm, CommentsForm, DBSCheckForm, FirstAidTrainingForm, \
    HealthForm, LogInDetailsForm, ReferencesForm, ReferencesForm2
from ..magic_link import generate_magic_link
from ..models import AdultInHome, ApplicantHomeAddress, ApplicantName, ApplicantPersonalDetails, Application, Arc, \
    ArcComments, ChildInHome, ChildcareType, CriminalRecordCheck, FirstAidTraining, HealthDeclarationBooklet, Reference, \
    UserDetails, PreviousRegistrationDetails
from ..models import ApplicantName, ApplicantPersonalDetails, Application, Arc, \
    ArcComments, ChildcareType, CriminalRecordCheck, FirstAidTraining, HealthDeclarationBooklet, Reference, \
    UserDetails
from ..review_util import redirect_selection, request_to_comment, save_comments
from .base import release_application


@login_required()
def task_list(request):
    """
    Generates the full task list for ARC users
    :param request:  The Http request directed to the view
    :return: The task list page with the associated context
    """

    # If the user has signed in and is a member of the ARC group
    if has_group(request.user, 'arc'):
        if request.method == 'GET':
            application_id = request.GET['id']
            application = Arc.objects.get(application_id=application_id)
            personal_details_record = ApplicantPersonalDetails.objects.get(application_id=application_id)
            name_record = ApplicantName.objects.get(personal_detail_id=personal_details_record.personal_detail_id)
            childcare_type_record = ChildcareType.objects.get(application_id=application_id)
            reviewed = []
            if application.login_details_review == 'COMPLETED' or application.login_details_review == 'FLAGGED':
                reviewed.append('login_details')
            if application.personal_details_review == 'COMPLETED' or application.personal_details_review == 'FLAGGED':
                reviewed.append('personal_details')
            if application.childcare_type_review == 'COMPLETED' or application.childcare_type_review == 'FLAGGED':
                reviewed.append('childcare_type')
            if application.first_aid_review == 'COMPLETED' or application.first_aid_review == 'FLAGGED':
                reviewed.append('first_aid')
            if application.dbs_review == 'COMPLETED' or application.dbs_review == 'FLAGGED':
                reviewed.append('dbs_check')
            if application.health_review == 'COMPLETED' or application.health_review == 'FLAGGED':
                reviewed.append('health')
            if application.references_review == 'COMPLETED' or application.references_review == 'FLAGGED':
                reviewed.append('references')
            if application.people_in_home_review == 'COMPLETED' or application.people_in_home_review == 'FLAGGED':
                reviewed.append('people_in_home')
            review_count = len(reviewed)
            # Load review status
            application_status_context = dict({
                'application_id': application_id,
                'login_details_status': application.login_details_review,
                'personal_details_status': application.personal_details_review,
                'childcare_type_status': application.childcare_type_review,
                'first_aid_training_status': application.first_aid_review,
                'criminal_record_check_status': application.dbs_review,
                'health_status': application.health_review,
                'reference_status': application.references_review,
                'people_in_home_status': application.people_in_home_review,
                'birth_day': personal_details_record.birth_day,
                'birth_month': personal_details_record.birth_month,
                'birth_year': personal_details_record.birth_year,
                'first_name': name_record.first_name,
                'middle_names': name_record.middle_names,
                'last_name': name_record.last_name,
                'zero_to_five': childcare_type_record.zero_to_five,
                'five_to_eight': childcare_type_record.five_to_eight,
                'eight_plus': childcare_type_record.eight_plus,
                'review_count': review_count,
                'all_complete': all_complete(application_id, False)
            })

    return render(request, 'task-list.html', application_status_context)


def contact_summary(request):
    """
    Method returning the template for the Your login and contact details: summary page (for a given application)
    displaying entered data for this task and navigating to the Type of childcare page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your login and contact details: summary template
    """
    TABLE_NAME = 'USER_DETAILS'

    if request.method == 'GET':
        application_id_local = request.GET["id"]
        application = Application.objects.get(pk=application_id_local)
        account = UserDetails.objects.get(application_id=application)
        login_id = account.login_id
        # Table keys are supplied in a list format for use in init
        form = LogInDetailsForm(table_keys=[login_id])
        application_id_local = request.GET["id"]
    elif request.method == 'POST':
        # Populate the form with the received data
        application_id_local = request.POST["id"]
        application = Application.objects.get(pk=application_id_local)
        account = UserDetails.objects.get(application_id=application)
        login_id = account.login_id
        form = LogInDetailsForm(request.POST, table_keys=[login_id])

        if form.is_valid():
            # Convert the data from the form into a series of comments with the
            # table id to be stored in the ARC COMMENTS Table
            comment_list = request_to_comment(login_id, TABLE_NAME, form.cleaned_data)
            save_successful = save_comments(comment_list)

            # If no comments have been made, the status has not been flagged
            # Therefore it has been completed
            if not comment_list:
                section_status = 'COMPLETED'
            else:
                section_status = 'FLAGGED'

            # If the save has been successful , save and redirect
            if save_successful:
                status = Arc.objects.get(pk=application_id_local)
                status.login_details_review = section_status
                status.save()
                default = '/childcare/age-groups'
                redirect_link = redirect_selection(request, default)

                return HttpResponseRedirect(settings.URL_PREFIX + redirect_link + '?id=' + application_id_local)
            else:
                return ChildProcessError

    application = Application.objects.get(pk=application_id_local)
    user_details = UserDetails.objects.get(application_id=application)
    email = user_details.email
    mobile_number = user_details.mobile_number
    add_phone_number = user_details.add_phone_number
    security_question = user_details.security_question
    security_answer = user_details.security_answer
    variables = {
        'form': form,
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

    if request.method == 'GET':
        application_id_local = request.GET["id"]
    elif request.method == 'POST':
        # As there is no actual flagging to be done for this section, the status is just set to completed on POST
        application_id_local = request.POST["id"]
        status = Arc.objects.get(pk=application_id_local)
        status.childcare_type_review = 'COMPLETED'
        status.save()
        default = '/personal-details/summary'
        redirect_link = redirect_selection(request, default)

        return HttpResponseRedirect(settings.URL_PREFIX + redirect_link + '?id=' + application_id_local)
    application_id_local = request.GET["id"]
    application = ChildcareType.objects.get(application_id=application_id_local)

    variables = {
        'application_id': str(application_id_local),
        'zero': application.zero_to_five,
        'five': application.five_to_eight,
        'eight': application.eight_plus,
    }
    return render(request, 'childcare-age-groups.html', variables)


def first_aid_training_summary(request):
    """
    Method returning the template for the First aid training: summary page (for a given application)
    displaying entered data for this task and navigating to the task list when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered First aid training: summary template
    """
    TABLE_NAME = 'FIRST_AID_TRAINING'

    if request.method == 'GET':
        application_id_local = request.GET["id"]
        first_aid_id = FirstAidTraining.objects.get(application_id=application_id_local).first_aid_id
        form = FirstAidTrainingForm(table_keys=[first_aid_id])

    elif request.method == 'POST':
        application_id_local = request.POST["id"]
        first_aid_id = FirstAidTraining.objects.get(application_id=application_id_local).first_aid_id
        form = FirstAidTrainingForm(request.POST, table_keys=[application_id_local])

        if form.is_valid():
            comment_list = request_to_comment(first_aid_id, TABLE_NAME, form.cleaned_data)
            save_successful = save_comments(comment_list)

            if not comment_list:
                section_status = 'COMPLETED'
            else:
                section_status = 'FLAGGED'

            if save_successful:
                status = Arc.objects.get(pk=application_id_local)
                status.first_aid_review = section_status
                status.save()
                default = '/dbs-check/summary'
                redirect_link = redirect_selection(request, default)

                return HttpResponseRedirect(settings.URL_PREFIX + redirect_link + '?id=' + application_id_local)
            else:
                return render(request, '500.html')

    training_organisation = FirstAidTraining.objects.get(application_id=application_id_local).training_organisation
    training_course = FirstAidTraining.objects.get(application_id=application_id_local).course_title
    certificate_day = FirstAidTraining.objects.get(application_id=application_id_local).course_day
    certificate_month = FirstAidTraining.objects.get(application_id=application_id_local).course_month
    certificate_year = FirstAidTraining.objects.get(application_id=application_id_local).course_year
    application = Application.objects.get(pk=application_id_local)
    variables = {
        'form': form,
        'application_id': application_id_local,
        'training_organisation': training_organisation,
        'training_course': training_course,
        'certificate_day': certificate_day,
        'certificate_month': certificate_month,
        'certificate_year': certificate_year,
        'first_aid_training_status': application.first_aid_training_status
    }
    return render(request, 'first-aid-summary.html', variables)


def dbs_check_summary(request):
    """
    Method returning the template for the Your criminal record (DBS) check: summary page (for a given application)
    displaying entered data for this task and navigating to the task list when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your criminal record (DBS) check: summary template
    """
    TABLE_NAME = 'CRIMINAL_RECORD_CHECK'

    if request.method == 'GET':
        application_id_local = request.GET["id"]
        criminal_record_id = CriminalRecordCheck.objects.get(application_id=application_id_local).criminal_record_id

        form = DBSCheckForm(table_keys=[criminal_record_id])
    elif request.method == 'POST':
        application_id_local = request.POST["id"]
        criminal_record_id = CriminalRecordCheck.objects.get(application_id=application_id_local).criminal_record_id
        form = DBSCheckForm(request.POST, table_keys=[criminal_record_id])

        if form.is_valid():
            comment_list = request_to_comment(criminal_record_id, TABLE_NAME, form.cleaned_data)
            save_successful = save_comments(comment_list)

            if not comment_list:
                section_status = 'COMPLETED'
            else:
                section_status = 'FLAGGED'

            if save_successful:
                status = Arc.objects.get(pk=application_id_local)
                status.dbs_review = section_status
                status.save()
                default = '/health/check-answers'
                redirect_link = redirect_selection(request, default)

                return HttpResponseRedirect(settings.URL_PREFIX + redirect_link + '?id=' + application_id_local)
            else:
                return render(request, '500.html')

    criminal_record_check = CriminalRecordCheck.objects.get(application_id=application_id_local)
    dbs_certificate_number = criminal_record_check.dbs_certificate_number
    cautions_convictions = criminal_record_check.cautions_convictions
    send_certificate_declare = criminal_record_check.send_certificate_declare
    application = Application.objects.get(pk=application_id_local)
    variables = {
        'form': form,
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
    TABLE_NAME = 'REFERENCE'

    if request.method == 'GET':
        application_id_local = request.GET["id"]

        reference_id_1 = Reference.objects.get(application_id=application_id_local, reference=1).reference_id
        reference_id_2 = Reference.objects.get(application_id=application_id_local, reference=2).reference_id

        form = ReferencesForm(table_keys=[reference_id_1], prefix="form")
        form2 = ReferencesForm2(table_keys=[reference_id_2], prefix="form2")
    elif request.method == 'POST':
        form1_dict = {}
        form2_dict = {}

        # Grab necessary IDs
        application_id_local = request.POST["id"]
        reference_id_1 = Reference.objects.get(application_id=application_id_local, reference=1).reference_id
        reference_id_2 = Reference.objects.get(application_id=application_id_local, reference=2).reference_id

        # Grab form data from post
        form = ReferencesForm(request.POST, table_keys=[reference_id_1], prefix="form")
        form2 = ReferencesForm2(request.POST, table_keys=[reference_id_2], prefix="form2")

        # As form data prefixed in above lines to separate the two forms, this prefix must be removed before
        # storage, this is to allow for easier retrieval form the database

        if form.is_valid() and form2.is_valid():

            # Get comments to be saved
            form_comments = request_to_comment(reference_id_1, TABLE_NAME, form.cleaned_data)
            form2_comments = request_to_comment(reference_id_2, TABLE_NAME, form2.cleaned_data)

            # Save the comments
            reference1_saved = save_comments(form_comments)
            reference2_saved = save_comments(form2_comments)

            if not form_comments and not form2_comments:
                section_status = 'COMPLETED'
            else:
                section_status = 'FLAGGED'

            if reference1_saved and reference2_saved:
                status = Arc.objects.get(pk=application_id_local)
                status.references_review = section_status
                status.save()
                default = '/other-people/summary'
                redirect_link = redirect_selection(request, default)

                return HttpResponseRedirect(settings.URL_PREFIX + redirect_link + '?id=' + application_id_local)
            else:
                return render(request, '500.html')

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
        'form': form,
        'form2': form2,
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


def health_check_answers(request):
    """
    Method returning the template for the Your health: answers page (for a given application)
    displaying entered data for this task and navigating to the task list when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your health: answers template
    """
    TABLE_NAME = 'HDB'

    if request.method == 'GET':
        application_id_local = request.GET["id"]
        hdb_id = HealthDeclarationBooklet.objects.get(application_id=application_id_local).hdb_id
        form = HealthForm(table_keys=[hdb_id])

    elif request.method == 'POST':
        application_id_local = request.POST["id"]
        hdb_id = HealthDeclarationBooklet.objects.get(application_id=application_id_local).hdb_id
        form = HealthForm(request.POST, table_keys=[hdb_id])

        if form.is_valid():
            comment_list = request_to_comment(hdb_id, TABLE_NAME, form.cleaned_data)
            save_successful = save_comments(comment_list)

            if not comment_list:
                section_status = 'COMPLETED'
            else:
                section_status = 'FLAGGED'

            if save_successful:
                status = Arc.objects.get(pk=application_id_local)
                status.health_review = section_status
                status.save()
                default = '/references/summary'
                redirect_link = redirect_selection(request, default)

                return HttpResponseRedirect(settings.URL_PREFIX + redirect_link + '?id=' + application_id_local)

            else:
                return render(request, '500.html')

    send_hdb_declare = HealthDeclarationBooklet.objects.get(application_id=application_id_local).send_hdb_declare
    application = Application.objects.get(pk=application_id_local)
    variables = {
        'form': form,
        'application_id': application_id_local,
        'send_hdb_declare': send_hdb_declare,
        'health_status': application.health_status,
    }
    return render(request, 'health-check-answers.html', variables)


def comments(request):
    """
    This is the arc comments page
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your arc comments template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = CommentsForm(request.POST, id=application_id_local)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = CommentsForm(request.POST, id=application_id_local)
        if form.is_valid():
            comments = form.cleaned_data['comments']
            if Arc.objects.filter(application_id=application_id_local):
                arc = Arc.objects.get(application_id=application_id_local)
                arc.comments = comments
                arc.save()
        return review(request)
    variables = {
        'form': form,
        'application_id': application_id_local,
    }
    return render(request, 'comments.html', variables)


def review(request):
    """
    Confirmation Page
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your App Review Confirmation template
    """
    application_id_local = request.GET["id"]
    application = Application.objects.get(application_id=application_id_local)
    account = UserDetails.objects.get(application_id=application)
    login_id = account.pk
    first_name = ''
    if UserDetails.objects.filter(login_id=login_id).exists():
        user_details = UserDetails.objects.get(login_id=login_id)
        email = user_details.email
        if ApplicantPersonalDetails.objects.filter(application_id=application_id_local).exists():
            personal_details = ApplicantPersonalDetails.objects.get(application_id=application_id_local)
            applicant_name = ApplicantName.objects.get(personal_detail_id=personal_details.personal_detail_id)
            first_name = applicant_name.first_name

    if all_complete(application_id_local, True):
        accepted_email(email, first_name, application_id_local)
        # If successful
        release_application(request, application_id_local, 'ACCEPTED')
        variables = {
            'application_id': application_id_local,
        }
        return render(request, 'review-confirmation.html')

    else:
        release_application(request, application_id_local, 'FURTHER_INFORMATION')
        magic_link = generate_magic_link()
        expiry = int(time.time())
        user_details.email_expiry_date = expiry
        user_details.magic_link_email = magic_link
        user_details.save()
        link = settings.CHILDMINDER_EMAIL_VALIDATION_URL + '/' + magic_link
        returned_email(email, first_name, application_id_local, link)

        # Copy Arc status' to Chilminder App
        if Arc.objects.filter(pk=application_id_local):
            arc = Arc.objects.get(pk=application_id_local)
            app = Application.objects.get(pk=application_id_local)
            app.login_details_status = arc.login_details_review
            app.personal_details_status = arc.personal_details_review
            app.childcare_type_status = arc.childcare_type_review
            app.first_aid_training_status = arc.first_aid_review
            app.health_status = arc.health_review
            app.criminal_record_check_status = arc.dbs_review
            app.references_status = arc.references_review
            app.people_in_home_status = arc.people_in_home_review
            app.save()
        variables = {
            'application_id': application_id_local,
        }
        return render(request, 'review-sent-back.html', variables)

    variables = {
        'application_id': application_id_local,
    }

    return render(request, 'review-sent-back.html', variables)


def has_group(user, group_name):
    """
    Check if user is in group
    :return: True if user is in group, else false
    """
    group = Group.objects.get(name=group_name)
    return True if group in user.groups.all() else False


def all_complete(id, flag):
    """
    Check the status of all sections
    :param id: Application Id
    :return: True or False dependingo n whether all sections have been reviewed
    """
    if Arc.objects.filter(application_id=id):
        arc = Arc.objects.get(application_id=id)
        list = [arc.login_details_review, arc.childcare_type_review, arc.personal_details_review,
                arc.first_aid_review, arc.dbs_review, arc.health_review, arc.references_review,
                arc.people_in_home_review]
        for i in list:
            if (i == 'NOT_STARTED' and not flag) or (i != 'COMPLETED' and flag):
                return False
        return True


# Add personalisation and create template
def accepted_email(email, first_name, ref):
    """
    Method to send an email using the Notify Gateway API
    :param email: string containing the e-mail address to send the e-mail to
    :param email: string email address
    :return: HTTP response
    """
    if hasattr(settings, 'NOTIFY_URL'):
        email = str(email)
        base_request_url = settings.NOTIFY_URL
        header = {'content-type': 'application/json'}
        request = {
            'email': email,
            'templateId': 'b973c5a2-cadd-46a5-baf7-beae65ab11dc',
            'personalisation': {
                'first_name': first_name,
                'ref': ref
            }
        }
        data = json.dumps(request)
        r = requests.post(base_request_url + '/api/v1/notifications/email/',
                          data,
                          headers=header)
        return r


# Add personalisation and create template
def returned_email(email, first_name, ref, link):
    """
    Method to send an email using the Notify Gateway API
    :param email: string containing the e-mail address to send the e-mail to
    :param email: string email address
    :return: HTTP response
    """
    if hasattr(settings, 'NOTIFY_URL'):
        email = str(email)
        base_request_url = settings.NOTIFY_URL
        header = {'content-type': 'application/json'}
        request = {
            'email': email,
            'templateId': 'c9157aaa-02cd-4294-8094-df2184c12930',
            'personalisation': {
                'first_name': first_name,
                'ref': ref,
                'link': link,
            }
        }
        data = json.dumps(request)
        r = requests.post(base_request_url + '/api/v1/notifications/email/',
                          data,
                          headers=header)
        return r


# Including the below file elsewhere caused cyclical import error, keeping here till this can be debugged


def other_people_initial_population(adult, person_list):
    initial_data = []

    for person in person_list:
        temp_dict = {}
        if not adult:
            table_id = person.child_id
            form_instance = ChildInYourHomeForm()
        else:
            table_id = person.adult_id
            form_instance = AdultInYourHomeForm()

        for field in form_instance.fields:
            try:
                if field[-8:] == 'comments':
                    field_name_local = field[:-9]
                    comment = (ArcComments.objects.filter(table_pk=table_id).get(field_name=field_name_local)).comment
                    temp_dict[field] = comment

                if field[-7:] == 'declare':
                    field_name_local = field[:-8]
                    checkbox = (ArcComments.objects.filter(table_pk=table_id).get(field_name=field_name_local)).flagged
                    temp_dict[field] = checkbox

            except ArcComments.DoesNotExist:
                pass
        initial_data.append(temp_dict)
    return initial_data


class PreviousRegistrationDetailsView(View):

    def get(self, request):
        application_id_local = request.GET["id"]
        form = PreviousRegistrationDetailsForm(id=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
        }
        return render(request, 'add-previous-registration.html', context=variables)

    def post(self, request):
        application_id_local = request.POST["id"]
        form = PreviousRegistrationDetailsForm(request.POST, id=application_id_local)
        if form.is_valid():

            app = Application.objects.get(pk=application_id_local)
            previous_registration = form.cleaned_data.get('previous_registration')
            individual_id = form.cleaned_data.get('individual_id')
            five_years_in_UK = form.cleaned_data.get('five_years_in_UK')

            if PreviousRegistrationDetails.objects.filter(application_id=app).exists():
                previous_reg_details = PreviousRegistrationDetails.objects.get(application_id=app)
            else:
                previous_reg_details = PreviousRegistrationDetails(application_id=app)

            previous_reg_details.previous_registration = previous_registration
            previous_reg_details.individual_id = individual_id
            previous_reg_details.five_years_in_UK = five_years_in_UK
            previous_reg_details.save()

            redirect_link = '/personal-details/summary'
            return HttpResponseRedirect(settings.URL_PREFIX + redirect_link + '?id=' + application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local,
            }
            return render(request, 'add-previous-registration.html', context=variables)

