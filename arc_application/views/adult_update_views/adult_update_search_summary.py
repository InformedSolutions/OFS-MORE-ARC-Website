import json
import logging
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View

from .adult_update_summary import get_application_summary_variables
from ..base import has_group
from ...services.db_gateways import HMGatewayActions, IdentityGatewayActions

# Initiate logging
log = logging.getLogger()

@method_decorator(login_required, name='get')
class AdultUpdateSearchSummary(View):
    """
    View to render the Search Application Summary
    Shares many similarities with the NannyArcSummary View
    """
    TEMPLATE_NAME = 'adult_update_templates/hm_search_summary.html'

    def get(self, request):
        application_id = request.GET["id"]
        context = self.create_context(application_id)
        #log_user_opened_application(request, application_id)
        log.debug("Rendering adult update search summary")
        return render(request, self.TEMPLATE_NAME, context=context)

    def create_context(self, application_id):
        """
        Creates the context dictionary for this view.

        Major changes with the Search view include the try_get_context_data method calls.
        The general strategy of this view is the same, gather all context_dicts and generate the view.
        :param application_id: Reviewed application's id.
        :return: Context dictionary.
        """
        context = get_application_summary_variables(application_id)
        adult_record = HMGatewayActions().get('adult', params={'adult_id': application_id}).record
        applicant_record = IdentityGatewayActions().get('user-details', params={'application_id': adult_record['token_id']}).record

        applicant_details_summary = [
                {"title": "Applicant's details",
            "id": applicant_record['token_id']},
            {"name": "Email Address",
            "value": applicant_record['email']},
            ]
        context.add(0, applicant_details_summary)
        context = context[:2]
        return context
