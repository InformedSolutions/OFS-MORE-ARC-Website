from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.utils.decorators import method_decorator

from arc_application.services.db_gateways import NannyGatewayActions
from arc_application.models import Arc
from arc_application.review_util import build_url


@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class NannyInsuranceCoverSummary(View):
    TEMPLATE_NAME = 'nanny_general_template.html'
    FORM_NAME = ''
    REDIRECT_NAME = 'nanny_task_list'

    def get(self, request):

        # Get application ID
        application_id = request.GET["id"]

        context = self.create_context(application_id)

        return render(request, self.TEMPLATE_NAME, context=context)

    def post(self, request):

        # Get application ID
        application_id = request.POST["id"]

        # Update task status to COMPLETED
        arc_application = Arc.objects.get(application_id=application_id)
        arc_application.insurance_cover_review = 'COMPLETED'
        arc_application.save()

        redirect_address = build_url(self.REDIRECT_NAME, get={'id': application_id})

        return HttpResponseRedirect(redirect_address)

    def create_context(self, application_id):
        """
        Creates the context dictionary for this view.
        :param application_id: Reviewed application's id.
        :return: Context dictionary.
        """

        # Get nanny information
        nanny_actions = NannyGatewayActions()
        insurance_cover_dict = nanny_actions.read('insurance-cover',
                                                  params={'application_id': application_id}).record

        insurance_bool = insurance_cover_dict['public_liability']

        # Set up context
        context = {
            'application_id': application_id,
            'title': 'Review: Insurance cover',
            # 'form': '',
            'rows': [
                {
                    'id': 'insurance_bool',
                    'name': 'Do you have public liability insurance?',
                    'info': insurance_bool
                }
            ]
        }

        return context