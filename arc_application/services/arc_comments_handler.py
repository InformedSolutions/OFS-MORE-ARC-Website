from uuid import uuid4

from arc_application.models import Arc
from .db_gateways import NannyGatewayActions


def save_arc_comments_from_request(request, endpoint, table_pk):
    """
    Function to save comments made by an ARC reviewer from a given request.
    :param request: request to check for comments.
    :param endpoint:
    :param table_pk: pk of the entry for which comments are being made.
    :return: True if comments were made, else False.
    """
    application_id = request.GET['id']

    # Generate dict with (key, value) pair of (field_name, comment) if field was flagged.
    comments = dict((key[:-8], request.POST[key[:-8] + '_comments']) for key in request.POST.keys() if request.POST[key] == 'on')

    for field_name in list(comments.keys()):
        existing_comment = NannyGatewayActions().list('arc-comments', params={'application_id': application_id, 'field_name': field_name})

        # Delete existing ArcComment
        if existing_comment.status_code == 200:
            record_id = existing_comment.record[0]['review_id']
            NannyGatewayActions().delete('arc-comments', params={'review_id': str(record_id)})
        else:
            pass

    # FIXME: For personal details, this function is called for EACH form - it will therefore create ARC comments with
    # FIXME: the wrong table_pk, since each form has its own table_pk.
    # FIXME: This then means the name field in the personal-details form can't find its initial value when the ARC
    # FIXME: reviewer returns to the page.
    table_record = NannyGatewayActions().read(endpoint, params={'application_id': application_id}).record

    for field_name, comment in comments.items():
        NannyGatewayActions().create(
            'arc-comments',
            params={
                'review_id': str(uuid4()),
                'table_pk': table_record[table_pk],
                'application_id': application_id,
                'table_name': '',
                'field_name': field_name,
                'comment': comment,
                'flagged': True,
            }
        )

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
