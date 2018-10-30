import time
from datetime import datetime

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View

from arc_application.models import AdultInHome
from arc_application.forms.childminder_forms.form import PreviousRegistrationDetailsForm, ChildForm, \
    ChildAddressForm
from arc_application.forms.childminder_forms.form import AdultInYourHomeForm, ChildInYourHomeForm
from arc_application.magic_link import generate_magic_link
from arc_application.models import PreviousRegistrationDetails, OtherPersonPreviousRegistrationDetails
from arc_application.models import ApplicantName, ApplicantPersonalDetails, Application, Arc, ArcComments, ChildcareType, UserDetails
from arc_application.views.base import release_application
from arc_application.notify import send_email
from arc_application.decorators import group_required, user_assigned_application

decorators = [login_required, group_required(settings.ARC_GROUP), user_assigned_application]


@login_required
@group_required(settings.ARC_GROUP)
@user_assigned_application
def task_list(request):
    """
    Generates the full task list for ARC users
    :param request:  The Http request directed to the view
    :return: The task list page with the associated context
    """

    # If the user has signed in and is a member of the ARC group
    if request.method == 'GET':
        application_id = request.GET['id']
        application = Application.objects.get(application_id=application_id)
        arc_application = Arc.objects.get(application_id=application_id)
        personal_details_record = ApplicantPersonalDetails.objects.get(application_id=application_id)
        name_record = ApplicantName.objects.get(personal_detail_id=personal_details_record.personal_detail_id)
        childcare_type_record = ChildcareType.objects.get(application_id=application_id)

        review_fields_to_check = set_review_fields_to_check(application, childcare_type_record)

        flagged_fields_to_check = set_flagged_fields_to_check(application, childcare_type_record)

        review_count = sum([1 for field in review_fields_to_check if getattr(arc_application, field) == 'COMPLETED'])
        review_count += sum([1 for field in flagged_fields_to_check if getattr(application, field)])

        # Set total number of tasks in right-hand side overview box
        number_of_tasks = set_number_of_tasks(application, childcare_type_record)

        # Load review status
        application_status_context = {
            'application_id': application_id,
            'application_reference': application.application_reference,
            'login_details_status': arc_application.login_details_review,
            'personal_details_status': arc_application.personal_details_review,
            'your_children_status': arc_application.your_children_review,
            'childcare_type_status': arc_application.childcare_type_review,
            'first_aid_training_status': arc_application.first_aid_review,
            'criminal_record_check_status': arc_application.dbs_review,
            'childcare_training_status': arc_application.childcare_training_review,
            'health_status': arc_application.health_review,
            'reference_status': arc_application.references_review,
            'people_in_home_status': arc_application.people_in_home_review,
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
            'all_complete': all_complete(application_id, False),
            'number_of_tasks': number_of_tasks,
            'own_children': application.own_children,
            'working_in_other_childminder_home': application.working_in_other_childminder_home
        }

    return render(request, 'childminder_templates/task-list.html', application_status_context)


def set_flagged_fields_to_check(application, childcare_type_record):
    """
    Method to set the flagged fields to check
    :param application: an Application object
    :param childcare_type_record: a ChildcareType object
    :return: integer
    """
    # Default flagged fields to check
    flagged_fields_to_check = (
        "childcare_type_arc_flagged",
        "criminal_record_check_arc_flagged",
        "childcare_training_arc_flagged",
        "first_aid_training_arc_flagged",
        "login_details_arc_flagged",
        "personal_details_arc_flagged",
        "references_arc_flagged"
    )

    if childcare_type_record.zero_to_five and not application.own_children and application.working_in_other_childminder_home:
        flagged_fields_to_check = (
            "childcare_type_arc_flagged",
            "criminal_record_check_arc_flagged",
            "childcare_training_arc_flagged",
            "first_aid_training_arc_flagged",
            "health_arc_flagged",
            "login_details_arc_flagged",
            "personal_details_arc_flagged",
            "references_arc_flagged"
        )
    elif childcare_type_record.zero_to_five and application.own_children and application.working_in_other_childminder_home:
        flagged_fields_to_check = (
            "childcare_type_arc_flagged",
            "criminal_record_check_arc_flagged",
            "childcare_training_arc_flagged",
            "first_aid_training_arc_flagged",
            "health_arc_flagged",
            "login_details_arc_flagged",
            "personal_details_arc_flagged",
            "references_arc_flagged",
            'your_children_arc_flagged'
        )
    elif childcare_type_record.zero_to_five and application.own_children and not application.working_in_other_childminder_home:
        flagged_fields_to_check = (
            "childcare_type_arc_flagged",
            "criminal_record_check_arc_flagged",
            "childcare_training_arc_flagged",
            "first_aid_training_arc_flagged",
            "health_arc_flagged",
            "login_details_arc_flagged",
            "people_in_home_arc_flagged",
            "personal_details_arc_flagged",
            "references_arc_flagged",
            'your_children_arc_flagged'
        )
    elif not childcare_type_record.zero_to_five and not application.own_children and application.working_in_other_childminder_home:
        flagged_fields_to_check = (
            "childcare_type_arc_flagged",
            "criminal_record_check_arc_flagged",
            "childcare_training_arc_flagged",
            "first_aid_training_arc_flagged",
            "login_details_arc_flagged",
            "personal_details_arc_flagged",
            "references_arc_flagged"
        )
    elif not childcare_type_record.zero_to_five and not application.own_children and not application.working_in_other_childminder_home:
        flagged_fields_to_check = (
            "childcare_type_arc_flagged",
            "criminal_record_check_arc_flagged",
            "childcare_training_arc_flagged",
            "first_aid_training_arc_flagged",
            "login_details_arc_flagged",
            "people_in_home_arc_flagged",
            "personal_details_arc_flagged",
            "references_arc_flagged"
        )
    elif not childcare_type_record.zero_to_five and application.own_children and not application.working_in_other_childminder_home:
        flagged_fields_to_check = (
            "childcare_type_arc_flagged",
            "criminal_record_check_arc_flagged",
            "childcare_training_arc_flagged",
            "first_aid_training_arc_flagged",
            "login_details_arc_flagged",
            "people_in_home_arc_flagged",
            "personal_details_arc_flagged",
            "references_arc_flagged",
            'your_children_arc_flagged'
        )
    elif childcare_type_record.zero_to_five and not application.own_children and not application.working_in_other_childminder_home:
        flagged_fields_to_check = (
            "childcare_type_arc_flagged",
            "criminal_record_check_arc_flagged",
            "childcare_training_arc_flagged",
            "first_aid_training_arc_flagged",
            "health_arc_flagged",
            "login_details_arc_flagged",
            "people_in_home_arc_flagged",
            "personal_details_arc_flagged",
            "references_arc_flagged"
        )
    elif not childcare_type_record.zero_to_five and application.own_children and application.working_in_other_childminder_home:
        flagged_fields_to_check = (
            "childcare_type_arc_flagged",
            "criminal_record_check_arc_flagged",
            "childcare_training_arc_flagged",
            "first_aid_training_arc_flagged",
            "login_details_arc_flagged",
            "personal_details_arc_flagged",
            "references_arc_flagged",
            'your_children_arc_flagged'
        )

    return flagged_fields_to_check


def set_review_fields_to_check(application, childcare_type_record):
    """
    Method to set the review fields to check
    :param application: an Application object
    :param childcare_type_record: a ChildcareType object
    :return: integer
    """
    # Default review fields to check
    review_fields_to_check = (
        'login_details_review',
        'personal_details_review',
        'childcare_type_review',
        'first_aid_review',
        'dbs_review',
        'childcare_training_review',
        'references_review'
    )

    if childcare_type_record.zero_to_five and not application.own_children and application.working_in_other_childminder_home:
        review_fields_to_check = (
            'login_details_review',
            'personal_details_review',
            'childcare_type_review',
            'first_aid_review',
            'dbs_review',
            'childcare_training_review',
            'health_review',
            'references_review'
        )
    elif childcare_type_record.zero_to_five and application.own_children and application.working_in_other_childminder_home:
        review_fields_to_check = (
            'login_details_review',
            'personal_details_review',
            'childcare_type_review',
            'first_aid_review',
            'dbs_review',
            'childcare_training_review',
            'health_review',
            'references_review',
            'your_children_review'
        )
    elif childcare_type_record.zero_to_five and application.own_children and not application.working_in_other_childminder_home:
        review_fields_to_check = (
            'login_details_review',
            'personal_details_review',
            'childcare_type_review',
            'first_aid_review',
            'dbs_review',
            'childcare_training_review',
            'health_review',
            'references_review',
            'your_children_review',
            'people_in_home_review'
        )
    elif not childcare_type_record.zero_to_five and not application.own_children and application.working_in_other_childminder_home:
        review_fields_to_check = (
            'login_details_review',
            'personal_details_review',
            'childcare_type_review',
            'first_aid_review',
            'dbs_review',
            'childcare_training_review',
            'references_review'
        )
    elif not childcare_type_record.zero_to_five and not application.own_children and not application.working_in_other_childminder_home:
        review_fields_to_check = (
            'login_details_review',
            'personal_details_review',
            'childcare_type_review',
            'first_aid_review',
            'dbs_review',
            'childcare_training_review',
            'references_review',
            'people_in_home_review'
        )
    elif not childcare_type_record.zero_to_five and application.own_children and not application.working_in_other_childminder_home:
        review_fields_to_check = (
            'login_details_review',
            'personal_details_review',
            'childcare_type_review',
            'first_aid_review',
            'dbs_review',
            'childcare_training_review',
            'references_review',
            'your_children_review',
            'people_in_home_review'
        )
    elif childcare_type_record.zero_to_five and not application.own_children and not application.working_in_other_childminder_home:
        review_fields_to_check = (
            'login_details_review',
            'personal_details_review',
            'childcare_type_review',
            'first_aid_review',
            'dbs_review',
            'childcare_training_review',
            'health_review',
            'references_review',
            'people_in_home_review'
        )
    elif not childcare_type_record.zero_to_five and application.own_children and application.working_in_other_childminder_home:
        review_fields_to_check = (
            'login_details_review',
            'personal_details_review',
            'childcare_type_review',
            'first_aid_review',
            'dbs_review',
            'childcare_training_review',
            'references_review',
            'your_children_review'
        )

    return review_fields_to_check


def set_number_of_tasks(application, childcare_type_record):
    """
    Method to set the total number of tasks in the right hand summary panel
    :param application: an Application object
    :param childcare_type_record: a ChildcareType object
    :return: integer
    """
    # Default total number of tasks
    number_of_tasks = 7

    if childcare_type_record.zero_to_five and not application.own_children and application.working_in_other_childminder_home:
        number_of_tasks = 8
    elif childcare_type_record.zero_to_five and application.own_children and application.working_in_other_childminder_home:
        number_of_tasks = 9
    elif childcare_type_record.zero_to_five and application.own_children and not application.working_in_other_childminder_home:
        number_of_tasks = 10
    elif not childcare_type_record.zero_to_five and not application.own_children and application.working_in_other_childminder_home:
        number_of_tasks = 7
    elif not childcare_type_record.zero_to_five and not application.own_children and not application.working_in_other_childminder_home:
        number_of_tasks = 8
    elif not childcare_type_record.zero_to_five and application.own_children and not application.working_in_other_childminder_home:
        number_of_tasks = 9
    elif childcare_type_record.zero_to_five and not application.own_children and not application.working_in_other_childminder_home:
        number_of_tasks = 9
    elif not childcare_type_record.zero_to_five and application.own_children and application.working_in_other_childminder_home:
        number_of_tasks = 8

    return number_of_tasks


@group_required(settings.ARC_GROUP)
def review(request):
    """
    Confirmation Page
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your App Review Confirmation template
    """
    application_id_local = request.GET["id"]
    application = Application.objects.get(application_id=application_id_local)
    app_ref = application.application_reference
    account = UserDetails.objects.get(application_id=application)
    login_id = account.pk
    first_name = ''

    # Get Application's related email and first_name to send an email.
    if UserDetails.objects.filter(login_id=login_id).exists():
        user_details = UserDetails.objects.get(login_id=login_id)
        email = user_details.email

        if ApplicantPersonalDetails.objects.filter(application_id=application_id_local).exists():
            personal_details = ApplicantPersonalDetails.objects.get(application_id=application_id_local)
            applicant_name = ApplicantName.objects.get(personal_detail_id=personal_details.personal_detail_id)
            first_name = applicant_name.first_name

    if all_complete(application_id_local, True):
        accepted_email(email, first_name, app_ref, application_id_local)

        # If successful
        release_application(request, application_id_local, 'ACCEPTED')

        # Get fresh version of application as it will have been updated in method call
        if Application.objects.filter(application_id=application_id_local).exists():
            application = Application.objects.get(application_id=application_id_local)
            application.date_accepted = datetime.now()
            application.save()

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
        returned_email(email, first_name, app_ref, link)

        # Copy Arc status' to Childminder App
        if Arc.objects.filter(pk=application_id_local):
            arc = Arc.objects.get(pk=application_id_local)
            app = Application.objects.get(pk=application_id_local)
            app.login_details_status = arc.login_details_review
            app.personal_details_status = arc.personal_details_review
            app.childcare_type_status = arc.childcare_type_review
            app.first_aid_training_status = arc.first_aid_review
            app.health_status = arc.health_review
            app.childcare_training_status = arc.childcare_training_review
            app.criminal_record_check_status = arc.dbs_review
            app.references_status = arc.references_review
            app.people_in_home_status = arc.people_in_home_review
            app.save()

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
    :return: True or False depending on whether all sections have been reviewed
    """
    if Arc.objects.filter(application_id=id):
        arc = Arc.objects.get(application_id=id)
        tasks = [arc.login_details_review, arc.childcare_type_review, arc.personal_details_review,
                 arc.first_aid_review, arc.childcare_training_review, arc.dbs_review, arc.people_in_home_review]
        zero_to_five = ChildcareType.objects.get(application_id=id).zero_to_five
        if zero_to_five:
            tasks.append(arc.health_review)
            tasks.append(arc.references_review)
        application = Application.objects.get(application_id=id)
        if application.own_children is True:
            tasks.append(arc.your_children_review)

        for i in tasks:

            if (i == 'NOT_STARTED' and not flag) or (i != 'COMPLETED' and flag):
                return False

        return True


# Add personalisation and create template
def accepted_email(email, first_name, ref, application_id):
    """
    Method to send an email using the Notify Gateway API
    :param email: string containing the e-mail address to send the e-mail to
    :param first_name: string first name
    :param ref: string ref
    :param application_id: application ID
    :return: HTTP response
    """
    if hasattr(settings, 'NOTIFY_URL'):
        email = str(email)

        childcare_type_record = ChildcareType.objects.get(application_id=application_id)

        # Send correct ARC accept next steps depending on whether the applicant applies for the Childcare Register only
        if childcare_type_record.zero_to_five is True:

            template_id = 'b973c5a2-cadd-46a5-baf7-beae65ab11dc'

        else:

            template_id = 'b3ae07da-3d14-4794-b989-9a15f961e4ee'

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


def children_address_initial_population(address_list):
    initial_data = []

    for address in address_list:
        temp_dict = {}
        table_id = address.child_address_id
        form_instance = ChildAddressForm()

        for field in form_instance.fields:
            try:

                if field[-8:] == 'comments':
                    field_name_local = field[:-9]
                    comment = (ArcComments.objects.filter(table_pk=table_id).get(field_name=field_name_local)).comment
                    temp_dict[field] = comment

                    # If a comment exists, set checkbox to True and show previously added comment.
                    temp_dict[field_name_local + '_declare'] = True

            except ArcComments.DoesNotExist:
                pass

        initial_data.append(temp_dict)

    return initial_data


def children_initial_population(person_list):
    initial_data = []

    for person in person_list:
        temp_dict = {}
        table_id = person.child_id
        form_instance = ChildForm()

        for field in form_instance.fields:
            try:

                if field[-8:] == 'comments':
                    field_name_local = field[:-9]
                    comment = (ArcComments.objects.filter(table_pk=table_id).get(field_name=field_name_local)).comment
                    temp_dict[field] = comment

                    # If a comment exists, set checkbox to True and show previously added comment.
                    temp_dict[field_name_local + '_declare'] = True

            except ArcComments.DoesNotExist:
                pass

        initial_data.append(temp_dict)

    return initial_data


@method_decorator(decorators, name='dispatch')
class PreviousRegistrationDetailsView(View):

    def get(self, request):
        application_id_local = request.GET["id"]
        form = PreviousRegistrationDetailsForm(id=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
        }

        return render(request, 'childminder_templates/add-previous-registration.html', variables)

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

            return render(request, 'childminder_templates/add-previous-registration.html', context=variables)


@method_decorator(decorators, name='dispatch')
class OtherPersonPreviousRegistrationDetailsView(View):

    def get(self, request):
        application_id_local = request.GET["id"]
        person_id = request.GET["person_id"]
        form = OtherPersonPreviousRegistrationDetailsForm(id=person_id)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'person_id': person_id,
        }

        return render(request, 'childminder_templates/add-previous-registration.html', context=variables)

    def post(self, request):
        application_id_local = request.POST["id"]
        person_id = request.POST["person_id"]
        person_record = AdultInHome.objects.get(adult_id=person_id)
        form = OtherPersonPreviousRegistrationDetailsForm(request.POST, id=person_id)

        if form.is_valid():
            app = Application.objects.get(pk=application_id_local)
            previous_registration = form.cleaned_data.get('previous_registration')
            individual_id = form.cleaned_data.get('individual_id')
            five_years_in_uk = form.cleaned_data.get('five_years_in_UK')

            if OtherPersonPreviousRegistrationDetails.objects.filter(person_id=person_record).exists():
                previous_reg_details = OtherPersonPreviousRegistrationDetails.objects.get(person_id=person_record)
            else:
                previous_reg_details = OtherPersonPreviousRegistrationDetails(person_id=person_record)

            previous_reg_details.previous_registration = previous_registration
            previous_reg_details.individual_id = individual_id
            previous_reg_details.five_years_in_UK = five_years_in_uk
            previous_reg_details.save()

            redirect_link = '/people/summary'
            return HttpResponseRedirect(settings.URL_PREFIX + redirect_link + '?id=' + application_id_local)

        else:
            variables = {
                'form': form,
                'application_id': application_id_local,
                'person_id': person_id,
            }

            return render(request, 'childminder_templates/add-previous-registration.html', context=variables)