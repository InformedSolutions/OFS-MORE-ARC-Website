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
    table_pk = NannyGatewayActions().read(endpoint, params={'application_id': application_id}).record[table_pk]
    existing_comments = NannyGatewayActions().list('arc-comments', params={'table_pk': table_pk})

    # Delete existing ArcComments
    if existing_comments.status_code == 200:
        for arc_comments_record in existing_comments.record:
            record_id = arc_comments_record['id']
            NannyGatewayActions().delete('arc-comments', params={'id': str(record_id)})
    else:
        pass

    # Generate dict with (key, value) pair of (field_name, comment) if field was flagged.
    comments = dict((key[:-8], request.POST[key[:-8] + '_comments']) for key in request.POST.keys() if request.POST[key] == 'on')

    for field_name, comment in comments.items():
        NannyGatewayActions().create(
            'arc-comments',
            params={
                'table_pk': table_pk,
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
