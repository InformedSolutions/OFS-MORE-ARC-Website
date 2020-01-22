from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from timeline_logger.models import TimelineLog
import logging
from ...decorators import group_required, user_assigned_application
from ...models import *
from ...utils import has_group
from .childminder_utils import get_application_summary_variables, load_json


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
    'Known to council social services?': 'own_children',
    'Training organisation': 'first_aid_training_organisation',
    'first_aid_training_course': 'title_of_training_course',
    'first_aid_date': 'course_date',
    'eyfs_course_name': 'eyfs_course_name',
    'eyfs_course_date': 'eyfs_course_date',
    'Provide a Health Declaration Booklet?': 'health_submission_consent',
    'DBS certificate number': 'dbs_certificate_number',
    'Known to council social services in regards to their own children?': 'known_to_council',
    'reasons_known_health_check': 'reasons_known_to_council_health_check',
    'Do you have any criminal cautions or convictions?': 'cautions_convictions',
    'Does anyone aged 16 or over live or work in your home?': 'adults_in_home',
    'Do children under 16 live in the home?': 'children_in_home',
    'known_personal_details': 'known_to_social_services',
    'reasons_known_personal_details': 'reasons_known_to_social_services',
    'Full name': 'full_name',
    'How they know you': 'relationship',
    'Known for': 'time_known',
    'address': 'address',
    'Phone number': 'phone_number',
    'Email address': 'email_address',
    'What type of childcare training have you completed?': 'childcare_training',
    'Have you lived outside of the UK in the last 5 years?': 'lived_abroad',
    'Have you lived or worked on a British military base outside of the UK in the last 5 years?': 'military_base',
    'British Military Base': 'military_base',
    'Ofsted DBS': 'capita',
    'Is it dated within the last 3 months?': 'within_three_months',
    'Is it an enhanced DBS check for home-based childcare?': 'enhanced_check',
    'Known to council social Services?': 'known_to_social_services',

    # PITH
    'Health questions status': 'health_check_status',
    'Name': 'full_name',
    'Date of birth': 'date_of_birth',
    'Relationship': 'relationship',
    'Email': 'email',
    'Lived abroad in the last 5 years?': 'lived_abroad',
    'Lived or worked in British military base in the last 5 years?': 'military_base',
    'Did they get their DBS check from the Ofsted DBS application website?': 'capita',
    'Enhanced DBS check for home-based childcare?': 'enhanced_check',
    'On the update service?': 'on_update',
    'known_pith': 'known_to_social_services_pith',
    'reasons_known_pith': 'reasons_known_to_social_services_pith',
}

# Initiate logging
log = logging.getLogger('')

@login_required
@group_required(settings.ARC_GROUP)
@user_assigned_application
def arc_summary(request):
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        variables = get_application_summary_variables(application_id_local)
        log.debug("Rendering arc summary page")

        if application.working_in_other_childminder_home is False:
            ordered_models.append(AdultInHome)
            ordered_models.append(Application)
            ordered_models.append(ChildInHome)
        zero_to_five = ChildcareType.objects.get(application_id=application_id_local).zero_to_five

        if zero_to_five:
            ordered_models.insert(6, HealthDeclarationBooklet)
            ordered_models.append(Reference)
        json = load_json(application_id_local, ordered_models, False)
        json = add_comments(json, application_id_local)

        application_reference = application.application_reference
        publish_details = application.publish_details

        variables = {
            'json': json,
            'application_id': application_id_local,
            'application_reference': application_reference,
            'publish_details': publish_details
        }
        return render(request, 'childminder_templates/arc-summary.html', variables)

    elif request.method == 'POST':
        application_id_local = request.POST["id"]
        status = Arc.objects.get(pk=application_id_local)
        status.declaration_review = 'COMPLETED'
        status.save()
        log.debug("Handling submissions for arc summary page")
        return HttpResponseRedirect(
            reverse('review') + '?id=' + application_id_local
        )


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
            log.debug("Conditional logic: Show people in the home tables")
            ordered_models.append(AdultInHome)
            ordered_models.append(Application)
            ordered_models.append(ChildInHome)
        zero_to_five = ChildcareType.objects.get(application_id=application_id_local).zero_to_five
        if zero_to_five:
            ordered_models.insert(6, HealthDeclarationBooklet)
            ordered_models.append(Reference)
            log.debug("Conditional logic: Show health declarations and references tables")

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

        publish_details = application.publish_details

        variables = {
            'json': json,
            'application_id': application_id_local,
            'application_reference': application.application_reference or None,
            'cc_user': cc_user,
            'publish_details': publish_details
        }
        log.debug("Rendering search summary page")
        return render(request, 'childminder_templates/search-summary.html', variables)

    elif request.method == 'POST':
        application_id_local = request.POST["id"]
        status = Arc.objects.get(pk=application_id_local)
        status.declaration_review = 'COMPLETED'
        status.save()
        log.debug("Handling submissions for arc summary")
        return HttpResponseRedirect(settings.URL_PREFIX + '/comments?id=' + application_id_local)
