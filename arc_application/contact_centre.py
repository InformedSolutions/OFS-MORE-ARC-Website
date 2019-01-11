from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render

from arc_application.services.search_service import SearchService
from arc_application.views import has_group
from .forms.childminder_forms.form import SearchForm
from .models import ApplicantName, ApplicantPersonalDetails, Application


@login_required()
def search(request):
    """
    This is the contact centre search applications page
    :param request: An Http request- you must be logged in.
    :return: The search template on GET request, or submit it and return the search results on POST
    """

    SEARCH_TEMPLATE_PATH = 'search.html'

    cc_user = has_group(request.user, settings.CONTACT_CENTRE)
    arc_user = has_group(request.user, settings.ARC_GROUP)
    context = {
        'cc_user': cc_user,
        'arc_user': arc_user,
        'empty': True
    }

    if (cc_user or arc_user) and request.user.is_authenticated():

        # Display all applications on search page
        results = SearchService.search("", "", "", "", "", 'Childminder')

        if results is not None and len(results) > 0:
            context['empty'] = False
            context['app'] = results

        if request.method == 'GET':
            context['form'] = SearchForm()
            return render(request, SEARCH_TEMPLATE_PATH, context)

        elif request.method == 'POST':
            form = SearchForm(request.POST)
            context['form'] = form

            if form.is_valid():
                name = form.cleaned_data['name_search_field']
                dob = form.cleaned_data['dob_search_field']
                home_postcode = form.cleaned_data['home_postcode_search_field']
                care_location_postcode = form.cleaned_data['care_location_postcode_search_field']
                reference = form.cleaned_data['reference_search_field']
                # application_type = form.cleaned_data['application_type_dropdown_search_field']

                # If no search terms have been entered
                if not name and not dob and not home_postcode and not care_location_postcode and not reference:
                    context['empty_error'] = True
                    context['error_title'] = 'There was a problem with your search'
                    context['error_text'] = 'Please use at least one filter'
                    return render(request, SEARCH_TEMPLATE_PATH, context)

                search_results = SearchService.search(name, dob, home_postcode, care_location_postcode, reference,
                                                      'Childminder')

                if search_results is not None and len(search_results) > 0:
                    context['app'] = search_results

                else:
                    context['empty_error'] = True
                    context['error_title'] = 'No results found'
                    context['error_text'] = 'Check that you have the correct details and spelling.'

            return render(request, SEARCH_TEMPLATE_PATH, context)
    else:
        return HttpResponseRedirect(settings.URL_PREFIX + '/login/')


def format_data(results):
    """
    This adds the missing data from the objects returned from the search
    :param results: Querystring of objects that match query.
    :return: a querystring of results that match the search
    """
    arr = list(results)
    for i in arr:
        # these if statements are not obvious, essentiall we need to get name, date submitted, updated and application id for each result found
        if hasattr(i, 'application_id'):
            if hasattr(i, 'personal_detail_id'):
                # DoB was searched for (has both personal_details_id and application_id columns)
                app = Application.objects.get(application_id=i.application_id.pk)
                name = ApplicantName.objects.get(personal_detail_id=i.personal_detail_id.pk)
                i.name = name.first_name + " " + name.last_name
            else:
                # This means an application id was searched for (has only application_id, and not
                app = Application.objects.get(application_id=i.application_id)

                if ApplicantName.objects.filter(application_id=app.pk).exists():
                    name = ApplicantName.objects.get(application_id=app.pk)
                    i.name = name.first_name + " " + name.last_name

        if hasattr(i, 'first_name'):
            # This if statement is for if they searched a name
            det = ApplicantPersonalDetails.objects.get(personal_detail_id=i.personal_detail_id.pk)
            i.application_id = det.application_id
            app = Application.objects.get(application_id=i.application_id.pk)
            i.name = i.first_name + " " + i.last_name

        if not app.date_submitted == None:
            i.submitted = app.date_submitted.strftime('%d/%m/%Y')
        else:
            i.submitted = None
        if not app.date_updated == None:
            i.accessed = app.date_updated.strftime('%d/%m/%Y')
        else:
            i.accessed = None

        i.type = 'Childminder'
        if app.application_status == 'DRAFTING':
            i.sub_type = 'Draft'
        elif app.application_status == 'ACCEPTED':
            i.sub_type = 'Pending checks'
        elif app.application_status == 'FURTHER_INFORMATION':
            i.sub_type = 'Returned'
        elif app.application_status == 'SUBMITTED':
            i.sub_type = 'New'
        elif app.application_status == 'ARC_REVIEW':
            i.sub_type = 'Assigned'
        else:
            i.sub_type = ''

        if hasattr(i, 'application_reference'):
            app_id = i.application_id
        else:
            app_id = i.application_id.pk
        i.link = '/arc/search-summary?id=' + str(app_id)
        i.audit_link = '/arc/auditlog?id=' + str(app_id)
    return results
