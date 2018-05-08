from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render

from ..forms.form import ReferencesForm, ReferencesForm2
from ..models import Application, Arc, Reference
from ..review_util import redirect_selection, request_to_comment, save_comments


def references_summary(request):
    """
    Method returning the template for the 2 references: summary page (for a given application)
    displaying entered data for this task and navigating to the task list when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered 2 references: summary template
    """
    table_name = 'REFERENCE'

    if request.method == 'GET':
        application_id_local = request.GET["id"]
        reference_id_1 = Reference.objects.get(application_id=application_id_local, reference=1).reference_id
        reference_id_2 = Reference.objects.get(application_id=application_id_local, reference=2).reference_id
        form = ReferencesForm(table_keys=[reference_id_1], prefix="form")
        form2 = ReferencesForm2(table_keys=[reference_id_2], prefix="form2")
    elif request.method == 'POST':
        # Grab necessary IDs
        application_id_local = request.POST["id"]
        reference_id_1 = Reference.objects.get(application_id=application_id_local, reference=1).reference_id
        reference_id_2 = Reference.objects.get(application_id=application_id_local, reference=2).reference_id
        # Grab form data from post
        form = ReferencesForm(request.POST, table_keys=[reference_id_1], prefix="form")
        form2 = ReferencesForm2(request.POST, table_keys=[reference_id_2], prefix="form2")
        # As form data prefixed in above lines to separate the two forms, this prefix must be removed before
        # storage, this is to allow for easier retrieval form the database

        if form.is_valid() and form2.is_valid():
            # Get comments to be saved
            form_comments = request_to_comment(reference_id_1, table_name, form.cleaned_data)
            form2_comments = request_to_comment(reference_id_2, table_name, form2.cleaned_data)
            # Save the comments
            reference1_saved = save_comments(form_comments)
            reference2_saved = save_comments(form2_comments)

            if not form_comments and not form2_comments:
                section_status = 'COMPLETED'
            else:
                section_status = 'FLAGGED'

            if reference1_saved and reference2_saved:
                status = Arc.objects.get(pk=application_id_local)
                status.references_review = section_status
                status.save()
                default = '/other-people/summary'
                redirect_link = redirect_selection(request, default)

                return HttpResponseRedirect(settings.URL_PREFIX + redirect_link + '?id=' + application_id_local)
            else:

                return render(request, '500.html')

    first_reference_record = Reference.objects.get(application_id=application_id_local, reference=1)
    second_reference_record = Reference.objects.get(application_id=application_id_local, reference=2)
    first_reference_first_name = first_reference_record.first_name
    first_reference_last_name = first_reference_record.last_name
    first_reference_relationship = first_reference_record.relationship
    first_reference_years_known = first_reference_record.years_known
    first_reference_months_known = first_reference_record.months_known
    first_reference_street_line1 = first_reference_record.street_line1
    first_reference_street_line2 = first_reference_record.street_line2
    first_reference_town = first_reference_record.town
    first_reference_county = first_reference_record.county
    first_reference_country = first_reference_record.country
    first_reference_postcode = first_reference_record.postcode
    first_reference_phone_number = first_reference_record.phone_number
    first_reference_email = first_reference_record.email
    second_reference_first_name = second_reference_record.first_name
    second_reference_last_name = second_reference_record.last_name
    second_reference_relationship = second_reference_record.relationship
    second_reference_years_known = second_reference_record.years_known
    second_reference_months_known = second_reference_record.months_known
    second_reference_street_line1 = second_reference_record.street_line1
    second_reference_street_line2 = second_reference_record.street_line2
    second_reference_town = second_reference_record.town
    second_reference_county = second_reference_record.county
    second_reference_country = second_reference_record.country
    second_reference_postcode = second_reference_record.postcode
    second_reference_phone_number = second_reference_record.phone_number
    second_reference_email = second_reference_record.email
    application = Application.objects.get(pk=application_id_local)
    variables = {
        'form': form,
        'form2': form2,
        'application_id': application_id_local,
        'first_reference_first_name': first_reference_first_name,
        'first_reference_last_name': first_reference_last_name,
        'first_reference_relationship': first_reference_relationship,
        'first_reference_years_known': first_reference_years_known,
        'first_reference_months_known': first_reference_months_known,
        'first_reference_street_line1': first_reference_street_line1,
        'first_reference_street_line2': first_reference_street_line2,
        'first_reference_town': first_reference_town,
        'first_reference_county': first_reference_county,
        'first_reference_country': first_reference_country,
        'first_reference_postcode': first_reference_postcode,
        'first_reference_phone_number': first_reference_phone_number,
        'first_reference_email': first_reference_email,
        'second_reference_first_name': second_reference_first_name,
        'second_reference_last_name': second_reference_last_name,
        'second_reference_relationship': second_reference_relationship,
        'second_reference_years_known': second_reference_years_known,
        'second_reference_months_known': second_reference_months_known,
        'second_reference_street_line1': second_reference_street_line1,
        'second_reference_street_line2': second_reference_street_line2,
        'second_reference_town': second_reference_town,
        'second_reference_county': second_reference_county,
        'second_reference_country': second_reference_country,
        'second_reference_postcode': second_reference_postcode,
        'second_reference_phone_number': second_reference_phone_number,
        'second_reference_email': second_reference_email,
        'references_status': application.references_status
    }

    return render(request, 'references-summary.html', variables)
