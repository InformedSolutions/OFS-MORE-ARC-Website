import re

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render

from .forms.form import SearchForm
from .models import ApplicantName, ApplicantPersonalDetails, Application
from .views import has_group


@login_required()
def search(request):
    """
    This is the contact centre search applications page
    :param request: An Http request- you must be logged in.
    :return: The search template on GET request, or submit it and return the search results on POST
    """
    cc_user = has_group(request.user, settings.CONTACT_CENTRE)
    arc_user = has_group(request.user, settings.ARC_GROUP)
    context = {
                'cc_user': cc_user,
                'arc_user': arc_user,
                'empty': True
            }

    if (cc_user or arc_user) and request.user.is_authenticated():

        if request.method == 'GET':
            context['form'] = SearchForm()
            return render(request, 'search.html', context)

        elif request.method == 'POST':
            form = SearchForm(request.POST)
            context['form'] = form

            if form.is_valid():
                name = form.cleaned_data['name_search_field']
                dob = form.cleaned_data['dob_search_field']
                home_postcode = form.cleaned_data['home_postcode_search_field']
                care_location_postcode = form.cleaned_data['care_location_postcode_search_field']
                reference = form.cleaned_data['reference_search_field']

                # If no search terms have been entered
                if not name and not dob and not home_postcode and not care_location_postcode and not reference:
                    context['empty'] = 'error'
                    context['error_title'] = 'There was a problem with your search'
                    context['error_text'] = 'Please use at least one filter'
                    return render(request, 'search.html', context)

                results = search_query(name, dob, home_postcode, care_location_postcode, reference)

                if results is not None and len(results) > 0:
                    data = format_data(results)
                    context['empty'] = False
                    context['app'] = data
                    return render(request, 'search.html', context)
                else:
                    context['empty'] = 'error'
                    context['error_title'] = 'No results found'
                    context['error_text'] = 'Check that you have the correct details and spelling.'
                    return render(request, 'search.html', context)

            return render(request, 'search.html', context)
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
            i.sub_type = 'New'
        elif app.application_status == 'FURTHER_INFORMATION':
            i.sub_type = 'Returned'
        elif app.application_status == 'ACCEPTED':
            i.sub_type = 'Pending checks'
        else:
            i.sub_type = ''

        if hasattr(i, 'application_reference'):
            app_id = i.application_id
        else:
            app_id = i.application_id.pk
        i.link = '/arc/search-summary?id=' + str(app_id)
        i.audit_link = '/arc/auditlog?id=' + str(app_id)
    return results


def search_query(name, dob, home_postcode, care_location_postcode, reference):
    """
    This method actually searches the database for results matching the query
    :param query: Either a search for DoB, Name, or Application Id
    :return: A querystring of results
    """
    query = Q()

    if len(reference) > 0:
        query.add(Q(application_reference__icontains=reference), Q.AND)

    query.add(
        Q(
            Q(applicantname__first_name__icontains=name) |
            Q(applicantname__last_name__icontains=name)
        ), Q.AND
    )

    if len(dob) > 0:
        # Split DOB by non-alpha characters
        split_dob = re.split(r"[^0-9]", dob)

        if len(split_dob) == 1:
            # If only one DOB part has been supplied assume it could be day month or year

            # Create four digit year if 2 digit year supplied
            if len(split_dob[0]) == 2:
                previous_century_year = str(19) + split_dob[0]
                current_century_year = str(20) + split_dob[0]
            else:
                # Otherwise allow longer values to be directly issued against query
                previous_century_year = split_dob[0]
                current_century_year = split_dob[0]

            query.add(
                Q(
                    Q(applicantpersonaldetails__birth_day=int(split_dob[0])) |
                    Q(applicantpersonaldetails__birth_month=int(split_dob[0])) |
                    Q(applicantpersonaldetails__birth_year=int(previous_century_year)) |
                    Q(applicantpersonaldetails__birth_year=int(current_century_year))
                ), Q.AND
            )

        if len(split_dob) == 2:
            # If two DOBs part have been supplied, again assume second part is either a month or a year

            # Create four digit year if 2 digit year supplied
            if len(split_dob[1]) == 2:
                previous_century_year = str(19) + split_dob[1]
                current_century_year = str(20) + split_dob[1]
            else:
                # Otherwise allow longer values to be directly issued against query
                previous_century_year = split_dob[1]
                current_century_year = split_dob[1]

            query.add(
                Q(
                    Q(applicantpersonaldetails__birth_day=int(split_dob[0])),
                    Q(applicantpersonaldetails__birth_month=int(split_dob[0])) |
                    Q(applicantpersonaldetails__birth_month=int(split_dob[1])) |
                    Q(applicantpersonaldetails__birth_year=int(previous_century_year)) |
                    Q(applicantpersonaldetails__birth_year=int(current_century_year))
                ), Q.AND
            )

        if len(split_dob) == 3:

            # Create four digit year if 2 digit year supplied
            if len(split_dob[2]) == 2:
                previous_century_year = str(19) + split_dob[2]
                current_century_year = str(20) + split_dob[2]
            else:
                # Otherwise allow longer values to be directly issued against query
                previous_century_year = split_dob[2]
                current_century_year = split_dob[2]

            query.add(
                Q(
                    Q(applicantpersonaldetails__birth_day=int(split_dob[0])),
                    Q(applicantpersonaldetails__birth_month=int(split_dob[0])) |
                    Q(applicantpersonaldetails__birth_month=int(split_dob[1])) |
                    Q(applicantpersonaldetails__birth_year=int(previous_century_year)) |
                    Q(applicantpersonaldetails__birth_year=int(current_century_year))
                ), Q.AND
            )

    address_query = Q()

    home_address_query = Q()
    home_address_query.add(
        Q(
            Q(applicanthomeaddress__childcare_address=False),
            Q(applicanthomeaddress__postcode__icontains=home_postcode)
        ), Q.AND
    )

    home_address_query.add(
        Q(applicanthomeaddress__postcode__icontains=home_postcode), Q.OR
    )

    childcare_address_query = Q()
    childcare_address_query.add(
        Q(
            Q(applicanthomeaddress__childcare_address=True),
            Q(applicanthomeaddress__postcode__icontains=care_location_postcode)
        ), Q.AND
    )

    address_query.add(home_address_query, Q.OR)
    address_query.add(childcare_address_query, Q.AND)

    query.add(address_query, Q.AND)

    return Application.objects.filter(
        query
    )