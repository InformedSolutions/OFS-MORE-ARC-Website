from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.utils.decorators import method_decorator

from arc_application.services.db_gateways import NannyGatewayActions
from arc_application.models import Arc
from arc_application.review_util import build_url
from arc_application.forms.nanny_forms.nanny_first_aid_training_form import FirstAidTrainingForm


@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class NannyFirstAidTrainingSummary(View):
    TEMPLATE_NAME = 'nanny_general_template.html'
    FORM = FirstAidTrainingForm
    REDIRECT_NAME = 'nanny_childcare_training_summary'

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
        arc_application.first_aid_review = 'COMPLETED'
        arc_application.save()

        redirect_address = build_url(self.REDIRECT_NAME, get={'id': application_id})

        return HttpResponseRedirect(redirect_address)

    def create_context(self, application_id):
        """
        Creates the context dictionary for this view.
        :param application_id: Reviewed application's id.
        :return: Context dictionary.
        """

        #Setup form
        #form = self.FORM() # table_keys=[first_aid_id]

        # Get nanny information
        nanny_actions = NannyGatewayActions()
        first_aid_dict = nanny_actions.read('first-aid',
                                            params={'application_id': application_id}).record

        training_organisation = first_aid_dict['training_organisation']
        training_course_title = first_aid_dict['course_title']
        date_course_completed = first_aid_dict['course_date']

        # Set up context
        context = {
            'application_id': application_id,
            'title': 'Review: First aid training',
            #'form': form,
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