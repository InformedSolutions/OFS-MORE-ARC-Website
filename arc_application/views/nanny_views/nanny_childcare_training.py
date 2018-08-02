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
class NannyChildcareTrainingSummary(View):
    TEMPLATE_NAME = 'nanny_childcare_training_summary.html'
    FORM_NAME = ''
    # TODO -o Fix to allow use of reverse_lazy
    REDIRECT_LINK = '/nanny/dbs' #reverse_lazy('nanny_childcare_address_summary')

    def get(self, request):

        # Get application ID
        application_id = request.GET["id"]

        context = self.create_context(application_id)

        return render(request, self.TEMPLATE_NAME, context=context)

    def post(self, request):
        # TODO -o childcare_training post

        # Get application ID
        application_id = request.POST["id"]

        # # Update task status to FLAGGED
        # arc_application = Arc.objects.get(application_id=application_id)
        # arc_application.childcare_training_review = 'FLAGGED'
        # arc_application.save()

        # Update task status to COMPLETED
        arc_application = Arc.objects.get(application_id=application_id)
        arc_application.childcare_training_review = 'COMPLETED'
        arc_application.save()

        redirect_address = settings.URL_PREFIX + self.REDIRECT_LINK + '?id=' + application_id

        return HttpResponseRedirect(redirect_address)

    def create_context(self, application_id):
        '''

        :return: Context for the form
        '''

        # Get nanny information
        nanny_actions = NannyGatewayActions()
        childcare_training_dict = nanny_actions.read('childcare-training',
                                                     params={'application_id': application_id}).record

        qualification_bool = childcare_training_dict['level_2_training']
        core_training_bool = childcare_training_dict['common_core_training']

        # Set up context
        context = {
            # 'form': '',
            'application_id': application_id,
            'qualification_bool': qualification_bool,
            'core_training_bool': core_training_bool
        }

        return context