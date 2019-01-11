from arc_application.models import Application, ChildcareType, Arc


def get_application(app_id):
    # TODO Make this function more robust and move to a Services folder
    return Application.objects.get(application_id=app_id)


def get_childcare_type_record(app_id):
    # TODO Make this function more robust and move to a Services folder
    return ChildcareType.objects.get(application_id=app_id)


def get_show_people_in_the_home(app_id):
    application = get_application(app_id)
    ctr = get_childcare_type_record(app_id)

    return __get_show_people_in_the_home_no_db(application, ctr)


def __get_show_people_in_the_home_no_db(application, childcare_type_record):
    return __find_in_flagged_fields('people_in_home_arc_flagged', application, childcare_type_record)


def get_show_references(app_id):
    application = get_application(app_id)
    ctr = get_childcare_type_record(app_id)

    return __get_show_references_no_db(application, ctr)


def __get_show_references_no_db(application, childcare_type_record):
    return __find_in_flagged_fields("references_arc_flagged", application, childcare_type_record)


def __find_in_flagged_fields(arc_flagged_str, application, childcare_type_record):
    flagged_fields_to_check = __get_flagged_fields_to_check_no_db(application, childcare_type_record)

    return arc_flagged_str in flagged_fields_to_check


def get_flagged_fields_to_check(app_id):
    application = get_application(app_id)
    ctr = get_childcare_type_record(app_id)

    return __get_flagged_fields_to_check_no_db(application, ctr)


def __get_flagged_fields_to_check_no_db(application, childcare_type_record):
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
            'your_children_arc_flagged'
        )

    return flagged_fields_to_check


def get_review_fields_to_check(app_id):
    application = get_application(app_id)
    ctr = get_childcare_type_record(app_id)

    return __get_review_fields_to_check_no_db(application, ctr)


def __get_review_fields_to_check_no_db(application, childcare_type_record):
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
        )
    elif not childcare_type_record.zero_to_five and not application.own_children and not application.working_in_other_childminder_home:
        review_fields_to_check = (
            'login_details_review',
            'personal_details_review',
            'childcare_type_review',
            'first_aid_review',
            'dbs_review',
            'childcare_training_review',
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
            'your_children_review'
        )

    return review_fields_to_check


def get_number_of_tasks(application, childcare_type_record):
    """
    Method to set the total number of tasks in the right hand summary panel
    :param application: an Application object
    :param childcare_type_record: a ChildcareType object
    :return: integer
    """
    flagged_fields_to_check = __get_flagged_fields_to_check_no_db(application, childcare_type_record)

    return len(flagged_fields_to_check)


def all_complete(app_id, flag):
    """
    Check the status of all sections
    :param app_id: Application Id
    :return: True or False depending on whether all sections have been reviewed
    """
    review_fields_to_check = get_review_fields_to_check(app_id)
    arc = Arc.objects.get(application_id=app_id)

    task_status_list = [getattr(arc, task_arc_flagged_str) for task_arc_flagged_str in review_fields_to_check]

    # TODO Refactor me to more intuitively explain the existence of flag
    for i in task_status_list:
        if (i == 'NOT_STARTED' and not flag) or (i != 'COMPLETED' and flag):
            return False

    return True
