from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.forms import formset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from ..forms.form import ChildForm, ChildAddressForm
from ..models import Child, ChildAddress
from ..decorators import group_required, user_assigned_application
from .review import children_initial_population, children_address_initial_population


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
    application_id = request.GET.get('id') or request.POST.get('id')

    children_form_set = formset_factory(ChildForm)

    children = Child.objects.filter(application_id=application_id).order_by('child')
    children_living_with_childminder \
        = Child.objects.filter(application_id=application_id, lives_with_childminder=True).order_by('child')

    initial_children_data = children_initial_population(children)
    formset_of_children = children_form_set(initial=initial_children_data, prefix='child')

    children_address_form_set = formset_factory(ChildAddressForm)
    child_addresses = ChildAddress.objects.filter(application_id=application_id).order_by('child')

    initial_children_address_data = children_address_initial_population(child_addresses)
    formset_of_children_address = children_address_form_set(initial=initial_children_address_data,
                                                            prefix='child-address')
    child_addresses_and_form_list = zip(children, child_addresses, formset_of_children_address)

    children_object_and_form_lists = zip(children, formset_of_children)

    variables = {
        'application_id': application_id,
        'children': children,
        'children_living_with_childminder': children_living_with_childminder,
        'children_object_and_form_lists': children_object_and_form_lists,
        'child_addresses': child_addresses,
        'child_addresses_and_form_list': child_addresses_and_form_list,
        'formset_of_children': formset_of_children,
    }

    return render(request, 'your-children-summary.html', variables)


def __your_children_summary_post__handler(request):
    application_id = request.GET.get('id') or request.POST.get('id')

    # Redirect to first aid trainin
    return HttpResponseRedirect(reverse('first_aid_training_summary') + '?id=' + str(application_id))
