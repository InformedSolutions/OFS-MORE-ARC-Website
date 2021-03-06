import logging
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View

from ...models import Arc
from ...services.db_gateways import NannyGatewayActions
from ...services.nanny_view_helpers import parse_date_of_birth, \
    nanny_all_reviewed

# Initiate logging
log = logging.getLogger()

@method_decorator(login_required, name='get')
class NannyTaskList(View):
    TEMPLATE_NAME = 'nanny_task_list.html'
    FORM_NAME = ''

    def get(self, request):
        # Get application ID
        application_id = request.GET["id"]

        context = self.create_context(application_id, request)
        log.debug("Rendering nanny task list")
        return render(request, self.TEMPLATE_NAME, context=context)

    def create_context(self, application_id, request):
        """
        Creates the context dictionary for this view.
        :param application_id: Reviewed application's id.
        :return: Context dictionary.
        """

        # Get nanny information
        nanny_actions = NannyGatewayActions()
        nanny_application_dict = nanny_actions.read('application',
                                                    params={'application_id': application_id}).record
        personal_details_dict = nanny_actions.read('applicant-personal-details',
                                                   params={'application_id': application_id}).record

        arc_application = Arc.objects.get(application_id=application_id)

        application_reference = nanny_application_dict['application_reference']
        first_name = personal_details_dict['first_name']
        middle_names = personal_details_dict['middle_names']
        last_name = personal_details_dict['last_name']
        review_count = self.get_review_count(nanny_application_dict, arc_application)

        dob_str = personal_details_dict['date_of_birth']
        birth_list = parse_date_of_birth(dob_str)

        # Set up context
        context = {
            # 'form':'',
            'application_id': application_id,
            'application_reference': application_reference,
            'first_name': first_name,
            'middle_names': middle_names,
            'last_name': last_name,
            'review_count': review_count,
            'number_of_tasks': self.number_of_tasks(),
            'login_details_status': arc_application.login_details_review,
            'personal_details_status': arc_application.personal_details_review,
            'your_children_status': arc_application.your_children_review,
            'childcare_address_status': arc_application.childcare_address_review,
            'first_aid_status': arc_application.first_aid_review,
            'childcare_training_status': arc_application.childcare_training_review,
            'dbs_status': arc_application.dbs_review,
            'insurance_cover_status': arc_application.insurance_cover_review,
            'birth_day': int(birth_list[2]),
            'birth_month': int(birth_list[1]),
            'birth_year': int(birth_list[0]),
            'all_complete': nanny_all_reviewed(arc_application, application_id),
        }

        return context

    @staticmethod
    def get_review_count(nanny_application, arc_application):
        """
        :param nanny_application: The nanny_application record
        :param arc_application: The arc_application record
        :return: The number of reviewed tasks
        """

        review_fields_to_check = [
            'login_details_review',
            'personal_details_review',
            'childcare_address_review',
            'first_aid_review',
            'childcare_training_review',
            'dbs_review',
            'insurance_cover_review'
        ]

        flagged_fields_to_check = [
            'login_details_arc_flagged',
            'personal_details_arc_flagged',
            'childcare_address_arc_flagged',
            'first_aid_arc_flagged',
            'childcare_training_arc_flagged',
            'dbs_arc_flagged',
            'insurance_cover_arc_flagged'
        ]

        review_count = sum([1 for field in review_fields_to_check if getattr(arc_application, field) == 'COMPLETED'])
        review_count += sum([1 for field in flagged_fields_to_check if nanny_application[field]])

        return review_count

    @staticmethod
    def number_of_tasks():
        # TODO: Rethink purpose of this function
        return 7
