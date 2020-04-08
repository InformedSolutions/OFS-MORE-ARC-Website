import logging
from django.contrib.auth.decorators import login_required
from django.views import View
from django.utils.decorators import method_decorator
from ..models import Application, Arc, ApplicantName
import csv
from django.http import HttpResponse, StreamingHttpResponse
from django.contrib.auth.models import User
from .audit_log import MockTimelineLog
from timeline_logger.models import TimelineLog
from ..services.db_gateways import NannyGatewayActions, HMGatewayActions
from datetime import datetime, timedelta
from collections import OrderedDict
import time

from ..decorators import group_required


# Initiate logging
log = logging.getLogger()

class Echo(View):
    """An object that implements just the write method of the file-like
    interface.
    """
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value

class DailyReportingBaseView(Echo):

    def application_history(self, app_id, app_type):
        """
        function to list the history of an application extracted from the timeline log
        :return Dictionary grouped by application id, then by date, then by historical item"""
        dictionary = {}
        if app_type == 'Childminder':
            timelinelog = TimelineLog.objects.filter(object_id=app_id).order_by('-timestamp')
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
                dictionary[entry.timestamp] = {'Created': entry.extra_data['user_type']}
            elif entry.extra_data['action'] == 'submitted by':
                dictionary[entry.timestamp] = {'Submitted': entry.extra_data['user_type']}
            elif entry.extra_data['action'] == 'assigned to':
                dictionary[entry.timestamp] = {'Assigned': str(entry.user)}
            elif entry.extra_data['action'] == 'returned by':
                dictionary[entry.timestamp] = {'Returned': str(entry.user)}
            elif entry.extra_data['action'] == 'resubmitted by':
                dictionary[entry.timestamp] = {'Resubmitted': entry.extra_data['user_type']}
            elif entry.extra_data['action'] == 'accepted by':
                dictionary[entry.timestamp] = {'Processed to Cygnum': str(entry.user)}
            elif entry.extra_data['action'] == 'released by':
                dictionary[entry.timestamp] = {'Released': str(entry.user)}
        dictionary = OrderedDict(sorted(dictionary.items(), key=lambda t: t[0]))
        return dictionary

    def get_application_histories(self):

        application_history = {}
        cm_application_id_list = Application.objects.all().values_list('application_id')
        application_history['Childminder'] = {}
        for app_id in cm_application_id_list:
            application_history['Childminder'][str(app_id[0])] = self.application_history(str(app_id[0]), 'Childminder')

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

    def get_user(self, user_id):
        first_name = User.objects.get(id=user_id).first_name
        last_name = User.objects.get(id=user_id).last_name
        if first_name is not '':
            arc_user = '{0} {1}'.format(first_name, last_name if not '' else "")
        else:
            arc_user = User.objects.get(id=user_id).username
        return arc_user

@method_decorator(login_required, name='get')
class ApplicationsInQueueView(DailyReportingBaseView):

    def get(self, request):
        context = self.get_applications_in_queue()
        now = datetime.now()
        now = datetime.strftime(now, "%Y%m%dT%H%M")
        csv_columns = ['Date', 'Childminder in Queue', 'New Association in Queue',
                       'Nanny in Queue', 'All Services in Queue']
        pseudo_buffer = Echo()
        writer = csv.DictWriter(pseudo_buffer,  fieldnames=csv_columns)
        response = StreamingHttpResponse((writer.writerow(data) for data in context),
                                         content_type="text/csv")
        response['Content-Disposition'] = 'attachment; filename="Applications_in_Queue_{}.csv"'.format(now)
        log.debug("Rendering applications in queue (Reporting)")

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
        apps_in_queue = [({'Date': 'Date',
                                  'Childminder in Queue': 'Childminder in Queue',
                                  'New Association in Queue': 'New Association in Queue',
                                  'Nanny in Queue': 'Nanny in Queue',
                                  'All Services in Queue':  'All Services in Queue'
                                 })]
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
                            adult['date_submitted'][:19], "%Y-%m-%dT%H:%M:%S").date() == initial_date.date():
                        adult_apps += 1
                    elif adult['date_resubmitted'] is not None and datetime.strptime(
                            adult['date_resubmitted'][:19], "%Y-%m-%dT%H:%M:%S").date() == initial_date.date():
                        adult_apps += 1
            if nanny_response.status_code == 200:
                nannies_submitted = nanny_response.record
                for nanny in nannies_submitted:
                    if datetime.strptime(
                            nanny['date_submitted'][:19],
                            "%Y-%m-%dT%H:%M:%S").date() == initial_date.date() and not None:
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
        pseudo_buffer = Echo()
        writer = csv.DictWriter(pseudo_buffer, fieldnames=csv_columns)
        response = StreamingHttpResponse((writer.writerow(data) for data in context),
                                         content_type="text/csv")
        response['Content-Disposition'] = 'attachment; filename="Applications_Returned_{}.csv"'.format(now)
        log.debug("Rendering applications returned (Reporting)")

        return response

    def get_applications_returned(self):
        """
        function to list the history of returned and returned applications on a given day.
        :return: List of adults, childminder and nannies returned or returned by day
        """

        returned_apps = [({'Date': 'Date',
                           'Childminder returned': 'Childminder returned',
                           'New Association returned': 'New Association returned',
                           'Nanny returned': 'Nanny returned',
                           'All services returned': 'All services returned'})]
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
        csv_columns = ['Date', 'Childminder Processed to Cygnum', 'Childminder Returned', 'Childminder % returned',
                       'New Association Processed to Cygnum', 'New Association Returned', 'New Association % returned',
                       'Nanny Processed to Cygnum', 'Nanny Returned', 'Nanny % returned',
                       'All services Processed to Cygnum', 'All services Returned', 'All services % returned']
        pseudo_buffer = Echo()
        writer = csv.DictWriter(pseudo_buffer, fieldnames=csv_columns)
        response = StreamingHttpResponse((writer.writerow(data) for data in context),
                                         content_type="text/csv")
        response['Content-Disposition'] = 'attachment; filename="Applications_Processed_{}.csv"'.format(now)
        log.debug("Rendering applications processed (Reporting)")

        return response

    def get_applications_processed(self):
        """
        Get how many applications that are submitted on a day end up being returned
        :return: List of values representing number of returned applications by date and by application type
        """

        processed_apps = [({'Date': 'Date',
                            'Childminder Processed to Cygnum': 'Childminder Processed to Cygnum',
                            'Childminder Returned': 'Childminder Returned',
                            'Childminder % returned': 'Childminder % returned',
                            'New Association Processed to Cygnum':  'New Association Processed to Cygnum',
                            'New Association Returned': 'New Association Returned',
                            'New Association % returned': 'New Association % returned',
                            'Nanny Processed to Cygnum': 'Nanny Processed to Cygnum',
                            'Nanny Returned': 'Nanny Returned',
                            'Nanny % returned': 'Nanny % returned',
                            'All services Processed to Cygnum': 'All services Processed to Cygnum',
                            'All services Returned': 'All services Returned',
                            'All services % returned': 'All services % returned'})]
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
                            if date_list[i].date() == initial_date.date():
                                if entry == 'accepted_by':
                                    if app_type == 'Childminder':
                                        cm_apps += 1
                                    elif app_type == 'Adult':
                                        adult_apps += 1
                                    elif app_type == 'Nanny':
                                        nanny_apps += 1
                                elif entry == 'returned_by':
                                    if app_type == 'Childminder':
                                        cm_apps_returned += 1
                                    elif app_type == 'Adult':
                                        adult_apps_returned += 1
                                    elif app_type == 'Nanny':
                                        nanny_apps_returned += 1
            total_accepted = (cm_apps + adult_apps + nanny_apps)
            total_returned = (cm_apps_returned + adult_apps_returned + nanny_apps_returned)
            processed_apps.append({'Date': datetime.strftime(initial_date, "%d %B %Y"),
                                   'Childminder Processed to Cygnum': cm_apps,
                                   'Childminder Returned': cm_apps_returned,
                                   'Childminder % returned': (cm_apps_returned / (cm_apps + cm_apps_returned)) * 100 if cm_apps_returned is not 0 else 0,
                                   'New Association Processed to Cygnum': adult_apps,
                                   'New Association Returned': adult_apps_returned,
                                   'New Association % returned': (adult_apps_returned / (adult_apps + adult_apps_returned)) * 100 if adult_apps_returned is not 0 else 0,
                                   'Nanny Processed to Cygnum': nanny_apps,
                                   'Nanny Returned': nanny_apps_returned,
                                   'Nanny % returned': ((nanny_apps_returned / (nanny_apps + nanny_apps_returned)) * 100) if nanny_apps_returned is not 0 else 0,
                                   'All services Processed to Cygnum': total_accepted,
                                   'All services Returned': total_returned,
                                   'All services % returned': (total_returned / (total_accepted + total_returned)) * 100 if total_returned is not 0 else 0
                                   })

            initial_date += delta
        total_cm_accepted = 0
        total_cm_returned = 0
        total_adult_accepted = 0
        total_adult_returned = 0
        total_nanny_accepted = 0
        total_nanny_returned = 0
        total_all_services_accepted = 0
        total_all_services_returned = 0
        for i in processed_apps[1:]:
            total_cm_accepted += i['Childminder Processed to Cygnum']
            total_cm_returned += i['Childminder Returned']
            total_adult_accepted += i['New Association Processed to Cygnum']
            total_adult_returned += i['New Association Returned']
            total_nanny_accepted += i['Nanny Processed to Cygnum']
            total_nanny_returned += i['Nanny Returned']
            total_all_services_accepted += i['All services Processed to Cygnum']
            total_all_services_returned += i['All services Returned']
        processed_apps.append({'Date': 'Total',
                               'Childminder Processed to Cygnum': total_cm_accepted,
                               'Childminder Returned': total_cm_returned,
                               'Childminder % returned': (total_cm_returned / (total_cm_accepted + total_cm_returned)) * 100 if total_cm_returned is not 0 else 0,
                               'New Association Processed to Cygnum': total_adult_accepted,
                               'New Association Returned': total_adult_returned,
                               'New Association % returned': (total_adult_returned / (total_adult_accepted + total_adult_returned)) * 100 if total_adult_returned is not 0 else 0,
                               'Nanny Processed to Cygnum': total_nanny_accepted,
                               'Nanny Returned': total_nanny_returned,
                               'Nanny % returned': (total_nanny_returned / (total_nanny_accepted + total_nanny_returned)) * 100 if total_nanny_returned is not 0 else 0,
                               'All services Processed to Cygnum': total_all_services_accepted,
                               'All services Returned': total_all_services_returned,
                               'All services % returned': (total_all_services_returned / (total_all_services_accepted + total_all_services_returned)) * 100 if total_all_services_returned is not 0 else 0
                               })
        return processed_apps


@method_decorator(login_required, name='get')
class ApplicationsAssignedView(DailyReportingBaseView):

    def get(self, request):
        context = self.get_applications_assigned()
        now = datetime.now()
        now = datetime.strftime(now, "%Y%m%dT%H%M")
        csv_columns = ['URN', 'Caseworker', 'Type',
                       'Action', 'Created Date/Time',
                       'Assigned to Date/Time']
        pseudo_buffer = Echo()
        writer = csv.DictWriter(pseudo_buffer, fieldnames=csv_columns)
        response = StreamingHttpResponse((writer.writerow(data) for data in context),
                                         content_type="text/csv")
        response['Content-Disposition'] = 'attachment; filename="Applications_Assigned_{}.csv"'.format(now)
        log.debug("Download applications assigned (Reporting)")

        return response

    def get_applications_assigned(self):
        """
        Snapshot in time showing all applications and who they have been most recently assigned to
        :return: List with every URN and who the application has most recently been assigned to
        """

        assigned_apps = [({'URN': 'URN',
                           'Caseworker': 'Caseworker',
                           'Type': 'Type',
                           'Action': 'Action',
                           'Created Date/Time': 'Created Date/Time',
                           'Assigned to Date/Time': 'Assigned to Date/Time'})]
        adult_response = HMGatewayActions().list('adult', params={"adult_status": 'ARC_REVIEW'})
        nanny_response = NannyGatewayActions().list('application', params={"application_status": 'ARC_REVIEW'})
        cm_applications = list(Application.objects.filter(application_status='ARC_REVIEW', ))
        for app in cm_applications:
            app_id = app.application_id
            cm_assigned_history = self.application_history(app_id, 'Childminder')
            urn = Application.objects.get(application_id=app_id).application_reference
            user_id = Arc.objects.get(application_id=app_id).user_id
            formatted_created_date = datetime.strftime(list(cm_assigned_history)[0], "%d/%m/%y %H:%M")
            formatted_assigned_date = datetime.strftime(list(cm_assigned_history)[-1], "%d/%m/%y %H:%M")
            assigned_apps.append({'URN': urn, 'Caseworker': self.get_user(user_id),
                                  'Type': 'CM', 'Action': 'Assigned',
                                  'Created Date/Time': formatted_created_date,
                                  'Assigned to Date/Time': formatted_assigned_date})

        if adult_response.status_code == 200:
            adults_assigned = adult_response.record
            for adult in adults_assigned:
                adult_assigned_history = self.application_history(adult['adult_id'], 'Adult')
                urn = HMGatewayActions().list('dpa-auth', params={'adult_id': adult['adult_id']}).record[0]['URN']
                user_id = Arc.objects.get(application_id=app_id).user_id
                formatted_created_date = datetime.strftime(list(adult_assigned_history)[0], "%d/%m/%y %H:%M")
                formatted_assigned_date = datetime.strftime(list(adult_assigned_history)[-1], "%d/%m/%y %H:%M")
                assigned_apps.append({'URN': urn, 'Caseworker': self.get_user(user_id), 'Type': 'New Association',
                                      'Action': 'Assigned',
                                      'Created Date/Time': formatted_created_date,
                                      'Assigned to Date/Time': formatted_assigned_date})

        if nanny_response.status_code == 200:
            nannies_assigned = nanny_response.record
            for nanny in nannies_assigned:
                nanny_assigned_history = self.application_history(nanny['application_id'], 'Nanny')
                urn = nanny['application_reference']
                user_id = Arc.objects.get(application_id=nanny['application_id']).user_id
                formatted_created_date = datetime.strftime(list(nanny_assigned_history)[0], "%d/%m/%y %H:%M")
                formatted_assigned_date = datetime.strftime(list(nanny_assigned_history)[-1], "%d/%m/%y %H:%M")
                assigned_apps.append({'URN': urn, 'Caseworker': self.get_user(user_id), 'Type': 'Nanny',
                                      'Action': 'Assigned',
                                      'Created Date/Time': formatted_created_date,
                                      'Assigned to Date/Time': formatted_assigned_date})

        return assigned_apps

@method_decorator(login_required, name='get')
class ApplicationsAuditLogView(DailyReportingBaseView):

    def get(self, request):
        context = self.get_applications_audit_log()
        now = datetime.now()
        now = datetime.strftime(now, "%Y%m%dT%H%M")
        csv_columns = ['URN', 'Name', 'Caseworker', 'Type',
                       'Action', 'Date/Time']
        pseudo_buffer = Echo()
        writer = csv.DictWriter(pseudo_buffer, fieldnames=csv_columns)
        response = StreamingHttpResponse((writer.writerow(data) for data in context),
                                         content_type="text/csv")
        response['Content-Disposition'] = 'attachment; filename="Applications_Audit_Log_{}.csv"'.format(now)
        log.debug("Download application audit log (Reporting)")

        return response

    def get_user_from_username(self, username):
        if username == 'applicant':
            return ''
        elif username == 'adult':
            return ''
        else:
            first_name = User.objects.get(username=username).first_name
            last_name = User.objects.get(username=username).last_name
            if first_name is not '':
                arc_user = '{0} {1}'.format(first_name, last_name if not '' else "")
            else:
                arc_user = User.objects.get(username=username).username
            return arc_user

    def get_applications_audit_log(self):
        """
        Snapshot in time showing the history of each application
        :return: List with every URN and who the application has most recently been assigned to
        """

        audit_log = [({'URN': 'URN',
                       'Name': 'Name',
                       'Caseworker': 'Caseworker',
                       'Type': 'Type',
                       'Action': 'Action',
                       'Date/Time': 'Date/Time',
                       })]
        applications_history = self.get_application_histories()

        for k1, v1 in applications_history.items():
            for k2, v2 in v1.items():
                if k1 == 'Childminder':
                    if ApplicantName.objects.filter(application_id=k2).exists():
                        name = ApplicantName.objects.get(application_id=k2)
                        full_name = name.first_name + " " + name.last_name
                    else:
                        full_name = ''
                    urn = Application.objects.get(application_id=k2).application_reference
                elif k1 == 'Adult':
                    urn = HMGatewayActions().list('dpa-auth', params={'adult_id': k2}).record[0]['URN']
                    full_name = HMGatewayActions().list('adult', params={'adult_id': k2}).record[0]['get_full_name']
                elif k1 == 'Nanny':
                    urn = NannyGatewayActions().list('application', params={'application_id': k2}).record[0][
                        'application_reference']
                    response = NannyGatewayActions().list('applicant-personal-details',
                                                          params={'application_id': k2})
                    if response.status_code == 200:
                        record = response.record[0]
                        full_name = record['first_name'] + " " + record['last_name']
                    else:
                        full_name = ''
                for k3, v3 in v2.items():
                    formatted_date = datetime.strftime(k3, "%d/%m/%y %H:%M")
                    k4, v4 = list(v3.keys())[0], list(v3.values())[0]
                    if k1 == 'Childminder':
                        audit_log.append({'URN': urn, 'Name': full_name,
                                          'Caseworker': self.get_user_from_username(v4), 'Type': 'CM', 'Action': k4,
                                          'Date/Time': formatted_date})
                    elif k1 == 'Adult':
                        audit_log.append({'URN': urn, 'Name': full_name,
                                          'Caseworker': self.get_user_from_username(v4), 'Type': 'New Association',
                                          'Action': k4, 'Date/Time': formatted_date})
                    elif k1 == 'Nanny':
                        audit_log.append({'URN': urn, 'Name': full_name,
                                          'Caseworker': self.get_user_from_username(v4), 'Type': 'Nanny', 'Action': k4,
                                          'Date/Time': formatted_date})
        return audit_log