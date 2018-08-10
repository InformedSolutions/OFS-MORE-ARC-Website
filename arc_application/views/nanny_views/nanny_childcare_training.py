from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.utils.decorators import method_decorator

from arc_application.services.db_gateways import NannyGatewayActions
from arc_application.models import Arc
from arc_application.review_util import build_url
from arc_application.forms.nanny_forms.nanny_form_builder import childcare_training_form



@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class NannyChildcareTrainingSummary(View):
    TEMPLATE_NAME = 'nanny_general_template.html'
    FORM_NAME = ''
    REDIRECT_NAME = 'nanny_dbs_summary'

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
        arc_application.childcare_training_review = 'COMPLETED'
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
        childcare_training_dict = nanny_actions.read('childcare-training',
                                                     params={'application_id': application_id}).record

        level_2_training = childcare_training_dict['level_2_training']
        common_core_training = childcare_training_dict['common_core_training']

        # Set up context
        context = {
            'application_id': application_id,
            'title': 'Review: Childcare training',
            'form': childcare_training_form,
            'rows': [
                {
                    'id': 'level_2_training',
                    'name': 'Do you have a childcare qualification?',
                    'info': level_2_training,
                    'declare': childcare_training_form['level_2_training_declare'],
                    'comments': childcare_training_form['level_2_training_comments'],
                },
                {
                    'id': 'common_core_training',
                    'name': 'Have you had common core training?',
                    'info': common_core_training,
                    'declare': childcare_training_form['common_core_training_declare'],
                    'comments': childcare_training_form['common_core_training_comments'],
                }
            ]

        }

        return context