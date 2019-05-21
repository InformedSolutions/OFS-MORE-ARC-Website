import json

from ...forms.adult_update_forms.adult_update_form import NewAdultForm
from ...services.db_gateways import HMGatewayActions
from ...models.arc import Arc

def new_adults_initial_population(adult_list):
    initial_data = []

    for adult in adult_list:
        temp_dict = {}

        table_id = adult["adult_id"]
        form_instance = NewAdultForm()

        for field in form_instance.fields:
            if field[-8:] == 'comments':
                field_name_local = field[:-9]
                response = HMGatewayActions().list('arc-comments', params={'table_pk': table_id, 'field_name': field_name_local})
                if response.status_code == 200:
                    comment = response.record[0]["comment"]
                    temp_dict[field] = comment

            if field[-7:] == 'declare':
                field_name_local = field[:-8]
                response = HMGatewayActions().list('arc-comments',
                                                      params={'table_pk': table_id, 'field_name': field_name_local})
                if response.status_code == 200:
                    checkbox = response.record[0]["flagged"]
                    temp_dict[field] = True

            if field == 'cygnum_relationship':
                temp_dict[field] = adult["cygnum_relationship_to_childminder"]

        initial_data.append(temp_dict)

    return initial_data

def request_to_comment(table_key, table_name, user_request, application_id):
    """
    Function for creating a ARC review comment from a page submission
    :param request: The inbound HTTP request from which the user will be extracted
    :param table_key: The applicants unique id for the table which the reviewer is currently reviewing
    :param table_name: The name of the table the reviewer is currently reviewing
    :param user_request: The dictionary containing the list of fields as keys, mapped to the result
    :return: Returns a list of what comment should be added for each field, blank signifies to do nothing
    """
    comment_list = []
    for param in user_request:
        # Finds all checkboxes sent in the request
        if 'declare' in param:

            if not user_request[param]:
                existing_comment_response = HMGatewayActions().list('arc-comments',params={'table_pk':table_key, 'field_name':param[:-8]})
                if existing_comment_response.status_code == 200:
                    review_id = existing_comment_response.record[0]['review_id']
                    HMGatewayActions().delete('arc-comments',params={'review_id': review_id})

            # Grabs the existing comment if it exists, returns None otherwise
            # Checkboxes set to on when they are ticked, param will always be the name of a field

            if user_request[param]:
                field_name = param[:-8]
                comment = user_request[param.replace("declare", "comments")]
                flagged = True
                comment_list.append([table_key, table_name, field_name, comment, flagged])

    return comment_list

def save_comments(request, comment_list, application_id, token_id):
    """
    Generic function for saving comments to database, once formatted by request_to_comments
    :param comment_list: List of comments as returned by request_to_comments
    :return: True: If function body executes without raising an error, return True to indicate this.
    """
    for single_comment in comment_list:
        defaults = {"table_pk": single_comment[0], "table_name": single_comment[1],
                    "field_name": single_comment[2], "comment": single_comment[3],
                    "flagged": single_comment[4], 'token_id': token_id, 'endpoint_name': 'adult'
                    }

        existing_comment_present = False
        existing_comment_response= HMGatewayActions().list('arc-comments', params={'table_pk':single_comment[0],
                                                                       'field_name':single_comment[2]})

        if existing_comment_response.status_code == 200:
            existing_comment_present = True
            existing_record = existing_comment_response.record[0]
            review_id = existing_record['review_id']
            comment = single_comment[3]

        if single_comment[2] == 'health_check_status':
            adult = HMGatewayActions().read('adult', {'adult_id':single_comment[0]})
            adult_record = adult.record
            adult_record['health_check_status'] = 'Started'
            adult_record['email_resent'] = 0
            HMGatewayActions().put('adult', adult_record)

        if existing_comment_present:
            update_comment = {
                'review_id': review_id,
                'comment': comment,
                'flagged': True
            }

            HMGatewayActions().put('arc-comments', params=update_comment)

        else:
            HMGatewayActions().create('arc-comments', params=defaults)

        #Audit field level change if not already tracked
        if not existing_comment_present:
            log_arc_flag_action(application_id, request.user.username, single_comment[2], 'adult')

    return True


def redirect_selection(request, default):
    """
    Selects redirect notifications for return to list links
    :param request: The incoming HTTP request
    :param default: The default link if no conditions have been met for extra logic
    :return:
    """
    redirect_link = default
    if 'return_to_list' in request.POST.keys():
        redirect_link = request.POST['return_to_list']
    elif 'previous_registration_details' in request.POST.keys():
        redirect_link = request.POST['previous_registration_details']
    return redirect_link


def log_arc_flag_action(application_id, arc_user, flagged_field, verbose_task_name):
    extra_data = {
        'user_type': 'reviewer',
        'formatted_field': flagged_field.replace("_", " "),
        'action': 'flagged by',
        'entity': 'application',
        'task_name': verbose_task_name
    }

    HMGatewayActions().create('timeline-log',
                                 params={
                                     'object_id': application_id,
                                     'user': arc_user,
                                     'template': 'timeline_logger/application_field_flagged.txt',
                                     'extra_data': json.dumps(extra_data)
                                 })

    return None