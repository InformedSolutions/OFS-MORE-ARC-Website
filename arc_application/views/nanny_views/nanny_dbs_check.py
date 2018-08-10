from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.utils.decorators import method_decorator

from arc_application.services.db_gateways import NannyGatewayActions
from arc_application.forms.nanny_forms.nanny_form_builder import dbs_form
from arc_application.models import Arc
from arc_application.review_util import build_url


@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class NannyDbsCheckSummary(View):
    TEMPLATE_NAME = 'nanny_general_template.html'
    FORM_NAME = ''
    REDIRECT_NAME = 'nanny_insurance_cover_summary'

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
        arc_application.dbs_review = 'COMPLETED'
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
        dbs_check_dict = nanny_actions.read('dbs-check',
                                            params={'application_id': application_id}).record

        dbs_certificate_number = dbs_check_dict['dbs_number']
        criminal_bool = dbs_check_dict['convictions']

        # Set up context
        context = {
            'application_id': application_id,
            'title': 'Review: Criminal record (DBS) check',
            'form': dbs_form,
            'rows': [
                {
                    'id': 'dbs_number',
                    'name': 'DBS certificate number',
                    'info': dbs_certificate_number,
                    'declare': dbs_form['dbs_number_declare'],
                    'comments': dbs_form['dbs_number_comments'],
                },
                {
                    'id': 'convictions',
                    'name': 'Do you have any criminal cautions or convictions?',
                    'info': criminal_bool,
                    'declare': dbs_form['convictions_declare'],
                    'comments': dbs_form['convictions_comments'],
                }
            ]
        }

        return context