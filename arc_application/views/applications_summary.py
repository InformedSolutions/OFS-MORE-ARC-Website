import logging
from django.contrib.auth.decorators import login_required
from django.views import View
from django.utils.decorators import method_decorator
from django.shortcuts import render
from ..models import Application
from .. services.db_gateways import NannyGatewayActions, HMGatewayActions
from django.conf import settings
from datetime import datetime, timedelta

# Initiate logging
log = logging.getLogger()

@method_decorator(login_required, name='get')
class ApplicationsSummaryView(View):
    template_name = "applications_summary.html"

    def get(self, request):
        context = self.get_context_data()
        log.debug("Rendering applications summary (Reporting)")
        return render(request, self.template_name, context=context)

    def get_childminder_data(self):
        """
        Function to return a dictionary of data for childminder applications at different statuses
        :return: dictionary of childminder application data
        """
        cm_data = {}

        # get lists of applications at each status
        cm_data['draft_applications'] = len(list(Application.objects.filter(application_status="DRAFTING")))
        cm_data['non_draft_applications'] = len(list(Application.objects.exclude(application_status="DRAFTING")))
        cm_data['new_applications'] = len(list(Application.objects.filter(application_status="SUBMITTED")))
        cm_data['returned_applications'] = len(list(Application.objects.filter(application_status="FURTHER_INFORMATION")))
        cm_data['pending_applications'] = len(list(Application.objects.filter(application_status="ACCEPTED")))

        return cm_data

    def get_nanny_data(self):
        """
        Function to return a dictionary of data for nannies applications at different statuses
        :return: dictionary of nannies application data
        """
        nanny_data = {}
        # get applications at draft stage
        draft_apps_response = NannyGatewayActions().list("application", params={'application_status': "DRAFTING"})
        nanny_data['draft_applications'] = len(draft_apps_response.record) if draft_apps_response.status_code == 200 else 0

        # get new applications
        new_apps_response = NannyGatewayActions().list("application", params={'application_status': "SUBMITTED"})
        nanny_data['new_applications'] = len(new_apps_response.record) if new_apps_response.status_code == 200 else 0

        # get returned applications
        returned_apps_response = NannyGatewayActions().list("application", params={'application_status': "FURTHER_INFORMATION"})
        nanny_data['returned_applications'] = len(returned_apps_response.record) if returned_apps_response.status_code == 200 else 0

        # get pending applications
        pending_apps_response = NannyGatewayActions().list("application",
                                                            params={'application_status': "ACCEPTED"})
        nanny_data['pending_applications'] = len(
            pending_apps_response.record) if pending_apps_response.status_code == 200 else 0

        # get all applications
        total_apps_response = NannyGatewayActions().list("application", params={})
        total_applications = len(total_apps_response.record) if total_apps_response.status_code == 200 else 0
        # take any applications in draft off the number of total applications
        nanny_data['non_draft_applications'] = total_applications - nanny_data[
            "draft_applications"]

        return nanny_data

    def get_hm_data(self):
        """
        Function to return a dictionary of data for additional household member applications at different statuses
        :return: dictionary of household members data
        """
        household_member_data = {}
        # get applications at draft stage, some of which will be in the 'waiting' status
        draft_apps_response = HMGatewayActions().list("adult", params={'adult_status': "DRAFTING"})
        waiting_apps_response = HMGatewayActions().list("adult", params={'adult_status': 'WAITING'})
        draft_applications = len(
            draft_apps_response.record) if draft_apps_response.status_code == 200 else 0
        waiting_applications = len(
            waiting_apps_response.record) if waiting_apps_response.status_code == 200 else 0
        household_member_data['draft_applications'] = draft_applications + waiting_applications

        # get new applications
        new_apps_response = HMGatewayActions().list("adult", params={'adult_status': "SUBMITTED"})
        household_member_data['new_applications'] = len(new_apps_response.record) if new_apps_response.status_code == 200 else 0

        # get returned applications
        returned_apps_response = HMGatewayActions().list("adult",
                                                            params={'adult_status': "FURTHER_INFORMATION"})
        household_member_data['returned_applications'] = len(
            returned_apps_response.record) if returned_apps_response.status_code == 200 else 0

        # get pending applications
        pending_apps_response = HMGatewayActions().list("adult",
                                                           params={'adult_status': "ACCEPTED"})
        household_member_data['pending_applications'] = len(
            pending_apps_response.record) if pending_apps_response.status_code == 200 else 0

        # get all applications
        total_apps_response = HMGatewayActions().list("adult", params={})
        total_applications = len(total_apps_response.record) if total_apps_response.status_code == 200 else 0
        # take any applications in draft off the number of total applications
        household_member_data['non_draft_applications'] = total_applications - household_member_data["draft_applications"]

        return household_member_data

    def extract_applications_in_queue(self):
        """
        function to list any application that has a status of SUBMITTED, grouped by date and by application.
        :return: list of adult, childminder and nanny records
        """
        now = datetime.now()
        initial_date = datetime(2020, 2, 19, 0, 0)
        delta = timedelta(days=1)
        adult_response = HMGatewayActions().list('adult', params={"adult_status": 'SUBMITTED'})
        nanny_response = NannyGatewayActions().list('application', params={"application_status": 'SUBMITTED'})
        cm_applications = list(Application.objects.filter(application_status='SUBMITTED', ))
        apps_in_queue = {}
        while initial_date <= now:
            cm_apps = 0
            adult_apps = 0
            nanny_apps = 0
            for item in cm_applications:
                if item.date_submitted == initial_date:
                    cm_apps += 1
            if adult_response.status_code == 200:
                adults_submitted = adult_response.record
                for adult in adults_submitted:
                    if adult['date_resubmitted'] is None and datetime.strptime(
                            adult['date_submitted'], "%Y-%m-%dT%H:%M:%S.%fZ").date() == initial_date.date():
                        adult_apps += 1
                    elif adult['date_resubmitted'] is not None and datetime.strptime(
                            adult['date_resubmitted'], "%Y-%m-%dT%H:%M:%S.%fZ").date() == initial_date.date():
                        adult_apps += 1
            if nanny_response.status_code == 200:
                nannies_submitted = nanny_response.record
                for nanny in nannies_submitted:
                    if nanny['date_submitted'] == initial_date and not None:
                        nanny_apps += 1

            apps_in_queue['Date'] = initial_date.isoformat()
            apps_in_queue['Date'] = {'Childminder': cm_apps, 'Adult': adult_apps, 'Nanny': nanny_apps}
            initial_date += delta

        return (apps_in_queue)
              
    def get_context_data(self):
        """
        method to get all row data for the applications summary
        :return: context data
        """
        context = {}
        childminder_data = self.get_childminder_data()
        nanny_data = self.get_nanny_data()
        context['enable_hm'] = False
        hm_data = {}
        apps_in_queue = self.extract_applications_in_queue()
        if settings.ENABLE_HM:
            hm_data = self.get_hm_data()
            context['enable_hm'] = True
        context["rows"] = [
            {
                'id': 'draft',
                'name': 'Draft',
                'childminder': childminder_data['draft_applications'],
                'nanny': nanny_data['draft_applications'],
                'hm': hm_data['draft_applications'] if hm_data.get('draft_applications') else 0
            },
            {
                'id': 'total_submitted',
                'name': 'Total submitted',
                'childminder': childminder_data['non_draft_applications'],
                'nanny': nanny_data['non_draft_applications'],
                'hm': hm_data['non_draft_applications'] if hm_data.get('non_draft_applications') else 0
            },
            {
                'id': 'new',
                'name': 'New',
                'childminder': childminder_data['new_applications'],
                'nanny': nanny_data['new_applications'],
                'hm': hm_data['new_applications'] if hm_data.get('new_applications') else 0
            },
            {
                'id': 'returned',
                'name': 'Returned',
                'childminder': childminder_data['returned_applications'],
                'nanny': nanny_data['returned_applications'],
                'hm': hm_data['returned_applications'] if hm_data.get('returned_applications') else 0
            },
            {
                'id': 'pending',
                'name': 'Processed to Cygnum',
                'childminder': childminder_data['pending_applications'],
                'nanny': nanny_data['pending_applications'],
                'hm': hm_data['pending_applications'] if hm_data.get('pending_applications') else 0
            }
        ]
        return context
