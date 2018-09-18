from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.forms import formset_factory

from ..decorators import group_required, user_assigned_application
from ..forms.form import ChildForm
from ..models import Application, Child


@login_required
@group_required(settings.ARC_GROUP)
@user_assigned_application
def your_children_summary(request):
    """
    Method returning the template for the Your Children (for a given application) task
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your Children template
    """

    if request.method == 'GET':
        return __your_children_summary_get__handler(request)
    elif request.method == 'POST':
        return __your_children_summary_post__handler(request)


def __your_children_summary_get__handler(request):
    child_form_set = formset_factory(ChildForm)
    table_names = ['CHILD']
    application_id = request.GET.get('id') or request.POST.get('id')
    application = Application.objects.get(pk=application_id)

    children = Child.objects.filter(application_id=application_id)

    form = ChildForm()
    # Compile list of childrens names
    #
    return None


def __your_children_summary_post__handler(request):
    return None