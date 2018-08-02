import time
from datetime import datetime
import uuid

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View

from arc_application.models import AdultInHome
from arc_application.forms.childminder_forms.form import PreviousRegistrationDetailsForm, OtherPersonPreviousRegistrationDetailsForm
from arc_application.forms.childminder_forms.form import AdultInYourHomeForm, ChildInYourHomeForm
from arc_application.magic_link import generate_magic_link
from arc_application.models import PreviousRegistrationDetails, OtherPersonPreviousRegistrationDetails
from arc_application.models import ApplicantName, ApplicantPersonalDetails, Application, Arc, ArcComments, ChildcareType, UserDetails
from arc_application.views.base import release_application
from arc_application.notify import send_email
from arc_application.decorators import group_required, user_assigned_application

from arc_application.db_gateways import IdentityGatewayActions, NannyGatewayActions
from arc_application.views.nanny_views.nanny_view_helpers import parse_date_of_birth

decorators = [login_required, group_required(settings.ARC_GROUP), user_assigned_application]

@login_required
@group_required(settings.ARC_GROUP)
@user_assigned_application
def nanny_task_list(request):
    """
    Generates the full task list for ARC users
    :param request:  The Http request directed to the view
    :return: The task list page with the associated context
    """

    # If the user has signed in and is a member of the ARC group
    if request.method == 'GET':
        application_id = request.GET['id']


        idg_actions = IdentityGatewayActions()
        nanny_actions = NannyGatewayActions()
        #test = identity_actions.read('user', params={'application_id': application_id})

        application = nanny_actions.read('application', params={'application_id': application_id}).record
        arc_application = Arc.objects.get(application_id=application_id)
        personal_details_record = nanny_actions.read('applicant-personal-details', params={'application_id': application_id}).record

        review_fields_to_check = (
            'login_details_review',
            'personal_details_review',
            'childcare_address_review',
            'first_aid_review',
            'childcare_training_review',
            'dbs_review',
            'insurance_cover_review'
        )

        flagged_fields_to_check = (
            'login_details_arc_flagged',
            'personal_details_arc_flagged',
            'childcare_address_arc_flagged',
            'first_aid_training_arc_flagged',
            'childcare_training_arc_flagged',
            'criminal_record_check_arc_flagged',
            'insurance_cover_arc_flagged'
        )

        review_count = sum([1 for field in review_fields_to_check if getattr(arc_application, field) == 'COMPLETED'])
        review_count += sum([1 for field in flagged_fields_to_check if application[field]])

        # Load review status
        dob_str = personal_details_record['date_of_birth']
        birth_dict = parse_date_of_birth(dob_str)

        application_status_context = {
            'application_id': application_id,
            'application_reference': application['application_reference'],
            'first_name': personal_details_record['first_name'],
            'middle_names': personal_details_record['middle_names'],
            'last_name': personal_details_record['last_name'],
            'review_count': review_count,
            'login_details_status': arc_application.login_details_review,
            'personal_details_status': arc_application.personal_details_review,
            'childcare_address_status': arc_application.childcare_address_review,
            'first_aid_status': arc_application.first_aid_review,
            'childcare_training_status': arc_application.childcare_training_review,
            'dbs_status': arc_application.dbs_review,
            'insurance_cover_status': arc_application.insurance_cover_review,
            'birth_day': int(birth_dict['birth_day']),
            'birth_month': int(birth_dict['birth_month']),
            'birth_year': int(birth_dict['birth_year']),
            'all_complete': nanny_all_complete(application_id, False)
        }

    return render(request, 'nanny_templates/nanny-task-list.html', application_status_context)


def nanny_all_complete(id, flag):
    """
    Check the status of all sections
    :param id: Application Id
    :return: True or False depending on whether all sections have been reviewed
    """

    #TODO: Redo this function.

    if Arc.objects.filter(application_id=id):
        arc = Arc.objects.get(application_id=id)
        list = [arc.login_details_review,
                arc.personal_details_review,
                arc.childcare_address_review,
                arc.first_aid_review,
                arc.childcare_training_review,
                arc.dbs_review,
                arc.insurance_cover_review,
        ]

        for i in list:
            if (i == 'NOT_STARTED' and not flag) or (i != 'COMPLETED' and flag):
                return False

        return True

    else:
        return False