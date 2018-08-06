def parse_date_of_birth(dob_str):
    '''
    Converts dob_str to it's corresponding parts.
    :param dob_str: The date of birth in assumed format YYYY-MM-DD
    :return: A dictionary containing strings birth_year, birth_month and birth_day.
    '''

    # TODO Overwrite this, use string.split instead. Also, change to tuples.

    if len(dob_str) == 10:
        birth_year = dob_str[:4]
        birth_month = dob_str[5:-3]
        birth_day = dob_str[-2:]

        dob_dict = {
            'birth_year': birth_year,
            'birth_month': birth_month,
            'birth_day': birth_day
        }

        return dob_dict

    else:
        raise ValueError("{0} is not a valid dob_str, the length should be 10 but it is {1}".format(dob_str, len(dob_str)))


def nanny_all_completed(arc_application):
    return check_all_task_statuses(arc_application, 'COMPLETED')


def nanny_all_reviewed(arc_application):

    return check_all_task_statuses(arc_application, ['FLAGGED', 'COMPLETED'])


def check_all_task_statuses(arc_application, status_list):

    field_list = [arc_application.login_details_review,
                  arc_application.personal_details_review,
                  arc_application.childcare_address_review,
                  arc_application.first_aid_review,
                  arc_application.childcare_training_review,
                  arc_application.dbs_review,
                  arc_application.insurance_cover_review,
                  ]
    
    for i in field_list:
        if i not in status_list:
            return False
    
    return True