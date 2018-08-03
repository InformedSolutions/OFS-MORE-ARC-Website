from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from arc_application.decorators import group_required, user_assigned_application

from arc_application.db_gateways import NannyGatewayActions
from arc_application.models import Arc
from arc_application.views.nanny_views.nanny_view_helpers import parse_date_of_birth


@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
#@user_assigned_application
#@group_required(settings.ARC_GROUP)
class NannyTaskList(View):
    TEMPLATE_NAME = 'nanny_task_list.html'
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
            'all_complete': self.nanny_all_complete(application_id, False)
        }

        return context

    def nanny_all_complete(self, id, flag):
        """
        Check the status of all sections
        :param id: Application Id
        :return: True or False depending on whether all sections have been reviewed
        """

        # TODO: Redo this function.

        if Arc.objects.filter(application_id=id):
            arc = Arc.objects.get(application_id=id)
            list = [arc.login_details_review,
                    arc.personal_details_review,
                    arc.childcare_address_review,
                    arc.first_aid_review,
                    arc.childcare_training_review,
                    arc.dbs_review,
                    arc.insurance_cover_review,
                    ]

            for i in list:
                if (i == 'NOT_STARTED' and not flag) or (i != 'COMPLETED' and flag):
                    return False

            return True

        else:
            return False

        return context

    def get_review_count(self, nanny_application, arc_application):

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