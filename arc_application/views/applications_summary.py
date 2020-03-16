import logging
from django.contrib.auth.decorators import login_required
from django.views import View
from django.utils.decorators import method_decorator
from django.shortcuts import render
from ..models import Application, Arc
from .audit_log import MockTimelineLog
from timeline_logger.models import TimelineLog
from ..services.db_gateways import NannyGatewayActions, HMGatewayActions
from django.conf import settings
from datetime import datetime, timedelta
from collections import OrderedDict

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
        :return: dictionary of adult, childminder and nanny totals submitted but unassigned each day
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
                if item.date_submitted.date() == initial_date.date():
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
                    if datetime.strptime(
                            nanny['date_submitted'], "%Y-%m-%dT%H:%M:%S.%fZ").date() == initial_date.date() and not None:
                        nanny_apps += 1

            apps_in_queue[initial_date.date()] = {'Childminder': cm_apps, 'Adult': adult_apps, 'Nanny': nanny_apps,
                                                  'Total': (cm_apps + adult_apps + nanny_apps)
                                                  }
            initial_date += delta

        return (apps_in_queue)

    def application_history(self, app_id, app_type):
        """
        function to list the history of an application extracted from the timeline log
        :return Dictionary grouped by application id, then by date, then by historical item"""
        dictionary = {}
        if app_type == 'Childminder':
            timelinelog = TimelineLog.objects.filter(object_id=str(app_id[0])).order_by('-timestamp')
        elif app_type == 'Adult':
            api_response = HMGatewayActions().list('timeline-log', params={'object_id': app_id})
            if api_response.status_code == 200:
                timelinelog = [MockTimelineLog(**log) for log in api_response.record]
            else:
                return dictionary
        elif app_type == 'Nanny':
            api_response = NannyGatewayActions().list('timeline-log', params={'object_id': app_id})
            if api_response.status_code == 200:
                timelinelog = [MockTimelineLog(**log) for log in api_response.record]
            else:
                return dictionary
        else:
            return dictionary


        return self.extract_timeline_history(timelinelog)

    def extract_timeline_history(self, timelinelog):
        """
        :param timelinelog: A queryset containing all the events that have occurred to an application.
        :return: A dictionary containing the relevant history of an application
        """
        dictionary = {}
        for entry in timelinelog:
            if entry.extra_data['action'] == 'created by':
                dictionary[entry.timestamp] = {'created by': entry.extra_data['user_type']}
            elif entry.extra_data['action'] == 'submitted by':
                dictionary[entry.timestamp] = {'submitted by': entry.extra_data['user_type']}
            elif entry.extra_data['action'] == 'assigned to':
                dictionary[entry.timestamp] = {'assigned_to': str(entry.user)}
            elif entry.extra_data['action'] == 'returned by':
                dictionary[entry.timestamp] = {'returned_by': str(entry.user)}
            elif entry.extra_data['action'] == 'resubmitted by':
                dictionary[entry.timestamp] = {'resubmitted_by': entry.extra_data['user_type']}
            elif entry.extra_data['action'] == 'accepted by':
                dictionary[entry.timestamp] = {'accepted_by': entry.extra_data['user_type']}
        dictionary = OrderedDict(sorted(dictionary.items(), key=lambda t: t[0]))
        return dictionary

    def get_application_histories(self):

        application_history = {}
        cm_application_id_list = Application.objects.all().values_list('application_id')
        application_history['Childminder'] = {}
        for app_id in cm_application_id_list:
            application_history['Childminder'][str(app_id[0])] = self.application_history(app_id, 'Childminder')

        adult_application_response = HMGatewayActions().list('adult', params={})
        if adult_application_response.status_code == 200:
            adult_application_records = adult_application_response.record
            application_history['Adult'] = {}
            for record in adult_application_records:
                app_id = record['adult_id']
                application_history['Adult'][app_id] = self.application_history(app_id, 'Adult')

        nanny_applications_response = NannyGatewayActions().list('application', params={})
        if nanny_applications_response.status_code == 200:
            nanny_applications_records = nanny_applications_response.record
            application_history['Nanny'] = {}
            for record in nanny_applications_records:
                application_history['Nanny'][record['application_id']] = self.application_history(
                    record['application_id'], 'Nanny')

        return application_history

    def get_applications_rereturned(self):
        """
        function to list the history of returned and rereturned applications on a given day.
        :return: Dictionary of adults, childminder and nannies returned or rereturned by day
        """

        returned_apps = {}
        now = datetime.now()
        initial_date = datetime(2020, 2, 19, 0, 0)
        delta = timedelta(days=1)
        applications_history = self.get_application_histories()
        app_types = ['Childminder', 'Adult', 'Nanny']
        while initial_date <= now:
            cm_apps = 0
            adult_apps = 0
            nanny_apps = 0
            for app_type in app_types:
                for app_id in applications_history[app_type]:
                    for date in applications_history[app_type][app_id]:
                        if date.date() == initial_date.date() and 'returned_by' in \
                                applications_history[app_type][app_id][date]:
                            if app_type == 'Childminder':
                                cm_apps += 1
                            elif app_type == 'Adult':
                                adult_apps += 1
                            elif app_type == 'Nanny':
                                nanny_apps += 1
            returned_apps[initial_date.date()] = {'Childminder': cm_apps, 'Adult': adult_apps,
                                                  'Nanny': nanny_apps,
                                                  'Total': (cm_apps + adult_apps + nanny_apps)
                                                  }
            initial_date += delta

        return (returned_apps)

    def get_applications_processed(self):
        """
        Get how many applications that are submitted on a day end up being returned
        :return: Dictionary of values representing number of returned applications by date and by application type
        """

        processed_apps = {}
        now = datetime.now()
        initial_date = datetime(2020, 2, 19, 0, 0)
        delta = timedelta(days=1)
        applications_history = self.get_application_histories()
        app_types = ['Childminder', 'Adult', 'Nanny']
        while initial_date <= now:
            cm_apps = 0
            cm_apps_returned = 0
            adult_apps = 0
            adult_apps_returned = 0
            nanny_apps = 0
            nanny_apps_returned = 0
            for app_type in app_types:
                for app_id in applications_history[app_type]:
                    date_list = list(applications_history[app_type][app_id].keys())
                    for i in range(0, len(date_list)):
                        for entry in applications_history[app_type][app_id][date_list[i]]:
                            if date_list[i].date() == initial_date.date() and entry == 'submitted by' or entry == 'resubmitted by':
                                reduced_dict = {your_key: applications_history[app_type][app_id][your_key] for your_key in date_list[i:]}
                                if app_type == 'Childminder':
                                    cm_apps += 1
                                    cm_apps_returned += self.check_if_returned(reduced_dict)
                                elif app_type == 'Adult':
                                    adult_apps += 1
                                    adult_apps_returned += self.check_if_returned(reduced_dict)
                                elif app_type == 'Nanny':
                                    nanny_apps += 1
                                    nanny_apps += self.check_if_returned(reduced_dict)

            processed_apps[initial_date.date()] = {'Childminder': cm_apps,
                                                   'Adult': adult_apps,
                                                    'Nanny': nanny_apps,
                                                    'Total': (cm_apps + adult_apps + nanny_apps)
                                                  }

            initial_date += delta
        return processed_apps

    def check_if_returned(self, dict):
        for date in dict:
            for entry in dict[date]:
                if entry == 'returned_by':
                    return 1
        return 0

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
        returned_apps = self.get_applications_rereturned()
        processed_apps = self.get_applications_processed()
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
