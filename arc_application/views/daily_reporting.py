import logging
from django.contrib.auth.decorators import login_required
from django.views import View
from django.utils.decorators import method_decorator
from django.shortcuts import render
from ..models import Application
import csv
from django.http import HttpResponse
from django.contrib.auth.models import User
from .audit_log import MockTimelineLog
from timeline_logger.models import TimelineLog
from ..services.db_gateways import NannyGatewayActions, HMGatewayActions
from django.conf import settings
from datetime import datetime, timedelta
from collections import OrderedDict


# Initiate logging
log = logging.getLogger()

class DailyReportingBaseView(View):

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
                dictionary[entry.timestamp] = {'accepted_by': str(entry.user)}
            elif entry.extra_data['action'] == 'released by':
                dictionary[entry.timestamp] = {'released_by': str(entry.user)}
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

@method_decorator(login_required, name='get')
class ApplicationsInQueueView(DailyReportingBaseView):

    def get(self, request):
        context = self.get_applications_in_queue()
        now = datetime.now()
        now = datetime.strftime(now, "%Y%m%dT%H%M")
        csv_columns = ['Date', 'Childminder in Queue', 'New Association in Queue',
                       'Nanny in Queue', 'All Services in Queue']
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Applications_in_Queue_{}.csv"'.format(now)
        log.debug("Rendering applications summary (Reporting)")

        writer = csv.DictWriter(response, fieldnames=csv_columns)
        writer.writeheader()
        for data in context:
            writer.writerow(data)

        return response


    def get_applications_in_queue(self):
        """
        function to list any application that has a status of SUBMITTED, grouped by date and by application.
        :return: list of adult, childminder and nanny totals submitted but unassigned each day
        """
        now = datetime.now()
        initial_date = datetime(2020, 2, 19, 0, 0)
        delta = timedelta(days=1)
        adult_response = HMGatewayActions().list('adult', params={"adult_status": 'SUBMITTED'})
        nanny_response = NannyGatewayActions().list('application', params={"application_status": 'SUBMITTED'})
        cm_applications = list(Application.objects.filter(application_status='SUBMITTED', ))
        apps_in_queue = []
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
                            nanny['date_submitted'],
                            "%Y-%m-%dT%H:%M:%S.%fZ").date() == initial_date.date() and not None:
                        nanny_apps += 1

            apps_in_queue.append({'Date': datetime.strftime(initial_date, "%d %B %Y"),
                                  'Childminder in Queue': cm_apps,
                                  'New Association in Queue': adult_apps,
                                  'Nanny in Queue': nanny_apps,
                                  'All Services in Queue': (cm_apps + adult_apps + nanny_apps)
                                 })
            initial_date += delta

        apps_in_queue.append(
            {'Date': 'Total', 'Childminder in Queue': len(cm_applications),
             'New Association in Queue': len(adult_response.record) if adult_response.status_code == 200 else 0,
             'Nanny in Queue': len(nanny_response.record) if nanny_response.status_code == 200 else 0,
             'All Services in Queue': (len(cm_applications) +
                                       (len(adult_response.record) if adult_response.status_code == 200 else 0) +
                                       (len(nanny_response.record) if nanny_response.status_code == 200 else 0))
             })

        return (apps_in_queue)


@method_decorator(login_required, name='get')
class ApplicationsReturnedView(DailyReportingBaseView):

    def get(self, request):
        context = self.get_applications_returned()
        now = datetime.now()
        now = datetime.strftime(now, "%Y%m%dT%H%M")
        csv_columns = ['Date', 'Childminder returned', 'New Association returned',
                       'Nanny returned', 'All services returned']
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Applications_Returned_{}.csv"'.format(now)
        log.debug("Rendering applications summary (Reporting)")

        writer = csv.DictWriter(response, fieldnames=csv_columns)
        writer.writeheader()
        for data in context:
            writer.writerow(data)

        return response

    def get_applications_returned(self):
        """
        function to list the history of returned and returned applications on a given day.
        :return: List of adults, childminder and nannies returned or returned by day
        """

        returned_apps = []
        now = datetime.now()
        initial_date = datetime(2020, 2, 19, 0, 0)
        delta = timedelta(days=1)
        applications_history = self.get_application_histories()
        app_types = ['Childminder', 'Adult', 'Nanny']
        cm_app_total = 0
        adult_app_total = 0
        nanny_app_total = 0
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
                                cm_app_total += 1
                            elif app_type == 'Adult':
                                adult_apps += 1
                                adult_app_total += 1
                            elif app_type == 'Nanny':
                                nanny_apps += 1
                                nanny_app_total += 1
            returned_apps.append({'Date': datetime.strftime(initial_date, "%d %B %Y"),
                                  'Childminder returned': cm_apps, 'New Association returned': adult_apps,
                                  'Nanny returned': nanny_apps,
                                  'All services returned': (cm_apps + adult_apps + nanny_apps)
                                  })
            initial_date += delta

        returned_apps.append(
            {'Date': 'Total', 'Childminder returned': cm_app_total, 'New Association returned': adult_app_total,
             'Nanny returned': nanny_app_total,
             'All services returned': (cm_app_total + adult_app_total + nanny_app_total)
             })

        return (returned_apps)


@method_decorator(login_required, name='get')
class ApplicationsProcessedView(DailyReportingBaseView):

    def get(self, request):
        context = self.get_applications_processed()
        now = datetime.now()
        now = datetime.strftime(now, "%Y%m%dT%H%M")
        csv_columns = ['Date', 'Childminder Received', 'Childminder Returned', 'Childminder % returned',
                       'New Association Received', 'New Association Returned', 'New Association % returned',
                       'Nanny Received', 'Nanny Returned', 'Nanny % returned',
                       'All services Received', 'All services Returned', 'All services % returned']
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Applications_Processed_{}.csv"'.format(now)
        log.debug("Rendering applications summary (Reporting)")

        writer = csv.DictWriter(response, fieldnames=csv_columns)
        writer.writeheader()
        for data in context:
            writer.writerow(data)

        return response

    def get_applications_processed(self):
        """
        Get how many applications that are submitted on a day end up being returned
        :return: List of values representing number of returned applications by date and by application type
        """

        processed_apps = []
        now = datetime.now()
        initial_date = datetime(2020, 2, 19, 0, 0)
        delta = timedelta(days=1)
        applications_history = self.get_application_histories()
        app_types = ['Childminder', 'Adult', 'Nanny']
        cm_app_total = 0
        adult_app_total = 0
        nanny_app_total = 0
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
                            if date_list[i].date() == initial_date.date():
                                if entry == 'submitted by' or entry == 'resubmitted by':
                                    reduced_dict = {your_key: applications_history[app_type][app_id][your_key] for
                                                    your_key in date_list[i:]}
                                    if app_type == 'Childminder':
                                        cm_apps += 1
                                        cm_apps_returned += self.check_if_returned(reduced_dict)
                                    elif app_type == 'Adult':
                                        adult_apps += 1
                                        adult_apps_returned += self.check_if_returned(reduced_dict)
                                    elif app_type == 'Nanny':
                                        nanny_apps += 1
                                        nanny_apps_returned += self.check_if_returned(reduced_dict)
            total_received = (cm_apps + adult_apps + nanny_apps)
            total_returned = (cm_apps_returned + adult_apps_returned + nanny_apps_returned)
            processed_apps.append({'Date': datetime.strftime(initial_date, "%d %B %Y"),
                                   'Childminder Received': cm_apps,
                                   'Childminder Returned': cm_apps_returned,
                                   'Childminder % returned': (cm_apps_returned / cm_apps) * 100 if cm_apps and cm_apps_returned is not 0 else 0,
                                   'New Association Received': adult_apps,
                                   'New Association Returned': adult_apps_returned,
                                   'New Association % returned': (adult_apps_returned / adult_apps) * 100 if adult_apps and adult_apps_returned is not 0 else 0,
                                   'Nanny Received': nanny_apps,
                                   'Nanny Returned': nanny_apps_returned,
                                   'Nanny % returned': (nanny_apps_returned / nanny_apps) * 100 if nanny_apps and nanny_apps_returned is not 0 else 0,
                                   'All services Received': total_received,
                                   'All services Returned': total_returned,
                                   'All services % returned': total_returned / total_received * 100 if total_received and total_returned is not 0 else 0
                                   })

            initial_date += delta
        total_cm_received = 0
        total_cm_returned = 0
        total_adult_received = 0
        total_adult_returned = 0
        total_nanny_received = 0
        total_nanny_returned = 0
        total_all_services_received = 0
        total_all_services_returned = 0
        for i in processed_apps:
            total_cm_received += i['Childminder Received']
            total_cm_returned += i['Childminder Returned']
            total_adult_received += i['New Association Received']
            total_adult_returned += i['New Association Returned']
            total_nanny_received += i['Nanny Received']
            total_nanny_returned += i['Nanny Returned']
            total_all_services_received += i['All services Received']
            total_all_services_returned += i['All services Returned']
        processed_apps.append({'Date': 'Total',
                               'Childminder Received': total_cm_received,
                               'Childminder Returned': total_cm_returned,
                               'Childminder % returned': (
                                                                     total_cm_returned / total_cm_received) * 100 if total_cm_received and total_cm_returned is not 0 else 0,
                               'New Association Received': total_adult_received,
                               'New Association Returned': total_adult_returned,
                               'New Association % returned': (
                                                                         total_adult_returned / total_adult_received) * 100 if total_adult_received and total_adult_returned is not 0 else 0,
                               'Nanny Received': total_nanny_received,
                               'Nanny Returned': nanny_apps_returned,
                               'Nanny % returned': (
                                                               total_nanny_returned / total_nanny_received) * 100 if total_nanny_received and total_nanny_returned is not 0 else 0,
                               'All services Received': total_all_services_received,
                               'All services Returned': total_all_services_returned,
                               'All services % returned': total_all_services_returned / total_all_services_received * 100 if total_all_services_received and total_all_services_returned is not 0 else 0
                               })
        return processed_apps

    def check_if_returned(self, dict):
        for date in dict:
            for entry in dict[date]:
                if entry == 'returned_by':
                    return 1
        return 0


@method_decorator(login_required, name='get')
class ApplicationsAssignedView(DailyReportingBaseView):

    def get(self, request):
        context = self.get_applications_assigned()
        now = datetime.now()
        now = datetime.strftime(now, "%Y%m%dT%H%M")
        csv_columns = ['URN', 'Caseworker', 'Type',
                       'Action', 'Date/Time']
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Applications_Assigned_{}.csv"'.format(now)
        log.debug("Download applications assigned (Reporting)")

        writer = csv.DictWriter(response, fieldnames=csv_columns)
        writer.writeheader()
        for data in context:
            writer.writerow(data)

        return response

    def get_applications_assigned(self):
        """
        Snapshot in time showing all applications and who they have been most recently assigned to
        :return: List with every URN and who the application has most recently been assigned to
        """

        assigned_apps = []
        applications_history = self.get_application_histories()
        app_types = ['Childminder', 'Adult', 'Nanny']
        for app_type in app_types:
            for app_id in applications_history[app_type]:
                assigned, username, date = self.check_assigned(applications_history[app_type][app_id])
                if assigned:
                    first_name = User.objects.get(username=username).first_name
                    last_name = User.objects.get(username=username).last_name
                    if first_name is not '':
                        arc_user = '{0} {1}'.format(first_name, last_name if not '' else "")
                    else:
                        arc_user = username
                    date = datetime.strftime(date, "%d/%m/%y %H:%M")
                    if app_type == 'Childminder':
                        urn = Application.objects.get(application_id=app_id).application_reference
                        assigned_apps.append({'URN': urn, 'Caseworker': arc_user, 'Type': 'CM', 'Action': 'Assigned',
                                              'Date/Time': date})
                    elif app_type == 'Adult':
                        urn = HMGatewayActions().list('dpa-auth', params={'adult_id': app_id}).record[0]['URN']
                        assigned_apps.append({'URN': urn, 'Caseworker': arc_user, 'Type': 'New Association',
                                              'Action': 'Assigned',
                                              'Date/Time': date})
                    elif app_type == 'Nanny':
                        urn = NannyGatewayActions().list('application', params={'application_id': app_id}).record[0][
                            'application_reference']
                        assigned_apps.append({'URN': urn, 'Caseworker': arc_user, 'Type': 'Nanny', 'Action': 'Assigned',
                                              'Date/Time': date})

        return assigned_apps

    def check_assigned(self, dict):
        for date in dict:
            for entry in dict[date]:
                if entry == 'assigned_to':
                    return (True, dict[date][entry], date)
        return False, None, None

@method_decorator(login_required, name='get')
class ApplicationsAuditLogView(DailyReportingBaseView):

    def get(self, request):
        context = self.get_applications_audit_log()
        now = datetime.now()
        now = datetime.strftime(now, "%Y%m%dT%H%M")
        csv_columns = ['URN', 'Caseworker', 'Type',
                       'Action', 'Date/Time']
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Applications_Audit_Log_{}.csv"'.format(now)
        log.debug("Download applications assigned (Reporting)")

        writer = csv.DictWriter(response, fieldnames=csv_columns)
        writer.writeheader()
        for data in context:
            writer.writerow(data)

        return response

    def get_applications_audit_log(self):
        """
        Snapshot in time showing the history of each application
        :return: List with every URN and who the application has most recently been assigned to
        """

        audit_log = []
        applications_history = self.get_application_histories()
        app_types = ['Childminder', 'Adult', 'Nanny']
        for app_type in app_types:
            for app_id in applications_history[app_type]:
                for date in applications_history[app_type][app_id]:
                    formatted_date = datetime.strftime(date, "%d/%m/%y %H:%M")
                    if 'created by' in applications_history[app_type][app_id][date]:
                        action = 'Created'
                        arc_user = ''
                    elif 'submitted by' in applications_history[app_type][app_id][date]:
                        action = 'Submitted'
                        arc_user = ''
                    elif 'assigned_to' in applications_history[app_type][app_id][date]:
                        username = applications_history[app_type][app_id][date]['assigned_to']
                        first_name = User.objects.get(username=username).first_name
                        last_name = User.objects.get(username=username).last_name
                        if first_name is not '':
                            arc_user = '{0} {1}'.format(first_name, last_name if not '' else "")
                        else:
                            arc_user = username
                        action = 'Assigned'
                    elif 'accepted_by' in applications_history[app_type][app_id][date]:
                        username = applications_history[app_type][app_id][date]['accepted_by']
                        first_name = User.objects.get(username=username).first_name
                        last_name = User.objects.get(username=username).last_name
                        if first_name is not '':
                            arc_user = '{0} {1}'.format(first_name, last_name if not '' else "")
                        else:
                            arc_user = username
                        action = 'Processed to Cygnum'
                    elif 'resubmitted_by' in applications_history[app_type][app_id][date]:
                        arc_user = ''
                        action = 'Resubmitted'
                    elif 'returned_by' in applications_history[app_type][app_id][date]:
                        username = applications_history[app_type][app_id][date]['returned_by']
                        first_name = User.objects.get(username=username).first_name
                        last_name = User.objects.get(username=username).last_name
                        if first_name is not '':
                            arc_user = '{0} {1}'.format(first_name, last_name if not '' else "")
                        else:
                            arc_user = username
                        arc_user = username
                        action = 'Returned'
                    elif 'released_by' in applications_history[app_type][app_id][date]:
                        username = applications_history[app_type][app_id][date]['released_by']
                        first_name = User.objects.get(username=username).first_name
                        last_name = User.objects.get(username=username).last_name
                        if first_name is not '':
                            arc_user = '{0} {1}'.format(first_name, last_name if not '' else "")
                        else:
                            arc_user = username
                        arc_user = username
                        action = 'Released'
                    if app_type == 'Childminder':
                        urn = Application.objects.get(application_id=app_id).application_reference
                        audit_log.append({'URN': urn, 'Caseworker': arc_user, 'Type': 'CM', 'Action': action,
                                                  'Date/Time': formatted_date})
                    elif app_type == 'Adult':
                        urn = HMGatewayActions().list('dpa-auth', params={'adult_id': app_id}).record[0]['URN']
                        audit_log.append({'URN': urn, 'Caseworker': arc_user, 'Type': 'New Association',
                                              'Action': action, 'Date/Time': formatted_date})
                    elif app_type == 'Nanny':
                        urn = NannyGatewayActions().list('application', params={'application_id': app_id}).record[0][
                            'application_reference']
                        audit_log.append({'URN': urn, 'Caseworker': arc_user, 'Type': 'Nanny', 'Action': action,
                                              'Date/Time': formatted_date})

        return audit_log