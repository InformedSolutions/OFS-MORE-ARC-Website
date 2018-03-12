from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render

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
        error_exist = 'false'
        error_title = ''
        error_text = ''
        form = SearchForm(request.POST)
        if request.method == 'POST':
            if form.is_valid():
                query = form.cleaned_data['query']
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
                    error_exist = 'true'
                    error_title = 'Your search \'' + query + '\' has returned no results'

        variables = {
            'empty': True,
            'form': form,
            'error_exist': error_exist,
            'error_title': error_title,
            'error_text': error_text
        }
        return render(request, 'search.html', variables)
    else:
        return HttpResponseRedirect(settings.URL_PREFIX + '/login/')


def format_data(results):
    """
    This adds the missing data from the objects returned from the search
    :param results: An Http request- you must be logged in.
    :return: a querystring of results that match the search
    """
    arr = list(results)
    for i in arr:
        if hasattr(i, 'application_id'):
            if hasattr(i, 'personal_detail_id'):
                # DoB was searched for
                app = Application.objects.get(application_id=i.application_id)
                name = ApplicantName.objects.get(personal_detail_id=i.personal_detail_id)
                i.name = name.first_name + " " + name.last_name
            else:
                # This means an application id was searched for
                app = Application.objects.get(application_id=i.application_id)
                det = ApplicantPersonalDetails.objects.get(application_id=i.application_id)
                name = ApplicantName.objects.get(personal_detail_id=det.personal_detail_id)
                i.name = name.first_name + " " + name.last_name
        if hasattr(i, 'first_name'):
            det = ApplicantPersonalDetails.objects.get(personal_detail_id=i.personal_detail_id)
            i.application_id = det.application_id
            app = Application.objects.get(application_id=i.application_id)
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
        i.link = '/arc/search-summary?id=' + str(i.application_id)
        i.audit_link = '/arc/audit-log?id=' + str(i.application_id)
    return results


def search_query(query):
    """
    This method actually searches the database for results matching the query
    :param query: Either a search for DoB, Name, or Application Id
    :return: A querystring of results
    """
    query = str(query).lower()
    if len(query) == 36 and Application.objects.filter(pk=query).count() > 0:
        return Application.objects.filter(pk=query)
    elif ApplicantName.objects.filter(first_name__iexact=query).count() > 0:
        return ApplicantName.objects.filter(first_name__iexact=query)
    elif ApplicantName.objects.filter(last_name__iexact=query).count() > 0:
        return ApplicantName.objects.filter(last_name__iexact=query)
    else:
        try:
            if ApplicantName.objects.filter(first_name__iexact=query.split(' ')[0], last_name__iexact=query.split(' ')[1]).count() > 0:
                return ApplicantName.objects.filter(first_name__iexact=query.split(' ')[0], last_name__iexact=query.split(' ')[1])
            elif query.count('.') == 2:
                arr = query.split('.')
                if len(arr[2]) == 2:
                    arr[2] = str(19) + arr[2]
                return ApplicantPersonalDetails.objects.filter(birth_day=int(arr[0]), birth_month=int(arr[1]),
                                                               birth_year=int(arr[2]))
            elif query.count('/') == 2:
                arr = query.split('/')
                if len(arr[2]) == 2:
                    arr[2] = str(19) + arr[2]
                return ApplicantPersonalDetails.objects.filter(birth_day=int(arr[0]), birth_month=int(arr[1]),
                                                               birth_year=int(arr[2]))
            elif query.count('-') == 2:
                arr = query.split('-')
                if len(arr[2]) == 2:
                    arr[2] = str(19) + arr[2]
                return ApplicantPersonalDetails.objects.filter(birth_day=int(arr[0]), birth_month=int(arr[1]),
                                                               birth_year=int(arr[2]))
        except Exception as ex:
            print(ex)
    return None


@login_required()
def search_summary(request):
    """
    This page may change, but currently returns a full summary of the application, this doenst have dynamic boxes as it
    needs data first
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered declaration-summary template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
    elif request.method == 'POST':
        application_id_local = request.POST["id"]
        status = Arc.objects.get(pk=application_id_local)
        status.declaration_review = 'COMPLETED'
        status.save()
        return HttpResponseRedirect(settings.URL_PREFIX + '/search' + application_id_local)
    # Retrieve all information related to the application from the database
    application = Application.objects.get(application_id=application_id_local)
    login_detail_id = application.login_id
    login_record = UserDetails.objects.get(login_id=login_detail_id)
    childcare_record = ChildcareType.objects.get(application_id=application_id_local)
    applicant_record = ApplicantPersonalDetails.objects.get(application_id=application_id_local)
    personal_detail_id = applicant_record.personal_detail_id
    applicant_name_record = ApplicantName.objects.get(personal_detail_id=personal_detail_id)
    applicant_home_address_record = ApplicantHomeAddress.objects.get(personal_detail_id=personal_detail_id,
                                                                     current_address=True)
    applicant_childcare_address_record = ApplicantHomeAddress.objects.get(personal_detail_id=personal_detail_id,
                                                                          childcare_address=True)
    first_aid_record = FirstAidTraining.objects.get(application_id=application_id_local)
    dbs_record = CriminalRecordCheck.objects.get(application_id=application_id_local)
    hdb_record = HealthDeclarationBooklet.objects.get(application_id=application_id_local)
    first_reference_record = Reference.objects.get(application_id=application_id_local, reference=1)
    second_reference_record = Reference.objects.get(application_id=application_id_local, reference=2)
    # Retrieve lists of adults and children, ordered by adult/child number for iteration by the HTML
    adults_list = AdultInHome.objects.filter(application_id=application_id_local).order_by('adult')
    children_list = ChildInHome.objects.filter(application_id=application_id_local).order_by('child')
    # Generate lists of data for adults in your home, to be iteratively displayed on the summary page
    # The HTML will then parse through each list simultaneously, to display the correct data for each adult
    adult_name_list = []
    adult_birth_day_list = []
    adult_birth_month_list = []
    adult_birth_year_list = []
    adult_relationship_list = []
    adult_dbs_list = []
    adult_permission_list = []
    application = Application.objects.get(pk=application_id_local)
    for adult in adults_list:
        # For each adult, append the correct attribute (e.g. name, relationship) to the relevant list
        # Concatenate the adult's name for display, displaying any middle names if present
        if adult.middle_names != '':
            name = adult.first_name + ' ' + adult.middle_names + ' ' + adult.last_name
        elif adult.middle_names == '':
            name = adult.first_name + ' ' + adult.last_name
        adult_name_list.append(name)
        adult_birth_day_list.append(adult.birth_day)
        adult_birth_month_list.append(adult.birth_month)
        adult_birth_year_list.append(adult.birth_year)
        adult_relationship_list.append(adult.relationship)
        adult_dbs_list.append(adult.dbs_certificate_number)
        adult_permission_list.append(adult.permission_declare)
    # Zip the appended lists together for the HTML to simultaneously parse
    adult_lists = zip(adult_name_list, adult_birth_day_list, adult_birth_month_list, adult_birth_year_list,
                      adult_relationship_list, adult_dbs_list, adult_permission_list)
    # Generate lists of data for adults in your home, to be iteratively displayed on the summary page
    # The HTML will then parse through each list simultaneously, to display the correct data for each adult
    child_name_list = []
    child_birth_day_list = []
    child_birth_month_list = []
    child_birth_year_list = []
    child_relationship_list = []

    for child in children_list:
        # For each child, append the correct attribute (e.g. name, relationship) to the relevant list
        # Concatenate the child's name for display, displaying any middle names if present
        if child.middle_names != '':
            name = child.first_name + ' ' + child.middle_names + ' ' + child.last_name
        elif child.middle_names == '':
            name = child.first_name + ' ' + child.last_name
        child_name_list.append(name)
        child_birth_day_list.append(child.birth_day)
        child_birth_month_list.append(child.birth_month)
        child_birth_year_list.append(child.birth_year)
        child_relationship_list.append(child.relationship)
    # Zip the appended lists together for the HTML to simultaneously parse
    child_lists = zip(child_name_list, child_birth_day_list, child_birth_month_list, child_birth_year_list,
                      child_relationship_list)
    variables = {
        'application_id': application_id_local,
        'login_details_email': login_record.email,
        'login_details_mobile_number': login_record.mobile_number,
        'login_details_alternative_phone_number': login_record.add_phone_number,
        'childcare_type_zero_to_five': childcare_record.zero_to_five,
        'childcare_type_five_to_eight': childcare_record.five_to_eight,
        'childcare_type_eight_plus': childcare_record.eight_plus,
        'personal_details_first_name': applicant_name_record.first_name,
        'personal_details_middle_names': applicant_name_record.middle_names,
        'personal_details_last_name': applicant_name_record.last_name,
        'personal_details_birth_day': applicant_record.birth_day,
        'personal_details_birth_month': applicant_record.birth_month,
        'personal_details_birth_year': applicant_record.birth_year,
        'home_address_street_line1': applicant_home_address_record.street_line1,
        'home_address_street_line2': applicant_home_address_record.street_line2,
        'home_address_town': applicant_home_address_record.town,
        'home_address_county': applicant_home_address_record.county,
        'home_address_postcode': applicant_home_address_record.postcode,
        'childcare_street_line1': applicant_childcare_address_record.street_line1,
        'childcare_street_line2': applicant_childcare_address_record.street_line2,
        'childcare_town': applicant_childcare_address_record.town,
        'childcare_county': applicant_childcare_address_record.county,
        'childcare_postcode': applicant_childcare_address_record.postcode,
        'location_of_childcare': applicant_home_address_record.childcare_address,
        'first_aid_training_organisation': first_aid_record.training_organisation,
        'first_aid_training_course': first_aid_record.course_title,
        'first_aid_certificate_day': first_aid_record.course_day,
        'first_aid_certificate_month': first_aid_record.course_month,
        'first_aid_certificate_year': first_aid_record.course_year,
        'dbs_certificate_number': dbs_record.dbs_certificate_number,
        'cautions_convictions': dbs_record.cautions_convictions,
        'declaration': dbs_record.send_certificate_declare,
        'send_hdb_declare': hdb_record.send_hdb_declare,
        'first_reference_first_name': first_reference_record.first_name,
        'first_reference_last_name': first_reference_record.last_name,
        'first_reference_relationship': first_reference_record.relationship,
        'first_reference_years_known': first_reference_record.years_known,
        'first_reference_months_known': first_reference_record.months_known,
        'first_reference_street_line1': first_reference_record.street_line1,
        'first_reference_street_line2': first_reference_record.street_line2,
        'first_reference_town': first_reference_record.town,
        'first_reference_county': first_reference_record.county,
        'first_reference_postcode': first_reference_record.postcode,
        'first_reference_country': first_reference_record.country,
        'first_reference_phone_number': first_reference_record.phone_number,
        'first_reference_email': first_reference_record.email,
        'second_reference_first_name': second_reference_record.first_name,
        'second_reference_last_name': second_reference_record.last_name,
        'second_reference_relationship': second_reference_record.relationship,
        'second_reference_years_known': second_reference_record.years_known,
        'second_reference_months_known': second_reference_record.months_known,
        'second_reference_street_line1': second_reference_record.street_line1,
        'second_reference_street_line2': second_reference_record.street_line2,
        'second_reference_town': second_reference_record.town,
        'second_reference_county': second_reference_record.county,
        'second_reference_postcode': second_reference_record.postcode,
        'second_reference_country': second_reference_record.country,
        'second_reference_phone_number': second_reference_record.phone_number,
        'second_reference_email': second_reference_record.email,
        'adults_in_home': application.adults_in_home,
        'children_in_home': application.children_in_home,
        'number_of_adults': adults_list.count(),
        'number_of_children': children_list.count(),
        'adult_lists': adult_lists,
        'child_lists': child_lists,
        'turning_16': application.children_turning_16,
    }

    return render(request, 'search-summary.html', variables)