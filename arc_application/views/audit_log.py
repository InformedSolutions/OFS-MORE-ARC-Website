from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.views.generic import ListView, View
from django.urls import reverse

from timeline_logger.models import TimelineLog

from arc_application.services.db_gateways import NannyGatewayActions
from arc_application.models import Application
from .base import has_group


def audit_log_dispatcher(request):
    """
    Dispatcher function to determine which view to call in handling the request.
    :param request: request to be handled.
    :return: Function call to either the Childminder or Nanny audit log view.
    """
    if request.GET['app_type']  == 'Childminder':
        return ChildminderAuditlog.as_view()(request)
    elif request.GET['app_type'] == 'Nanny':
        return NannyAuditLog.as_view()(request)
    else:
        raise ValueError('The "app_type" request.GET QueryDict does not equal either "Childminder" nor "Nanny".')


class ChildminderAuditlog(ListView):
    template_name = "auditlog_list.html"
    paginate_by = settings.TIMELINE_PAGINATE_BY

    def get_queryset(self, **kwargs):
        app_id = self.request.GET.get('id')
        queryset = TimelineLog.objects.filter(object_id=app_id).order_by('-timestamp')
        return queryset

    def get_context_data(self, **kwargs):
        context = super(ChildminderAuditlog, self).get_context_data(**kwargs)
        app_id = self.request.GET.get('id')
        try:
            context['application_reference'] = Application.objects.get(application_id=app_id).application_reference
        except ObjectDoesNotExist:
            context['application_reference'] = None

        if has_group(self.request.user, settings.CONTACT_CENTRE):
            context['back'] = reverse('search')
            context['cc_user'] = True

        if has_group(self.request.user, settings.ARC_GROUP):
            context['arc_user'] = True
            context['back'] = reverse('task_list') + '?id=' + self.request.GET.get('id')

        return context


class NannyAuditLog(View):
    template_name = "auditlog_list.html"

    def get_object_list(self):
        api_response = NannyGatewayActions().list('timeline-log', params={'object_id': self.request.GET['id']})
        return api_response.record

    def get_context_data(self):
        context = dict()
        application_id = self.request.GET.get('id')
        context['application_reference'] = NannyGatewayActions().read('application', params={'application_id': application_id}).record['application_reference']

        if has_group(self.request.user, settings.CONTACT_CENTRE):
            context['back'] = reverse('search')
            context['cc_user'] = True

        if has_group(self.request.user, settings.ARC_GROUP):
            context['arc_user'] = True
            context['back'] = reverse('task_list') + '?id=' + self.request.GET.get('id')

        context['object_list'] = self.get_object_list()

        return context

    def get(self, request):
        return render(request, self.template_name, context=self.get_context_data())
