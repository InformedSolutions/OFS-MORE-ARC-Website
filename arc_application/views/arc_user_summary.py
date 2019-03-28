import logging
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views import View
from django.utils.decorators import method_decorator

from ..services.application_handler import ChildminderApplicationHandler, GenericApplicationHandler, \
    NannyApplicationHandler

# Initiate logging
log = logging.getLogger()

@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class ARCUserSummaryView(View):
    template_name = 'arc_user_summary.html'

    def get(self, request):
        context = self.get_context_data()
        log.debug("Rendering arc user summary")
        return render(request, self.template_name, context=context)

    def post(self, request):

        if settings.ENABLE_NANNIES:
            if 'add_nanny_application' in request.POST:
                log.debug("Conditional logic: show nanny arc")
                app_handler = NannyApplicationHandler(arc_user=request.user)
        else:
            context = self.get_context_data()
            context['error_exist'] = 'true'
            context['error_title'] = 'Nannies application review is disabled'
            context['error_text'] = 'Nannies applications cannot be reviewed at this time.'

        if 'add_childminder_application' in request.POST:
            app_handler = ChildminderApplicationHandler(arc_user=request.user)

        try:
            app_handler.add_application_from_pool()
            context = self.get_context_data()

        except ObjectDoesNotExist:
            context = self.get_context_data()
            context['error_exist'] = 'true'
            context['error_title'] = 'No available applications'
            context['error_text'] = 'There are currently no more applications ready for a review'

        except PermissionDenied:
            context = self.get_context_data()
            context['error_exist'] = 'true'
            context['error_title'] = 'You have reached the limit'
            context['error_text'] = 'You have already reached the maximum (' + str(settings.APPLICATION_LIMIT) + ') applications'

        log.debug("Rendering arc user summary")
        return render(request, self.template_name, context=context)

    def get_context_data(self):
        context = dict()
        if settings.ENABLE_NANNIES:
            entries = GenericApplicationHandler(arc_user=self.request.user).get_all_table_data()
        else:
            entries = ChildminderApplicationHandler(arc_user=self.request.user).get_all_table_data()

        context['entries'] = entries

        if not len(context['entries']):
            context['empty'] = 'true'

        context['enable_nannies'] = settings.ENABLE_NANNIES

        return context
