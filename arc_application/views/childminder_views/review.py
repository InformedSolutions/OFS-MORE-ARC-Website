import base64
import time
from datetime import datetime

import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View

from arc_application.childminder_task_util import all_complete
from arc_application.decorators import group_required, user_assigned_application
from arc_application.forms.childminder_forms.form import AdultInYourHomeForm, ChildInYourHomeForm, \
    OtherPersonPreviousRegistrationDetailsForm
from arc_application.forms.childminder_forms.form import PreviousRegistrationDetailsForm, ChildForm, ChildAddressForm
from arc_application.magic_link import generate_magic_link
from arc_application.notify import send_email
from arc_application.views.base import release_application

from django.core import serializers
from ...messaging import SQSHandler

from ...models import ApplicantName, ApplicantPersonalDetails, Application, Arc, ArcComments, ChildcareType, ChildcareTraining, UserDetails, OtherPersonPreviousRegistrationDetails, PreviousName, \
PreviousRegistrationDetails, PreviousAddress, HealthDeclarationBooklet, FirstAidTraining, Reference, CriminalRecordCheck, ChildInHome, ApplicantHomeAddress, AdultInHome, \
HealthCheckHospital, HealthCheckSerious, HealthCheckCurrent

decorators = [login_required, group_required(settings.ARC_GROUP), user_assigned_application]

sqs_handler = SQSHandler(settings.APPLICATION_QUEUE_NAME)


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
        personalisation = {'first_name': first_name, 'ref': app_ref}
        accepted_email(email, first_name, app_ref, application_id_local)
        send_survey_email(email, personalisation, application)

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

        export = __create_full_application_export(application_id_local)
        sqs_handler.send_message(export)

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


def send_survey_email(email, personalisation, application):
    """
    Sends an email if
    :param email: Applicant's email string
    :param personalisation: Applicant's details dictionary, presumed firstName and ref
    :param application: Application model instance
    :return: Void
    """
    survey_template_id = '90580388-f10d-440a-b900-4d5f948112a5'
    send_email(email, personalisation, survey_template_id)


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
                    temp_dict[field] = True

                if adult and field == 'cygnum_relationship':
                    temp_dict[field] = person.cygnum_relationship_to_childminder

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


def __create_full_application_export(application_id):
    """
    Method for exporting a full application in a dictionary format
    :param application_id: the identifier of the application to be exported
    :return: a dictionary export of an application
    """

    export = {}

    application = Application.objects.filter(application_id=application_id)
    export['application'] = serializers.serialize('json', list(application))

    adults_in_home = AdultInHome.objects.filter(application_id=application_id).order_by('adult')
    adults_in_home_export = []
    export['adults_in_home'] = serializers.serialize('json', list(adults_in_home))

    # Iterate adults in home, appending prior names and addresses

    for adult_in_home in adults_in_home:
        previous_name = PreviousName.objects.filter(person_id=adult_in_home.pk)
        previous_address = PreviousAddress.objects.filter(person_id=adult_in_home.pk)
        serious_illness = HealthCheckSerious.objects.filter(person_id=adult_in_home.pk)
        hospital_admissions = HealthCheckHospital.objects.filter(person_id=adult_in_home.pk)
        current_illnesses = HealthCheckCurrent.objects.filter(person_id=adult_in_home.pk)

        adults_in_home_export.append({
            'adult': adult_in_home.adult,
            'previous_names': serializers.serialize('json', list(previous_name)),
            'previous_address': serializers.serialize('json', list(previous_address)),
            'serious_illness': serializers.serialize('json', list(serious_illness)),
            'hospital_admissions': serializers.serialize('json', list(hospital_admissions)),
            'current_illnesses': serializers.serialize('json', list(current_illnesses))
        })

    export['health'] = adults_in_home_export

    applicant_name = ApplicantName.objects.filter(application_id=application_id)
    export['applicant_name'] = serializers.serialize('json', applicant_name)

    applicant_personal_details = ApplicantPersonalDetails.objects.filter(application_id=application_id)
    export['applicant_personal_details'] = serializers.serialize('json', list(applicant_personal_details))

    applicant_home_address = ApplicantHomeAddress.objects.filter(application_id=application_id)
    export['applicant_home_address'] = serializers.serialize('json', list(applicant_home_address))

    child_in_home = ChildInHome.objects.filter(application_id=application_id)
    export['child_in_home'] = serializers.serialize('json', list(child_in_home))

    childcare_type = ChildcareType.objects.filter(application_id=application_id)
    export['childcare_type'] = serializers.serialize('json', list(childcare_type))

    criminal_record_check = CriminalRecordCheck.objects.filter(application_id=application_id)
    export['criminal_record_check'] = serializers.serialize('json', list(criminal_record_check))

    eyfs = ChildcareTraining.objects.filter(application_id=application_id)
    export['eyfs'] = serializers.serialize('json', list(eyfs))

    first_aid_training = FirstAidTraining.objects.filter(application_id=application_id)
    export['first_aid_training'] = serializers.serialize('json', list(first_aid_training))

    health_declaration_booklet = HealthDeclarationBooklet.objects.filter(application_id=application_id)
    export['health_declaration_booklet'] = serializers.serialize('json', list(health_declaration_booklet))

    previous_registration_details = PreviousRegistrationDetails.objects.filter(application_id=application_id)
    export['previous_name'] = serializers.serialize('json', list(previous_registration_details))

    references = Reference.objects.filter(application_id=application_id)
    export['references'] = serializers.serialize('json', list(references))

    user_details = UserDetails.objects.filter(application_id=application_id)
    export['user_details'] = serializers.serialize('json', list(user_details))

    # Create document exports

    documents = {}

    # Create endpoint URL location
    eyc_endpoint = reverse('application_summary_pdf') + '?id=' + application_id

    # Retrieve document
    file_result = requests.get(eyc_endpoint, allow_redirects=True)
    base64_string = str(base64.b64encode(file_result.content).decode("utf-8"))

    documents['EYC'] = base64_string

    if len(adults_in_home):

        adult_documents = {}

        for adult in adults_in_home:
            endpoint = reverse('application_summary_pdf_adult') + '?id=' \
                       + application_id + '&adult_id=' + adult.adult_id

            # Retrieve document
            file_result = requests.get(endpoint, allow_redirects=True)
            base64_string = str(base64.b64encode(file_result.content).decode("utf-8"))

            adult_document_object = {
                "adult_id": adult.adult_id,
                "document": base64_string,
            }

            adult_documents.update(adult_document_object)

        documents['EY2'] = adult_documents

    export['documents'] = documents

    return export
