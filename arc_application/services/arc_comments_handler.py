import json
from uuid import uuid4

from arc_application.models import Arc
from .db_gateways import NannyGatewayActions


def save_arc_comments_from_request(request, endpoint, table_pk, verbose_task_name):
    """
    Function to save comments made by an ARC reviewer from a given request.
    :param request: request to check for comments.
    :param endpoint:
    :param table_pk: pk of the entry for which comments are being made.
    :param verbose_task_name: The name of the task to be recorded in the audit log.
    :return: True if comments were made, else False.
    """
    application_id = request.GET['id']
    table_pk = NannyGatewayActions().read(endpoint, params={'application_id': application_id}).record[table_pk]
    existing_comments = NannyGatewayActions().list('arc-comments', params={'table_pk': table_pk})

    # Delete existing ArcComments
    if existing_comments.status_code == 200:
        # Create list of existing arc_comments with 'flagged' field as True.
        fields_with_existing_comments = [arc_comments_record['field_name'] for arc_comments_record in existing_comments.record if arc_comments_record['flagged']]

        for arc_comments_record in existing_comments.record:
            record_id = arc_comments_record['review_id']
            NannyGatewayActions().delete('arc-comments', params={'review_id': str(record_id)})
    else:
        fields_with_existing_comments = []

    # Generate dict with (key, value) pair of (field_name, comment) if field was flagged.
    comments = dict((key[:-8], request.POST[key[:-8] + '_comments']) for key in request.POST.keys() if request.POST[key] == 'on')

    for field_name, comment in comments.items():
        NannyGatewayActions().create(
            'arc-comments',
            params={
                'review_id': str(uuid4()),
                'table_pk': table_pk,
                'application_id': application_id,
                'table_name': '',
                'field_name': field_name,
                'comment': comment,
                'flagged': True,
            }
        )

        # Prevent duplicate logs for fields which are already flagged.
        if field_name not in fields_with_existing_comments:
            log_arc_flag_action(application_id, request.user.username, field_name, verbose_task_name)

    return False if len(comments) == 0 else True


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
    endpoint = form.api_endpoint_name
    table_pk = form.pk_field_name

    table_pk = NannyGatewayActions().read(endpoint, params={'application_id': application_id}).record[table_pk]
    form_fields = form.field_names

    for field_name in form_fields:
        api_response = NannyGatewayActions().list('arc-comments', params={'table_pk': table_pk, 'field_name': field_name})
        if api_response.status_code == 200:
            arc_comments_record = api_response.record[0]
            form[field_name + '_declare'].initial = True
            form[field_name + '_comments'].initial = arc_comments_record['comment']
        else:
            form[field_name + '_declare'].initial = False
            form[field_name + '_comments'].initial = ''

    return form


def update_returned_application_statuses(application_id):
    application_record = NannyGatewayActions().read('application', params={'application_id': application_id}).record
    review_record = Arc.objects.get(application_id=application_id)

    fields_for_review = [i[:-12] for i in application_record.keys() if i[-12:] == '_arc_flagged']
    for field in fields_for_review:
        if getattr(review_record, field + '_review') == 'FLAGGED':
            application_record[field + '_arc_flagged'] = True
            application_record[field + '_status'] = 'FLAGGED'

    NannyGatewayActions().put('application', params=application_record)
