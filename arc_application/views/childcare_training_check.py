from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View

from ..forms.form import EYFSTrainingCheckForm, TypeOfChildcareTrainingCheckForm
from ..models import Application, Arc, ChildcareTraining, ChildcareType
from ..review_util import redirect_selection, request_to_comment, save_comments
from ..decorators import group_required, user_assigned_application


decorators = [login_required, group_required(settings.ARC_GROUP), user_assigned_application]


@method_decorator(decorators, name='dispatch')
class ChildcareTrainingCheckSummaryView(View):
    table_name = 'ChildcareTraining'

    def get(self, request):
        application_id_local = request.GET["id"]
        eyfs_id = ChildcareTraining.objects.get(application_id=application_id_local).eyfs_id

        # If the applicant applied for the EYFS register, check EYFS training details.
        # If they're applying to the Childcare Register only, check that they have at least common core training.
        if ChildcareType.objects.get(application_id=application_id_local).zero_to_five:
            childcare_register_only = False
            form = EYFSTrainingCheckForm(table_keys=[eyfs_id])
        else:
            childcare_register_only = True
            form = TypeOfChildcareTrainingCheckForm(table_keys=[eyfs_id])

        return self.render_summary_with_context(request, form=form, app_id_local=application_id_local, childcare_register_only=childcare_register_only)

    def post(self, request):
        application_id_local = request.POST["id"]
        eyfs_id = ChildcareTraining.objects.get(application_id=application_id_local).eyfs_id

        if ChildcareType.objects.get(application_id=application_id_local).zero_to_five:
            childcare_register_only = False
            form = EYFSTrainingCheckForm(request.POST, table_keys=[eyfs_id])
        else:
            childcare_register_only = True
            form = TypeOfChildcareTrainingCheckForm(request.POST, table_keys=[eyfs_id])

        if form.is_valid():
            comment_list = request_to_comment(eyfs_id, self.table_name, form.cleaned_data)
            save_successful = save_comments(request, comment_list)
            application = Application.objects.get(pk=application_id_local)

            if not comment_list:
                section_status = 'COMPLETED'
                application.childcare_training_arc_flagged = False
            else:
                section_status = 'FLAGGED'
                application.childcare_training_arc_flagged = True
                application.childcare_training_status = section_status

            application.save()

            if save_successful:
                status = Arc.objects.get(pk=application_id_local)
                status.childcare_training_review = section_status
                status.save()
                childcare_type = ChildcareType.objects.get(application_id=application_id_local)
                default = '/health/check-answers' if childcare_type.zero_to_five else '/dbs-check/summary'
                redirect_link = redirect_selection(request, default)
                return HttpResponseRedirect(settings.URL_PREFIX + redirect_link + '?id=' + application_id_local)
            else:
                return render(request, '500.html')

        else:
            form.error_summary_title = 'There was a problem'

            return self.render_summary_with_context(request, form=form, app_id_local=application_id_local,
                                                    childcare_register_only=childcare_register_only)

    def render_summary_with_context(self, request, form, app_id_local, childcare_register_only):
        eyfs_check = ChildcareTraining.objects.get(application_id=app_id_local)
        context = {
            'form': form,
            'application_id': app_id_local,
            'childcare_register_only': childcare_register_only
            }

        if childcare_register_only:
            eyfs_training = eyfs_check.eyfs_training
            common_core_training = eyfs_check.common_core_training
            if eyfs_training and common_core_training:
                context['childcare_training'] = 'Childcare qualification (level 2 or higher) and training in common core skills'
            elif eyfs_training:
                context['childcare_training'] = 'Childcare qualification (level 2 or higher)'
            elif common_core_training:
                context['childcare_training'] = 'Training in common core skills'
            else:
                context['childcare_training'] = 'None'
        else:
            context['eyfs_course_title'] = eyfs_check.eyfs_course_name
            context['eyfs_course_date_day'] = eyfs_check.eyfs_course_date_day
            context['eyfs_course_date_month'] = eyfs_check.eyfs_course_date_month
            context['eyfs_course_date_year'] = eyfs_check.eyfs_course_date_year

        return render(request, 'childcare-training-summary.html', context=context)

