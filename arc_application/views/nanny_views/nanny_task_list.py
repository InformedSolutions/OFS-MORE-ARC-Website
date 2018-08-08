from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views import View
from django.utils.decorators import method_decorator

from arc_application.services.db_gateways import NannyGatewayActions
from arc_application.models import Arc
from arc_application.views.nanny_views.nanny_view_helpers import parse_date_of_birth, \
    nanny_all_reviewed


@method_decorator(login_required, name='get')
class NannyTaskList(View):
    TEMPLATE_NAME = 'nanny_task_list.html'
    FORM_NAME = ''

    def get(self, request):

        # Get application ID
        application_id = request.GET["id"]

        context = self.create_context(application_id)

        return render(request, self.TEMPLATE_NAME, context=context)

    def create_context(self, application_id):
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
        birth_dict = parse_date_of_birth(dob_str)

        # Set up context
        context = {
            # 'form':'',
            'application_id': application_id,
            'application_reference': application_reference,
            'first_name': first_name,
            'middle_names': middle_names,
            'last_name': last_name,
            'review_count': review_count,
            'login_details_status': arc_application.login_details_review,
            'personal_details_status': arc_application.personal_details_review,
            'childcare_address_status': arc_application.childcare_address_review,
            'first_aid_status': arc_application.first_aid_review,
            'childcare_training_status': arc_application.childcare_training_review,
            'dbs_status': arc_application.dbs_review,
            'insurance_cover_status': arc_application.insurance_cover_review,
            'birth_day': int(birth_dict['birth_day']),
            'birth_month': int(birth_dict['birth_month']),
            'birth_year': int(birth_dict['birth_year']),
            'all_complete': nanny_all_reviewed(arc_application)
        }

        return context

    def get_review_count(self, nanny_application, arc_application):
        """
        :param nanny_application: The nanny_application record
        :param arc_application: The arc_application record
        :return: The number of reviewed tasks
        """

        review_fields_to_check = (
            'login_details_review',
            'personal_details_review',
            'childcare_address_review',
            'first_aid_review',
            'childcare_training_review',
            'dbs_review',
            'insurance_cover_review'
        )

        flagged_fields_to_check = (
            'login_details_arc_flagged',
            'personal_details_arc_flagged',
            'childcare_address_arc_flagged',
            'first_aid_training_arc_flagged',
            'childcare_training_arc_flagged',
            'criminal_record_check_arc_flagged',
            'insurance_cover_arc_flagged'
        )

        review_count = sum([1 for field in review_fields_to_check if getattr(arc_application, field) == 'COMPLETED'])
        review_count += sum([1 for field in flagged_fields_to_check if nanny_application[field]])

        return review_count
