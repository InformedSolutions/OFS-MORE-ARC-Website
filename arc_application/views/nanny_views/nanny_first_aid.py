from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy

from arc_application.db_gateways import IdentityGatewayActions, NannyGatewayActions
from arc_application.views.nanny_views.nanny_view_helpers import parse_date_of_birth


@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class NannyFirstAidTrainingSummary(View):
    TEMPLATE_NAME = 'nanny_first_aid_training_summary.html'
    FORM_NAME = ''
    # TODO -o Fix to allow use of reverse_lazy
    REDIRECT_LINK = '/nanny/childcare-training' #reverse_lazy('nanny_childcare_address_summary')

    def get(self, request):

        # Get application ID
        application_id = request.GET["id"]

        # Get nanny information
        nanny_actions = NannyGatewayActions()
        first_aid_dict = nanny_actions.read('first-aid',
                                                params={'application_id': application_id}).record

        training_organisation = first_aid_dict['training_organisation'] # TODO Find work_location field
        training_course_title = first_aid_dict['course_title']
        date_course_completed = first_aid_dict['course_date']

        # Set up context
        context = {
            # 'form': '',
            'application_id': application_id,
            'training_organisation': training_organisation,
            'training_course_title': training_course_title,
            'date_course_completed': date_course_completed,
        }

        return render(request, self.TEMPLATE_NAME, context=context)

    def post(self, request):
        # TODO -o childcare_address post

        # Get application ID
        application_id = request.GET["id"]

        context = {}

        redirect_address = settings.URL_PREFIX + self.REDIRECT_LINK + '?id=' + application_id

        return HttpResponseRedirect(redirect_address)