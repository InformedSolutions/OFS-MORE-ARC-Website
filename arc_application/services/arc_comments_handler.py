import abc
import json

from arc_application.models import Arc
from .db_gateways import NannyGatewayActions


class ARCCommentsProcessor:
    """
    'Chain of responsibility' class for handling ARC comments.
    """
    @staticmethod
    def process_comments(request, form_class, verbose_task_name):
        """
        Entrance to processing pipeline.
        Acts as interface to ARCCommentsHandler for clients.
        :return Bool: True if ARC comments were saved, else False.
        """
        one_to_one_handler = OneToOneARCCommentsHandler()
        many_to_one_handler = ManyToOneARCCommentsHandler(one_to_one_handler)
        formset_handler = FormSetARCCommentsHandler(many_to_one_handler)
        return formset_handler.handle_comments(request, form_class, verbose_task_name)


class ARCCommentsHandler(metaclass=abc.ABCMeta):
    """
    Abstract Base Class which all ARC Comments Handler classes must implement
    """
    def __init__(self, successor=None):
        self._successor = successor

    @abc.abstractmethod
    def handle_comments(self, request, form_class, verbose_task_name):
        pass


class FormSetARCCommentsHandler(ARCCommentsHandler):
    """
    ARC Comments Handler for a Formset instance.
    """
    def handle_comments(self, request, form_class, verbose_task_name):
        if hasattr(form_class(), 'management_form'):  # If it is a FormSet instance.
            if self.has_management_form_data(request):  # If management form data absent, do nothing.
                for form in form_class(request.POST).forms:
                    return any([self._successor.handle_comments(request, form, verbose_task_name)])
            else:
                pass
        else:
            return self._successor.handle_comments(request, form_class, verbose_task_name)

    @staticmethod
    def has_management_form_data(request):
        management_form_data_fields = (
            'form-TOTAL_FORMS',
            'form-INITIAL_FORMS',
            'form-MIN_NUM_FORMS',
        )

        return all([field in request.POST for field in management_form_data_fields])


class ManyToOneARCCommentsHandler(ARCCommentsHandler):
    """
    ARC Comments Handler for endpoints with a Many-To-One relationship to the APPLICATION table.
    """
    def handle_comments(self, request, form_class, verbose_task_name):
        endpoint = form_class.api_endpoint_name
        pk_field_name = NannyGatewayActions().get_endpoint_pk(endpoint)

        # If application_id is the primary key for the db_table, then that table forms a one-to-one relation with the
        # Application table.
        # If so, then ManyToOneARCCommentsHandler defers to its successor.

        if pk_field_name == 'application_id':
            return self._successor.handle_comments(request, form_class, verbose_task_name)
        else:
            application_id = request.GET['id']
            endpoint = form_class.api_endpoint_name
            pk_field_name = NannyGatewayActions().get_endpoint_pk(endpoint)

            records = NannyGatewayActions().list(endpoint, params={'application_id': application_id}).record

            flagged_fields = False

            for index, record in enumerate(records):
                relevant_data = dict((key[7:], value) for key, value in request.POST.items() if key[:6] == 'form-' + str(index))

                new_comments = dict()

                for field in form_class.field_names:
                    if relevant_data.get(field + '_declare') == 'on':
                        new_comments[field] = relevant_data[field + '_comments']

                table_pk = record[pk_field_name]

                existing_comments = NannyGatewayActions().list('arc-comments', params={'table_pk': table_pk})

                fields_with_existing_comments = get_fields_with_existing_comments(existing_comments)
                delete_existing_comments(existing_comments)
                create_new_arc_comments(new_comments, table_pk, application_id, endpoint=endpoint)
                log_arc_comment_creation(request, verbose_task_name, new_comments, fields_with_existing_comments)

                if len(new_comments) > 0:
                    flagged_fields = True

            return flagged_fields


class OneToOneARCCommentsHandler(ARCCommentsHandler):
    """
    ARC Comments Handler for endpoints with a One-To-One relationship to the APPLICATION table.
    """
    def handle_comments(self, request, form_class, verbose_task_name):
        application_id = request.GET['id']
        endpoint = form_class.api_endpoint_name
        pk_field_name = NannyGatewayActions().get_endpoint_pk(endpoint)
        table_pk = NannyGatewayActions().read(endpoint, params={'application_id': application_id}).record[pk_field_name]

        existing_comments = NannyGatewayActions().list('arc-comments', params={'table_pk': table_pk})

        new_comments = dict()

        # Generate dict with (key, value) pair of (field_name, comment) if field was flagged.
        for field in form_class.field_names:
            if request.POST.get(field + '_declare') == 'on':
                new_comments[field] = request.POST[field + '_comments']

        fields_with_existing_comments = get_fields_with_existing_comments(existing_comments)
        delete_existing_comments(existing_comments)
        create_new_arc_comments(new_comments, table_pk, application_id, endpoint=endpoint)
        log_arc_comment_creation(request, verbose_task_name, new_comments, fields_with_existing_comments)

        return False if len(new_comments) == 0 else True


def get_fields_with_existing_comments(existing_comments):
    if existing_comments.status_code == 200:
        # Create list of existing arc_comments with 'flagged' field as True.
        fields_with_existing_comments = [arc_comments_record['field_name'] for arc_comments_record in
                                         existing_comments.record if arc_comments_record['flagged']]
    else:
        fields_with_existing_comments = []

    return fields_with_existing_comments


def delete_existing_comments(existing_comments):
    if existing_comments.status_code == 200:
        for arc_comments_record in existing_comments.record:
            record_id = arc_comments_record['review_id']
            NannyGatewayActions().delete('arc-comments', params={'review_id': str(record_id)})


def create_new_arc_comments(new_comments, table_pk, application_id, endpoint=''):
    """
    Function to create an ARC comment for a dictionary of new comments for a database entry with some table pk.
    :param new_comments: dict of comments to create.
    :param table_pk: primary key of record for which comment is being created.
    :param application_id: primary key of the application
    :return: None
    """
    for field_name, comment in new_comments.items():
        NannyGatewayActions().create(
            'arc-comments',
            params={
                # 'review_id': str(uuid4()),
                'table_pk': table_pk,
                'application_id': application_id,
                'endpoint_name': endpoint,
                'field_name': field_name,
                'comment': comment,
                'flagged': True,
            }
        )


def log_arc_comment_creation(request, verbose_task_name, new_comments, fields_with_existing_comments):
    for field_name in list(new_comments.keys()):
        # Prevent duplicate logs for fields which are already flagged.
        if field_name not in fields_with_existing_comments:
            log_arc_flag_action(request.GET['id'], request.user.username, field_name, verbose_task_name)


def update_arc_review_status(application_id, flagged_fields, reviewed_task):
    """
    Update the {{task}}_review status in the ARC user's record for that application.
    :param application_id:
    :param flagged_fields:
    :param reviewed_task:
    :return:
    """
    arc_application = Arc.objects.get(application_id=application_id)

    if flagged_fields:
        setattr(arc_application, reviewed_task, 'FLAGGED')
    else:
        setattr(arc_application, reviewed_task, 'COMPLETED')
    arc_application.save()


def update_application_arc_flagged_status(flagged_fields, application_id, reviewed_task):
    task_name = reviewed_task[:-7] + '_arc_flagged'

    if flagged_fields:
        NannyGatewayActions().patch('application', {'application_id': application_id, task_name: True})
    else:
        NannyGatewayActions().patch('application', {'application_id': application_id, task_name: False})


def log_arc_flag_action(application_id, arc_user, flagged_field, verbose_task_name):
    extra_data = {
        'user_type': 'reviewer',
        'formatted_field': flagged_field.replace("_", " "),
        'action': 'flagged by',
        'entity': 'application',
        'task_name': verbose_task_name
    }

    NannyGatewayActions().create('timeline-log',
                                 params={
                                     'object_id': application_id,
                                     'user': arc_user,
                                     'template': 'timeline_logger/application_field_flagged.txt',
                                     'extra_data': json.dumps(extra_data)
                                 })

    return None


def get_form_initial_values(form, application_id):

    # TODO: Turn the below into a recursive function.

    if hasattr(form, 'management_form'):  # If it is a FormSet instance.
        endpoint = form.form.api_endpoint_name
        table_pk_name = NannyGatewayActions().get_endpoint_pk(endpoint)
        form_fields = form.form.field_names
        records = NannyGatewayActions().list(endpoint, params={'application_id': application_id}).record

        initial = []

        for index, record in enumerate(records):
            table_pk_value = record[table_pk_name]

            initial_vals = dict()

            for field_name in form_fields:
                api_response = NannyGatewayActions().list('arc-comments',
                                                          params={'table_pk': table_pk_value, 'field_name': field_name})

                if api_response.status_code == 200:
                    arc_comments_record = api_response.record[0]
                    initial_vals[field_name + '_declare'] = True
                    initial_vals[field_name + '_comments']= arc_comments_record['comment']
                else:
                    initial_vals[field_name + '_declare'] = False
                    initial_vals[field_name + '_comments'] = ''

            initial.append(initial_vals)

        return initial

    endpoint = form.api_endpoint_name

    table_pk_name =     NannyGatewayActions().get_endpoint_pk(endpoint)
    table_pk_value = NannyGatewayActions().read(endpoint, params={'application_id': application_id}).record[table_pk_name]
    form_fields = form.field_names

    initial = dict()

    for field_name in form_fields:
        api_response = NannyGatewayActions().list('arc-comments', params={'table_pk': table_pk_value, 'field_name': field_name})
        if api_response.status_code == 200:
            arc_comments_record = api_response.record[0]
            initial[field_name + '_declare'] = True
            initial[field_name + '_comments'] = arc_comments_record['comment']
        else:
            initial[field_name + '_declare'] = False
            initial[field_name + '_comments'] = ''

    return initial


def update_returned_application_statuses(application_id):
    application_record = NannyGatewayActions().read('application', params={'application_id': application_id}).record
    review_record = Arc.objects.get(application_id=application_id)

    fields_for_review = [i[:-12] for i in application_record.keys() if i[-12:] == '_arc_flagged']
    for field in fields_for_review:
        if getattr(review_record, field + '_review') == 'FLAGGED':
            application_record[field + '_arc_flagged'] = True
            application_record[field + '_status'] = 'FLAGGED'

    NannyGatewayActions().put('application', params=application_record)
