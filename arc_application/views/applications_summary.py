from django.contrib.auth.decorators import login_required
from django.views import View
from django.utils.decorators import method_decorator
from django.shortcuts import render
from ..models import Application
from .. services.db_gateways import NannyGatewayActions

@method_decorator(login_required, name='get')
class ApplicationsSummaryView(View):
    template_name = "applications_summary.html"

    def get(self, request):
        context = self.get_context_data()
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

        # get applications which have been submitted
        # get applications in arc review
        arc_apps_response = NannyGatewayActions().list("application", params={'application_status': "ARC_REVIEW"})
        nanny_data['arc_applications'] = len(
            arc_apps_response.record) if arc_apps_response.status_code == 200 else 0
        # sum all applications not in drafting
        nanny_data['non_draft_applications'] = nanny_data['pending_applications'] + nanny_data['returned_applications'] \
                         + nanny_data['new_applications'] + nanny_data['arc_applications']

        return nanny_data
              

    def get_context_data(self):
        context = {}
        childminder_data = self.get_childminder_data()
        nanny_data = self.get_nanny_data()
        context["rows"] = [
            {
                'id': 'draft',
                'name': 'Draft',
                'childminder': childminder_data['draft_applications'],
                'nanny': nanny_data['draft_applications']
            },
            {
                'id': 'total_submitted',
                'name': 'Total submitted',
                'childminder': childminder_data['non_draft_applications'],
                'nanny': nanny_data['non_draft_applications']
            },
            {
                'id': 'new',
                'name': 'New',
                'childminder': childminder_data['new_applications'],
                'nanny': nanny_data['new_applications']
            },
            {
                'id': 'returned',
                'name': 'Returned',
                'childminder': childminder_data['returned_applications'],
                'nanny': nanny_data['returned_applications']
            },
            {
                'id': 'pending',
                'name': 'Processed to Cygnum',
                'childminder': childminder_data['pending_applications'],
                'nanny': nanny_data['pending_applications']
            }
        ]
        return context
