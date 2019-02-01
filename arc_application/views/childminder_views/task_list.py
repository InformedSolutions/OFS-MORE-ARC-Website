from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from arc_application.childminder_task_util import get_show_people_in_the_home, get_number_of_tasks, \
    __get_flagged_fields_to_check_no_db, all_complete, __get_review_fields_to_check_no_db, get_show_references
from arc_application.decorators import group_required, user_assigned_application
from arc_application.models import ApplicantName, ApplicantPersonalDetails, Application, Arc, ChildcareType

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

        review_fields_to_check = __get_review_fields_to_check_no_db(application, childcare_type_record)

        flagged_fields_to_check = __get_flagged_fields_to_check_no_db(application, childcare_type_record)

        review_count = sum([1 for field in review_fields_to_check if getattr(arc_application, field) == 'COMPLETED'])
        review_count += sum([1 for field in flagged_fields_to_check if getattr(application, field)])

        # Set total number of tasks in right-hand side overview box
        number_of_tasks = get_number_of_tasks(application, childcare_type_record)

        show_people_in_the_home = get_show_people_in_the_home(application_id)
        show_references = get_show_references(application_id)

        all_complete_val = all_complete(application_id, False)

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
            'all_complete': all_complete_val,
            'number_of_tasks': number_of_tasks,
            'own_children': application.own_children,
            'working_in_other_childminder_home': application.working_in_other_childminder_home,
            'show_people_in_the_home': show_people_in_the_home,
            'show_references': show_references
        }

    return render(request, 'childminder_templates/task-list.html', application_status_context)
