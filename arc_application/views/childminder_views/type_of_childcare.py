from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
import logging
from ...models import Arc, ChildcareType
from ...review_util import redirect_selection
from ...decorators import group_required, user_assigned_application

# Initiate logging
log = logging.getLogger('')

@login_required
@group_required(settings.ARC_GROUP)
@user_assigned_application
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
        log.debug("Handling submissions for type of childcare")
        return HttpResponseRedirect(settings.URL_PREFIX + redirect_link + '?id=' + application_id_local)

    application_id_local = request.GET["id"]
    childcare_type = ChildcareType.objects.get(application_id=application_id_local)
    register_name = childcare_type.get_register_name()
    variables = {
        'application_id': str(application_id_local),
        'zero': childcare_type.zero_to_five,
        'five': childcare_type.five_to_eight,
        'eight': childcare_type.eight_plus,
        'register': register_name,
        'childcare_places': childcare_type.childcare_places,
        'childcare_times': childcare_type.get_timings(),
        'overnight_care': childcare_type.overnight_care
    }
    log.debug("Render type of childcare page")
    return render(request, 'childminder_templates/childcare-age-groups.html', variables)

