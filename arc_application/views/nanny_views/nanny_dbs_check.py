from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy

from arc_application.db_gateways import IdentityGatewayActions, NannyGatewayActions
from arc_application.views.nanny_views.nanny_view_helpers import parse_date_of_birth
from arc_application.models import Arc


@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class NannyDbsCheckSummary(View):
    TEMPLATE_NAME = 'nanny_general_template.html'
    FORM_NAME = ''
    # TODO -o Fix to allow use of reverse_lazy
    REDIRECT_LINK = '/nanny/insurance-cover' #reverse_lazy('nanny_childcare_address_summary')

    def get(self, request):

        # Get application ID
        application_id = request.GET["id"]

        context = self.create_context(application_id)

        return render(request, self.TEMPLATE_NAME, context=context)

    def post(self, request):
        # TODO -o dbs_check post

        # Get application ID
        application_id = request.POST["id"]

        # # Update task status to FLAGGED
        # arc_application = Arc.objects.get(application_id=application_id)
        # arc_application.dbs_review = 'FLAGGED'
        # arc_application.save()

        # Update task status to COMPLETED
        arc_application = Arc.objects.get(application_id=application_id)
        arc_application.dbs_review = 'COMPLETED'
        arc_application.save()

        redirect_address = settings.URL_PREFIX + self.REDIRECT_LINK + '?id=' + application_id

        return HttpResponseRedirect(redirect_address)

    def create_context(self, application_id):
        '''

        :return: Context for the form
        '''

        # Get nanny information
        nanny_actions = NannyGatewayActions()
        dbs_check_dict = nanny_actions.read('dbs-check',
                                            params={'application_id': application_id}).record

        dbs_certificate_number = dbs_check_dict['dbs_number']
        criminal_bool = dbs_check_dict['convictions']

        # Set up context
        context = {
            'application_id': application_id,
            'title': 'Review: Childcare training',
            # 'form': '',
            'rows': [
                {
                    'id': 'dbs_certificate_number',
                    'name': 'DBS certificate number',
                    'info': dbs_certificate_number
                },
                {
                    'id': 'criminal_bool',
                    'name': 'Do you have any criminal cautions or convictions?',
                    'info': criminal_bool
                }
            ]

        }

        return context