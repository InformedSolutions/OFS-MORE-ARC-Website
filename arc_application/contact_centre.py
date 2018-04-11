from itertools import chain

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.db.models import Q

from timeline_logger.models import TimelineLog

from .forms import SearchForm
from .models import AdultInHome, ApplicantHomeAddress, ApplicantName, ApplicantPersonalDetails, Application, Arc, \
    ChildInHome, ChildcareType, CriminalRecordCheck, FirstAidTraining, HealthDeclarationBooklet, Reference, \
    UserDetails
from .views import has_group


@login_required()
def search(request):
    """
    This is the contact centre search applications page
    :param request: An Http request- you must be logged in.
    :return: The search template on GET request, or submit it and return the search results on POST
    """
    if has_group(request.user, settings.CONTACT_CENTRE) and request.user.is_authenticated():

        if request.method == 'GET':
            form = SearchForm()
            variables = {
                'empty': True,
                'form': form,
            }
            return render(request, 'search.html', variables)

        elif request.method == 'POST':
            form = SearchForm(request.POST)

            if form.is_valid():
                query = form.cleaned_data['query']

                if len(query) > 2:
                    results = search_query(query)
                    if results is not None and len(results) > 0:
                        data = format_data(results)
                        variables = {
                            'empty': False,
                            'form': form,
                            'app': data,
                        }
                        return render(request, 'search.html', variables)
                    else:
                        variables = {
                            'empty': 'error',
                            'error_title': 'No Results Found',
                            'error_text': '',
                            'form': form,
                        }
                        return render(request, 'search.html', variables)
            variables = {
                'empty': True,
                'form': form,
            }

            return render(request, 'search.html', variables)
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
        i.sub_type = 'New'

        if hasattr(i, 'order_code'):
            app_id = i.application_id
        else:
            app_id = i.application_id.pk
        i.link = '/arc/search-summary?id=' + str(app_id)
        i.audit_link = '/arc/auditlog?id=' + str(app_id)
    return results


def search_query(query):
    """
    This method actually searches the database for results matching the query
    :param query: Either a search for DoB, Name, or Application Id
    :return: A querystring of results
    """

    query = str(query).lower()
    query_length = len(query)

    # Check for Application Id (36 Chars)
    if query_length == 36 and Application.objects.filter(pk=query).exists():
        return Application.objects.filter(pk=query)
    elif ApplicantName.objects.filter(first_name__icontains=query).exists():
        return ApplicantName.objects.filter(first_name__icontains=query)
    elif ApplicantName.objects.filter(last_name__icontains=query).exists():
        return ApplicantName.objects.filter(last_name__icontains=query)
    else:
        try:
            if ' ' in query:
                if ApplicantName.objects.filter(first_name__icontains=query.split(' ')[0],
                                                last_name__icontains=query.split(' ')[1]).count() > 0:
                    return ApplicantName.objects.filter(first_name__icontains=query.split(' ')[0],
                                                        last_name__icontains=query.split(' ')[1])
            elif query.count('.') == 2:
                arr = query.split('.')
                temp_year = arr[2]
                if len(arr[2]) == 2:
                    temp_year = str(20) + arr[2]
                    arr[2] = str(19) + arr[2]
                return list(
                    ApplicantPersonalDetails.objects.filter(
                        Q(birth_day=int(arr[0]), birth_month=int(arr[1]), birth_year=int(arr[2])) |
                        Q(birth_day=int(arr[0]), birth_month=int(arr[1]), birth_year=int(temp_year))
                    )
                )
            elif query.count('/') == 2:
                arr = query.split('/')
                temp_year = arr[2]
                if len(arr[2]) == 2:
                    temp_year = str(20) + arr[2]
                    arr[2] = str(19) + arr[2]
                return list(
                    ApplicantPersonalDetails.objects.filter(
                        Q(birth_day=int(arr[0]), birth_month=int(arr[1]), birth_year=int(arr[2])) |
                        Q(birth_day=int(arr[0]), birth_month=int(arr[1]), birth_year=int(temp_year))
                    )
                )
            elif query.count('-') == 2:
                arr = query.split('-')
                temp_year = arr[2]
                if len(arr[2]) == 2:
                    temp_year = str(20) + arr[2]
                    arr[2] = str(19) + arr[2]
                return list(
                    ApplicantPersonalDetails.objects.filter(
                        Q(birth_day=int(arr[0]), birth_month=int(arr[1]), birth_year=int(arr[2])) |
                        Q(birth_day=int(arr[0]), birth_month=int(arr[1]), birth_year=int(temp_year))
                    )
                )
        except Exception as ex:
            print(ex)
    return None
