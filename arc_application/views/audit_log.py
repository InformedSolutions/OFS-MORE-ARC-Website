from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import ListView
from django.urls import reverse

from timeline_logger.models import TimelineLog

from arc_application.models import Application
from .base import has_group


class AuditlogListView(ListView):
    template_name = "auditlog_list.html"
    paginate_by = settings.TIMELINE_PAGINATE_BY

    def get_queryset(self, **kwargs):
        app_id = self.request.GET.get('id')
        queryset = TimelineLog.objects.filter(object_id=app_id).order_by('-timestamp')
        return queryset

    def get_context_data(self, **kwargs):
        context = super(AuditlogListView, self).get_context_data(**kwargs)
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
