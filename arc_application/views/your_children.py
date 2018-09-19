from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.forms import formset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from ..forms.form import ChildForm, ChildAddressForm
from ..models import Child, ChildAddress, Application, Arc
from ..decorators import group_required, user_assigned_application
from .review import children_initial_population, children_address_initial_population

from ..review_util import request_to_comment, save_comments, redirect_selection, build_url

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
    children_address_form_set = formset_factory(ChildAddressForm)

    # Fetch child data and instantiate associate forms

    children = Child.objects.filter(application_id=application_id).order_by('child')
    children_living_with_childminder \
        = Child.objects.filter(application_id=application_id, lives_with_childminder=True).order_by('child')

    initial_children_data = children_initial_population(children)
    formset_of_children = children_form_set(initial=initial_children_data, prefix='child')
    children_object_and_form_lists = zip(children, formset_of_children)

    # Fetch address data and instantiate associate forms

    child_addresses = ChildAddress.objects.filter(application_id=application_id).order_by('child')

    initial_children_address_data = children_address_initial_population(child_addresses)
    formset_of_children_address = children_address_form_set(initial=initial_children_address_data,
                                                            prefix='child-address')
    child_addresses_and_form_list = zip(children, child_addresses, formset_of_children_address)

    # Render page

    variables = {
        'application_id': application_id,
        'children': children,
        'children_living_with_childminder': children_living_with_childminder,
        'children_form_set': children_form_set,
        'children_object_and_form_lists': children_object_and_form_lists,
        'child_addresses': child_addresses,
        'children_address_form_set': children_address_form_set,
        'child_addresses_and_form_list': child_addresses_and_form_list,
        'formset_of_children': formset_of_children,
        'formset_of_children_address': formset_of_children_address
    }

    return render(request, 'your-children-summary.html', variables)


def __your_children_summary_post__handler(request):
    application_id = request.GET.get('id') or request.POST.get('id')

    children_form_set = formset_factory(ChildForm)
    children_address_form_set = formset_factory(ChildAddressForm)

    # Retrieve form sets from POST body
    posted_children_forms = children_form_set(request.POST, prefix='child')
    posted_children_address_forms = children_address_form_set(request.POST, prefix='child-address')

    # Validated all submitted forms
    if all([posted_children_forms.is_valid(), posted_children_address_forms.is_valid()]):
        # These are the table names for all of the objects on the page that are being iterated. Used in the request
        # to comment function and for saving
        table_names = ['CHILD', 'CHILD_ADDRESS']

        # Unique id fields of each distinct object type. Must match order of table_names_array
        attr_list = ['child_id', 'child_address_id']

        clean_child_data = posted_children_forms.cleaned_data
        clean_address_data = posted_children_address_forms.cleaned_data

        clean_child_data.pop()
        clean_address_data.pop()

        children = Child.objects.filter(application_id=application_id).order_by('child')
        child_addresses = ChildAddress.objects.filter(application_id=application_id).order_by('child')

        all_forms_data_collection = [clean_child_data, clean_address_data]
        existing_data_collections_list = [children, child_addresses]

        section_status = 'COMPLETED'

        for form_data_for_all_forms_of_given_type in all_forms_data_collection:
            object_index = all_forms_data_collection.index(form_data_for_all_forms_of_given_type)
            for single_object_form_data in form_data_for_all_forms_of_given_type:
                request_index = form_data_for_all_forms_of_given_type.index(single_object_form_data)
                relevant_object_type_collection = existing_data_collections_list[object_index]
                relevant_record = relevant_object_type_collection[request_index]
                relevant_record_pk = getattr(relevant_record, attr_list[object_index])
                record_comments = request_to_comment(relevant_record_pk, table_names[object_index], single_object_form_data)
                if record_comments:
                    section_status = 'FLAGGED'
                    application = Application.objects.get(pk=application_id)
                    application.your_children_arc_flagged = True
                    application.save()

                successful = save_comments(request, record_comments)
                if not successful:
                    return render(request, '500.html')

        # Set overall status of task
        status = Arc.objects.get(pk=application_id)
        status.your_children_review = section_status
        status.save()

    # Redirect to first aid training
    return HttpResponseRedirect(reverse('first_aid_training_summary') + '?id=' + str(application_id))
