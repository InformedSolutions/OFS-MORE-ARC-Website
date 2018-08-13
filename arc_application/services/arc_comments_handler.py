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
    comments = dict((key[:-8], request.POST[key[:-8] + '_comments']) for key in request.POST.keys() if request.POST[key] == 'on')

    pk = NannyGatewayActions().read(endpoint, params={'application_id': request.GET['id']}).record[table_pk]

    for field_name, comment in comments.items():
        NannyGatewayActions().delete('arc-comments', params={'table_pk': table_pk})  # Delete existing comment.
        NannyGatewayActions().create(
            'arc-comments',
            params={
                'table_pk': pk,
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
    :return:
    """
    arc_application = Arc.objects.get(application_id=application_id)

    if flagged_fields:
        setattr(arc_application, reviewed_task, 'FLAGGED')
    else:
        setattr(arc_application, reviewed_task, 'COMPLETED')
    arc_application.save()


def get_arc_comments_for_form(table_pk):
    pass
