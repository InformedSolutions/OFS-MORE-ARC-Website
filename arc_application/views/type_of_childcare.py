from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from ..models import Arc, ChildcareType
from ..review_util import redirect_selection
from .base import group_required


@group_required(settings.ARC_GROUP)
def type_of_childcare_age_groups(request):
    """
    Method returning the template for the Type of childcare: age groups page (for a given application) and navigating
    to the task list when successfully completed; business logic is applied to either create or update the
    associated Childcare_Type record
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Type of childcare: age groups template
    """

    if request.method == 'GET':
        application_id_local = request.GET["id"]
    elif request.method == 'POST':
        # As there is no actual flagging to be done for this section, the status is just set to completed on POST
        application_id_local = request.POST["id"]
        status = Arc.objects.get(pk=application_id_local)
        status.childcare_type_review = 'COMPLETED'
        status.save()
        default = '/personal-details/summary'
        redirect_link = redirect_selection(request, default)
        return HttpResponseRedirect(settings.URL_PREFIX + redirect_link + '?id=' + application_id_local)

    application_id_local = request.GET["id"]
    application = ChildcareType.objects.get(application_id=application_id_local)
    variables = {
        'application_id': str(application_id_local),
        'zero': application.zero_to_five,
        'five': application.five_to_eight,
        'eight': application.eight_plus,
    }

    return render(request, 'childcare-age-groups.html', variables)
