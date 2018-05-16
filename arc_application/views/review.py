import json
import time
import requests

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from timeline_logger.models import TimelineLog

from ..forms.form import PreviousRegistrationDetailsForm
from ..forms.form import AdultInYourHomeForm, ChildInYourHomeForm, CommentsForm
from ..magic_link import generate_magic_link
from ..models import PreviousRegistrationDetails
from ..models import ApplicantName, ApplicantPersonalDetails, Application, Arc, ArcComments, ChildcareType, UserDetails
from .base import release_application
from ..notify import send_email

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

            queryset = TimelineLog.objects.filter(object_id=application_id).order_by('-timestamp')

            resubmitted = False
            for log in queryset:
                log_message = log.get_message()
                if "Application re-submitted" in log_message:
                    resubmitted = True
                    break

            if resubmitted:
                if application.login_details_review == 'COMPLETED':
                    reviewed.append('login_details')
                if application.personal_details_review == 'COMPLETED':
                    reviewed.append('personal_details')
                if application.childcare_type_review == 'COMPLETED':
                    reviewed.append('childcare_type')
                if application.first_aid_review == 'COMPLETED':
                    reviewed.append('first_aid')
                if application.dbs_review == 'COMPLETED':
                    reviewed.append('dbs_check')
                if application.eyfs_review == 'COMPLETED':
                    reviewed.append('eyfs_review')
                if application.health_review == 'COMPLETED':
                    reviewed.append('health')
                if application.references_review == 'COMPLETED':
                    reviewed.append('references')
                if application.people_in_home_review == 'COMPLETED':
                    reviewed.append('people_in_home')

            else:
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
                if application.eyfs_review == 'COMPLETED' or application.eyfs_review == 'FLAGGED':
                    reviewed.append('eyfs_review')
                if application.health_review == 'COMPLETED' or application.health_review == 'FLAGGED':
                    reviewed.append('health')
                if application.references_review == 'COMPLETED' or application.references_review == 'FLAGGED':
                    reviewed.append('references')
                if application.people_in_home_review == 'COMPLETED' or application.people_in_home_review == 'FLAGGED':
                    reviewed.append('people_in_home')

            review_count = len(reviewed)
            # Load review status
            application_status_context = {
                'application_id': application_id,
                'login_details_status': application.login_details_review,
                'personal_details_status': application.personal_details_review,
                'childcare_type_status': application.childcare_type_review,
                'first_aid_training_status': application.first_aid_review,
                'criminal_record_check_status': application.dbs_review,
                'eyfs_status': application.eyfs_review,
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
            }

    return render(request, 'task-list.html', application_status_context)


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

        return render(request, 'review-confirmation.html', variables)

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
            app.eyfs_review = arc.eyfs_review
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
    :param first_name: string first name
    :param ref: string ref
    :return: HTTP response
    """
    if hasattr(settings, 'NOTIFY_URL'):
        email = str(email)
        template_id = 'b973c5a2-cadd-46a5-baf7-beae65ab11dc'
        personalisation = {'first_name': first_name, 'ref': ref}
        return send_email(email, personalisation, template_id)


# Add personalisation and create template
def returned_email(email, first_name, ref, link):
    """
    Method to send an email using the Notify Gateway API
    :param email: string containing the e-mail address to send the e-mail to
    :param first_name: string first name
    :param ref: string ref
    :return: HTTP response
    """
    if hasattr(settings, 'NOTIFY_URL'):
        email = str(email)
        template_id = 'c9157aaa-02cd-4294-8094-df2184c12930'
        personalisation = {'first_name': first_name, 'ref': ref, 'link': link}
        return send_email(email, personalisation, template_id)


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
            five_years_in_uk = form.cleaned_data.get('five_years_in_UK')

            if PreviousRegistrationDetails.objects.filter(application_id=app).exists():
                previous_reg_details = PreviousRegistrationDetails.objects.get(application_id=app)
            else:
                previous_reg_details = PreviousRegistrationDetails(application_id=app)

            previous_reg_details.previous_registration = previous_registration
            previous_reg_details.individual_id = individual_id
            previous_reg_details.five_years_in_UK = five_years_in_uk
            previous_reg_details.save()

            redirect_link = '/personal-details/summary'
            return HttpResponseRedirect(settings.URL_PREFIX + redirect_link + '?id=' + application_id_local)

        else:
            variables = {
                'form': form,
                'application_id': application_id_local,
            }

            return render(request, 'add-previous-registration.html', context=variables)
