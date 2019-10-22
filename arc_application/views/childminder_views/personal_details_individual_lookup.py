import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from ...decorators import group_required, user_assigned_application
from ...models import ApplicantPersonalDetails, ApplicantName, ApplicantHomeAddress
from ...services.db_gateways import NannyGatewayActions

log = logging.getLogger()


def read_record(actions, endpoint, params):
    response = getattr(actions, 'read')(endpoint, params=params)
    if response.status_code != 200 or not hasattr(response, 'record'):
        return {}
    return response.record


def fetch_childminder_data(app_id):
    personal_details_record = ApplicantPersonalDetails.objects.get(application_id=app_id)
    name_record = ApplicantName.objects.get(personal_detail_id=personal_details_record)
    home_address_record = ApplicantHomeAddress.objects.get(
        personal_detail_id=personal_details_record,
        current_address=True
    )

    return name_record, personal_details_record, home_address_record


def fetch_nanny_data(app_id):
    nanny_actions = NannyGatewayActions()
    personal_details = read_record(
        nanny_actions, 'applicant-personal-details', {'application_id': app_id}
    )
    home_address_record = read_record(
        nanny_actions, 'applicant-home-address', {'application_id': app_id}
    )

    return personal_details, personal_details, home_address_record


@login_required
@group_required(settings.ARC_GROUP, raise_exception=True)
@user_assigned_application
def personal_details_individual_lookup(request):

    application_id = request.GET.get('id')
    referrer_type = request.GET.get('referrer')

    data_fetcher_mapping = {
        'childminder': fetch_childminder_data,
        'nanny': fetch_nanny_data
    }

    if not application_id or referrer_type not in data_fetcher_mapping.keys():
        context = {}
    else:
        name_record, personal_details_record, home_address_record = data_fetcher_mapping[referrer_type](application_id)
        context = {
            'first_name': name_record.get('first_name'),
            'last_name': name_record.get('last_name'),
            'date_of_birth': personal_details_record.get('date_of_birth'),
            'street_line1': home_address_record.get('street_line1'),
            'street_line2': home_address_record.get('street_line2'),
            'town': home_address_record.get('town'),
            'postcode': home_address_record.get('postcode'),
            'application_id': application_id,
        }

    return render(request, 'childminder_templates/personal-details-individual-lookup.html', context)
