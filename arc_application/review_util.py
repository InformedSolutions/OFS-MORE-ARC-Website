from timeline_logger.models import TimelineLog

from .models import ArcComments, Application, AdultInHome
from urllib.parse import urlencode
from django.core.urlresolvers import reverse


def request_to_comment(table_key, table_name, user_request):
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
                try:
                    existing_comment = ArcComments.objects.get(table_pk=table_key, field_name=param[:-8])
                    existing_comment.delete()
                except ArcComments.DoesNotExist:
                    pass

            # Grabs the existing comment if it exists, returns None otherwise
            # Checkboxes set to on when they are ticked, param will always be the name of a field

            if user_request[param]:
                field_name = param[:-8]
                comment = user_request[param.replace("declare", "comments")]
                flagged = True
                comment_list.append([table_key, table_name, field_name, comment, flagged])

    return comment_list


def populate_initial_values(self):
    """
    Function to populate the existing forms with their flagged status and the associated comment if so
    :param self:  The form object to be populated
    :return: Object is passed by reference, therefore nothing needs to be passed
    """
    for field_string in self.fields:
        if field_string[-7:] == 'declare':
            try:
                comment_object = ArcComments.objects.get(table_pk__in=self.table_keys, field_name=field_string[:-8])
                self.fields[field_string].initial = comment_object.flagged

            except ArcComments.DoesNotExist:
                pass
        elif field_string[-8:] == 'comments':
            try:
                comment_object = ArcComments.objects.get(table_pk__in=self.table_keys, field_name=field_string[:-9])
                self.fields[field_string].initial = comment_object.comment
            except ArcComments.DoesNotExist:
                pass


def save_comments(request, comment_list):
    """
    Generic funciton for saving comments to database, once formatted by request_to_comments
    :param comment_list:
    :return:
    """
    try:
        for single_comment in comment_list:
            defaults = {"table_pk": single_comment[0], "table_name": single_comment[1],
                        "field_name": single_comment[2], "comment": single_comment[3],
                        "flagged": single_comment[4]
                        }

            existing_comment_present = ArcComments.objects.filter(table_pk=single_comment[0],
                                                                           field_name=single_comment[2]).count() > 0

            if single_comment[2] == 'health_check_status':
                adult = AdultInHome.objects.get(adult_id=single_comment[0])
                adult.health_check_status = 'Flagged'
                adult.save()

            # If a field already has a comment, this will update it, otherwise it will use the 'default' dictionary
            ArcComments.objects.update_or_create(table_pk=single_comment[0],
                                                                           field_name=single_comment[2],
                                                                           defaults=defaults)

            # Audit field level change if not already tracked
            if not existing_comment_present:
                application_id = request.POST['id']
                application = Application.objects.get(application_id=application_id)
                TimelineLog.objects.create(
                    content_object=application,
                    user=request.user,
                    template='timeline_logger/application_field_flagged.txt',
                    extra_data={
                        'user_type': 'reviewer',
                        'formatted_field': single_comment[2].replace("_", " "),
                        'action': 'flagged by',
                        'entity': 'application',
                        'task_name': get_task_name(single_comment[1], single_comment[2])
                    }
                )

        return True
    except:
        return False


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


def build_url(*args, **kwargs):
    get = kwargs.pop('get', {})
    url = reverse(*args, **kwargs)
    if get:
        url += '?' + urlencode(get)
    return url


def get_task_name(table_name, field_name):
    """
    Helper method to derive a task name from a table modification
    :param table_name: the name of the table against which an update is being performed
    :param table_name: the name of the field being updated
    :return: a task name based on the table adjusted
    """
    if table_name == "USER_DETAILS":
        return 'Your login details'

    if table_name == "APPLICANT_NAME" \
            or table_name == "APPLICANT_PERSONAL_DETAILS" \
            or table_name == "APPLICANT_HOME_ADDRESS":
        return 'Your personal details'

    if table_name == "FIRST_AID_TRAINING":
        return 'First aid training'

    if table_name == "CRIMINAL_RECORD_CHECK":
        return 'Criminal record (DBS) check'

    if field_name == "adults_in_home" or field_name == "children_in_home":
        return 'People in your home'

    if table_name == "REFERENCE":
        return 'References'

    if table_name == "EYFS":
        return 'Early years training'


def reset_declaration(application):
    """
    Method to reset the declaration status to To Do if a task is updated
    :param application: current application
    """
    if application.declarations_status == 'COMPLETED':
        application.declarations_status = 'NOT_STARTED'
        application.share_info_declare = None
        application.display_contact_details_on_web = None
        application.suitable_declare = None
        application.information_correct_declare = None
        application.change_declare = None
        application.save()