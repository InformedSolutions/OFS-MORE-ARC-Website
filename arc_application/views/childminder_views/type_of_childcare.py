from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from arc_application.models import Arc, ChildcareType
from arc_application.review_util import redirect_selection
from arc_application.decorators import group_required, user_assigned_application


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
        return HttpResponseRedirect(settings.URL_PREFIX + redirect_link + '?id=' + application_id_local)

    application_id_local = request.GET["id"]
    childcare_type = ChildcareType.objects.get(application_id=application_id_local)
    register_name = get_register_name(childcare_type)
    variables = {
        'application_id': str(application_id_local),
        'zero': childcare_type.zero_to_five,
        'five': childcare_type.five_to_eight,
        'eight': childcare_type.eight_plus,
        'register': register_name,
        'overnight_care': childcare_type.overnight_care
    }

    return render(request, 'childminder_templates/childcare-age-groups.html', variables)


def get_register_name(childcare_type):
    """
    Method to get the names of the registers to which the applicant is applying
    :param childcare_type: ChildcareType record
    :return: string
    """
    zero_to_five = childcare_type.zero_to_five
    five_to_eight = childcare_type.five_to_eight
    eight_plus = childcare_type.eight_plus
    register = ''
    if zero_to_five and five_to_eight and eight_plus:
        register = 'Early Years Register and Childcare Register (both parts)'
    if not zero_to_five and five_to_eight and eight_plus:
        register = 'Childcare Register (both parts)'
    if zero_to_five and not five_to_eight and not eight_plus:
        register = 'Early Years Register'
    if zero_to_five and five_to_eight and not eight_plus:
        register = 'Early Years Register and Childcare Register (compulsory part)'
    if zero_to_five and not five_to_eight and eight_plus:
        register = 'Early Years Register and Childcare Register (voluntary part)'
    if not zero_to_five and five_to_eight and not eight_plus:
        register = 'Childcare Register (compulsory part)'
    if not zero_to_five and not five_to_eight and eight_plus:
        register = 'Childcare Register (voluntary part)'
    return register
