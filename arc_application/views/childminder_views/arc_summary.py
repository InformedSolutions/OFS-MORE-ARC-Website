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
from .childminder_utils import get_application_summary_variables, load_json, add_comments

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
        json = add_comments(json, application_id_local, add_change_links=False)
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