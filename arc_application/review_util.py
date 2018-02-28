from .models import AdultInHome, ApplicantHomeAddress, ApplicantName, ApplicantPersonalDetails, Application, Arc, \
    ChildInHome, ChildcareType, CriminalRecordCheck, FirstAidTraining, HealthDeclarationBooklet, Reference, \
    UserDetails, ArcComments


def request_to_comment(table_key, table_name, user_request):
    """

    :param table_key: The applicants unique id for the table which the reviewer is currently reviewing
    :param table_name: The name of the table the reviewer is currently reviewing
    :param user_request: The dictionary containing the list of fields as keys, mapped to the result
    :return: Returns a list of what comment should be added for each field, blank signifies to do nothing
    """
    comment_list = []
    print(user_request)
    for param in user_request:
        print(param)
        # Finds all checkboxes sent in the request
        if param[-7:] == 'declare':
            # Grabs the existing comment if it exists, returns None otherwise
            try:
                existing_comment = ArcComments.objects.get(table_pk=table_key, field_name=param[:-8])
            except ArcComments.DoesNotExist:
                existing_comment = None

            print(user_request[param])
            # Checkboxes set to on when they are ticked, param will always be the name of a field
            if user_request[param] == 'on':
                field_name = param[:-8]
                comment = user_request[param.replace("declare", "comments")]
                flagged = True

            # For the case where a result has been previously flagged but now unflagged
            elif param not in user_request and existing_comment is not None:
                field_name = existing_comment.field_name
                comment = existing_comment.comment
                flagged = False

            else:
                field_name = param[:-8]
                comment = None
                flagged = False

            comment_list.append([table_key, table_name, field_name, comment, flagged])
        if param[-8:] == 'comments' and ((param[:-9]) + '_declare') not in user_request:
            print('Removed!')

    return comment_list
