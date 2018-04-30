from .models import ArcComments
from urllib.parse import urlencode
from django.core.urlresolvers import reverse

def request_to_comment(table_key, table_name, user_request):
    """

    :param table_key: The applicants unique id for the table which the reviewer is currently reviewing
    :param table_name: The name of the table the reviewer is currently reviewing
    :param user_request: The dictionary containing the list of fields as keys, mapped to the result
    :return: Returns a list of what comment should be added for each field, blank signifies to do nothing
    """
    comment_list = []
    for param in user_request:
        # Finds all checkboxes sent in the request
        if 'declare' in param:
            # Grabs the existing comment if it exists, returns None otherwise
            # Checkboxes set to on when they are ticked, param will always be the name of a field

            if user_request[param] == True:
                field_name = param[:-8]
                comment = user_request[param.replace("declare", "comments")]
                flagged = True
                comment_list.append([table_key, table_name, field_name, comment, flagged])

            if user_request[param] == False:
                field_name = param[:-8]
                flagged = False
                try:
                    existing_comment = ArcComments.objects.get(table_pk=table_key, field_name=param[:-8])
                    existing_comment.delete()
                except ArcComments.DoesNotExist:
                    pass
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


def save_comments(comment_list):
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
            # If a field already has a comment, this will update it, otherwise it will use the 'default' dictionary
            comment_record, created = ArcComments.objects.update_or_create(table_pk=single_comment[0],
                                                                           field_name=single_comment[2],
                                                                           defaults=defaults)
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
    return redirect_link


def build_url(*args, **kwargs):
    get = kwargs.pop('get', {})
    url = reverse(*args, **kwargs)
    if get:
        url += '?' + urlencode(get)
    return url