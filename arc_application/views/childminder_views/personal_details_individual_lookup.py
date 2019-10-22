import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from ...decorators import group_required, user_assigned_application
from ...models import ApplicantPersonalDetails, ApplicantName, ApplicantHomeAddress

log = logging.getLogger()


@login_required
@group_required(settings.ARC_GROUP, raise_exception=True)
@user_assigned_application
def personal_details_individual_lookup(request):

    application_id_local = request.GET["id"]
    personal_details_record = ApplicantPersonalDetails.objects.get(application_id=application_id_local)
    name_record = ApplicantName.objects.get(personal_detail_id=personal_details_record)
    home_address_record = ApplicantHomeAddress.objects.get(personal_detail_id=personal_details_record, current_address=True)

    variables = {
        'first_name': name_record.first_name,
        'last_name': name_record.last_name,
        'date_of_birth': personal_details_record.date_of_birth,
        'street_line1': home_address_record.street_line1,
        'street_line2': home_address_record.street_line2,
        'town': home_address_record.town,
        'postcode': home_address_record.postcode,
        'application_id': application_id_local,
    }

    return render(request, 'childminder_templates/personal-details-individual-lookup.html', variables)
