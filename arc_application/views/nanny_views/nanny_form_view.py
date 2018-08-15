from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import FormView
from django.views.decorators.cache import never_cache

from ...review_util import build_url
from ...services.arc_comments_handler import save_arc_comments_from_request, \
    update_arc_review_status, get_form_initial_values, update_application_arc_flagged_status


@method_decorator(never_cache, name='dispatch')
@method_decorator(login_required, name='dispatch')
class NannyARCFormView(FormView):
    """
    Parent FormView class from which all subsequent FormViews will inherit.
    """
    template_name = None
    success_url = None
    task_for_review = None
    application_id = None

    def get(self, request, *args, **kwargs):
        self.application_id = request.GET['id']
        context = self.get_context_data(self.application_id)
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        self.application_id = request.GET['id']

        if isinstance(self.form_class, list):
            for form in self.form_class:
                self.handle_post_data(form)
        else:
            self.handle_post_data(self.form_class)

        return HttpResponseRedirect(build_url(self.success_url, get={'id': self.application_id}))

    def handle_post_data(self, form):
        # Write ArcComments to db from form.
        endpoint = form.api_endpoint_name
        table_pk = form.pk_field_name
        flagged_fields = save_arc_comments_from_request(request=self.request, endpoint=endpoint, table_pk=table_pk)

        # Update {{task}}_review status for ARC user.
        reviewed_task = self.get_task_for_review()
        update_arc_review_status(self.application_id, flagged_fields, reviewed_task=reviewed_task)

        # Update {{task}}_arc_flagged status for NannyApplication table.
        update_application_arc_flagged_status(flagged_fields, self.application_id, reviewed_task)

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        form = form_class()
        return get_form_initial_values(form, application_id=self.application_id)

    def get_forms(self):
        return [self.get_form(form_class=form_class) for form_class in self.form_class]

    def get_context_data(self, *args, **kwargs):
        raise NotImplementedError('You must set the context_data and pk for this FormView with the record from the db.')

    def get_task_for_review(self):
        if self.task_for_review is None:
            raise NotImplementedError('You must supply the name of the task being reviewed.')
        else:
            return self.task_for_review
