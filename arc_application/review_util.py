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
        # Finds all checkboxes sent in the request
        if param[-7:] == 'declare':
            # Grabs the existing comment if it exists, returns None otherwise


            # Checkboxes set to on when they are ticked, param will always be the name of a field
            if user_request[param] == 'on':
                field_name = param[:-8]
                comment = user_request[param.replace("declare", "comments")]
                flagged = True

            comment_list.append([table_key, table_name, field_name, comment, flagged])

        # For the case where a result has been previously flagged but now unflagged
        if param[-8:] == 'comments' and ((param[:-9]) + '_declare') not in user_request:
            try:
                existing_comment = ArcComments.objects.get(table_pk=table_key, field_name=param[:-9])
            except ArcComments.DoesNotExist:
                existing_comment = None
            if existing_comment is not None:
                field_name = existing_comment.field_name
                comment = existing_comment.comment
                flagged = False
                comment_list.append([table_key, table_name, field_name, comment, flagged])

    return comment_list

def populate_initial_values(self):
    for field_string in self.fields:
        if field_string[-7:] == 'declare':
            try:
                comment_object = ArcComments.objects.get(table_pk=self.table_key, field_name=field_string[:-8])
                self.fields[field_string].initial = comment_object.flagged
            except ArcComments.DoesNotExist:
                pass
        elif field_string[-8:] == 'comments':
            try:
                comment_object = ArcComments.objects.get(table_pk=self.table_key, field_name=field_string[:-9])
                self.fields[field_string].initial = comment_object.comment
            except ArcComments.DoesNotExist:
                pass
