from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View

from ..forms.form import EYFSCheckForm
from ..models import Application, Arc, EYFS
from ..review_util import redirect_selection, request_to_comment, save_comments


class EFYSCheckSummaryView(View):
    table_name = 'EYFS'

    def get(self, request):
        application_id_local = request.GET["id"]
        eyfs_id = EYFS.objects.get(application_id=application_id_local).eyfs_id
        form = EYFSCheckForm(table_keys=[eyfs_id])

        return self.render_summary_with_context(request, form=form, app_id_local=application_id_local)

    def post(self, request):
        application_id_local = request.POST["id"]
        eyfs_id = EYFS.objects.get(application_id=application_id_local).eyfs_id
        form = EYFSCheckForm(request.POST, table_keys=[eyfs_id])

        if form.is_valid():
            comment_list = request_to_comment(request, eyfs_id, self.table_name, form.cleaned_data)
            save_successful = save_comments(comment_list)

            if not comment_list:
                section_status = 'COMPLETED'
            else:
                section_status = 'FLAGGED'

            if save_successful:
                status = Arc.objects.get(pk=application_id_local)
                status.eyfs_review = section_status
                status.save()
                default = '/health/check-answers'
                redirect_link = redirect_selection(request, default)
                return HttpResponseRedirect(settings.URL_PREFIX + redirect_link + '?id=' + application_id_local)
            else:
                return render(request, '500.html')

        else:
            return self.render_summary_with_context(request, form=form, app_id_local=application_id_local)

    def render_summary_with_context(self, request, form, app_id_local):
        eyfs_check = EYFS.objects.get(application_id=app_id_local)
        context = {
        'form': form,
        'application_id': app_id_local,
        'eyfs_course_title': eyfs_check.eyfs_course_name,
        'eyfs_course_date_day': eyfs_check.eyfs_course_date_day,
        'eyfs_course_date_month': eyfs_check.eyfs_course_date_month,
        'eyfs_course_date_year': eyfs_check.eyfs_course_date_year
        }
        return render(request, 'eyfs-summary.html', context=context)
