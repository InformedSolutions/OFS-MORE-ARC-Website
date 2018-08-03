from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy

from arc_application.db_gateways import IdentityGatewayActions, NannyGatewayActions
from arc_application.models import Arc


@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class NannyFirstAidTrainingSummary(View):
    TEMPLATE_NAME = 'nanny_general_template.html'
    FORM_NAME = ''
    # TODO -o Fix to allow use of reverse_lazy
    REDIRECT_LINK = '/nanny/childcare-training' #reverse_lazy('nanny_childcare_address_summary')

    def get(self, request):

        # Get application ID
        application_id = request.GET["id"]

        context = self.create_context(application_id)

        return render(request, self.TEMPLATE_NAME, context=context)

    def post(self, request):
        # TODO -o first_aid_training post

        # Get application ID
        application_id = request.POST["id"]

        # # Update task status to FLAGGED
        # arc_application = Arc.objects.get(application_id=application_id)
        # arc_application.first_aid_review = 'FLAGGED'
        # arc_application.save()

        # Update task status to COMPLETED
        arc_application = Arc.objects.get(application_id=application_id)
        arc_application.first_aid_review = 'COMPLETED'
        arc_application.save()

        redirect_address = settings.URL_PREFIX + self.REDIRECT_LINK + '?id=' + application_id

        return HttpResponseRedirect(redirect_address)

    def create_context(self, application_id):
        '''

        :return: Context for the form
        '''

        # Get nanny information
        nanny_actions = NannyGatewayActions()
        first_aid_dict = nanny_actions.read('first-aid',
                                            params={'application_id': application_id}).record

        training_organisation = first_aid_dict['training_organisation']  # TODO Find work_location field
        training_course_title = first_aid_dict['course_title']
        date_course_completed = first_aid_dict['course_date']

        # Set up context
        context = {
            'application_id': application_id,
            'title': 'Review: First aid training',
            # 'form': '',
            'rows': [
                {
                    'id': 'training_organisation',
                    'name': 'Training organisation',
                    'info': training_organisation
                },
                {
                    'id': 'training_course_title',
                    'name': 'Title of training course',
                    'info': training_course_title
                },
                {
                    'id': 'date_course_completed',
                    'name': 'Date you completed the course',
                    'info': date_course_completed
                }
            ]

        }

        return context