from arc_application.services.db_gateways import NannyGatewayActions


def parse_date_of_birth(dob_str):
    '''
    Converts dob_str to it's corresponding parts.
    :param dob_str: The date of birth in assumed format YYYY-MM-DD
    :return: A list containing strings birth_year, birth_month and birth_day, in that order.
    '''

    return dob_str.split('-')


def nanny_all_completed(arc_application, application_id):
    """
    Returns a boolean representing if all tasks have been reviewed AND marked as 'COMPLETED'.
    :param arc_application: A direct reference to an arc_application.
    :return: Boolean only.
    """
    return check_all_task_statuses(arc_application, application_id, ['COMPLETED'])


def nanny_all_reviewed(arc_application, application_id):
    """
    Returns a boolean representing if all tasks have been reviewed AND marked as 'COMPLETED'.
    :param arc_application: A direct reference to an arc_application.
    :return: Boolean only.
    """
    return check_all_task_statuses(arc_application, application_id, ['FLAGGED', 'COMPLETED'])


def get_your_children_status(application_id):
    """
    Helper function to check if the application contains the 'Your children' task
    :return: True or False depending on if the task is activated
    """
    try:
        your_children_record = NannyGatewayActions().read('applicant-personal-details',
                                                    params={'application_id': application_id}).record['your_children']
        return your_children_record

    except AttributeError:
        return False


def check_all_task_statuses(arc_application, application_id, status_list):
    """
    Iterates through the arc_application task's statuses and compares each task status to a given status.
    :param arc_application: A direct reference to an arc_application.
    :param status_list: A list of statuses to check against, e.g ['NOT_STARTED', 'COMPLETED']
    :return: Boolean only.
    """

    field_list = [arc_application.login_details_review,
                  arc_application.personal_details_review,
                  arc_application.childcare_address_review,
                  arc_application.first_aid_review,
                  arc_application.childcare_training_review,
                  arc_application.dbs_review,
                  arc_application.insurance_cover_review,
                  ]

    if get_your_children_status(application_id):
        field_list.append(arc_application.your_children_review, )

    for i in field_list:
        if i not in status_list:
            return False

    return True
