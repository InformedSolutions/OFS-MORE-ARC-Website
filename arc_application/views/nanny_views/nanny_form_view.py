import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import FormView
from django.views.decorators.cache import never_cache

from ...models import Arc
from ...review_util import build_url
from ...services.arc_comments_handler import update_arc_review_status, \
    get_form_initial_values, \
    update_application_arc_flagged_status, \
    ARCCommentsProcessor
from ...services.db_gateways import NannyGatewayActions
from ...decorators import group_required, user_assigned_application

# Initiate logging
log = logging.getLogger()


@method_decorator(never_cache, name='dispatch')
@method_decorator(login_required, name='dispatch')
@method_decorator(user_assigned_application, name='dispatch')
@method_decorator(group_required(settings.ARC_GROUP), name='dispatch')
class NannyARCFormView(FormView):
    """
    Parent FormView class from which all subsequent FormViews will inherit.
    """
    template_name     = None
    success_url       = None
    task_for_review   = None
    application_id    = None
    verbose_task_name = None

    def get(self, request, *args, **kwargs):
        self.application_id = request.GET['id']
        context = self.get_context_data(self.application_id)
        page_name = self.verbose_task_name
        log.debug("Rendering nanny %s page" % page_name)
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        self.application_id = request.GET['id']
        self.__handle_post_data()
        page_name = self.verbose_task_name
        log.debug("Handling submissions for nanny %s page" % page_name)
        return HttpResponseRedirect(build_url(self.get_success_url(), get={'id': request.GET['id']}))

    def __handle_post_data(self):
        # Cast self.form_class to a list if not already a list. Then iterate over list.
        form_class = self.get_form_class()
        _form_classes = [form_class] if not isinstance(form_class, list) else form_class

        flagged_fields = any([ARCCommentsProcessor.process_comments(
            request=self.request,
            form_class=_class,
            verbose_task_name=self.verbose_task_name
        ) for _class in _form_classes])

        # Update {{task}}_review status for ARC user.
        reviewed_task = self.get_task_for_review()
        update_arc_review_status(self.application_id, flagged_fields, reviewed_task=reviewed_task)

        # If a personal details review check whether linking complete
        if reviewed_task == 'personal_details_review':
            self.update_linking_review_status(self.application_id, reviewed_task)

        # Update {{task}}_arc_flagged status for NannyApplication table.
        update_application_arc_flagged_status(flagged_fields, self.application_id, reviewed_task)

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        initial = get_form_initial_values(form_class, application_id=self.application_id)
        return form_class(initial=initial)

    def get_forms(self):
        return [self.get_form(form_class=form_class) for form_class in self.get_form_class()]

    def get_context_data(self, *args, **kwargs):
        raise NotImplementedError('You must set the context_data and pk for this FormView with the record from the db.')

    def get_task_for_review(self):
        if self.task_for_review is None:
            raise NotImplementedError('You must supply the name of the task being reviewed.')
        else:
            return self.task_for_review

    def update_linking_review_status(self, application_id, reviewed_task):
        linking_complete = False

        # Get data to find out if an individual_id is saved
        api_response = NannyGatewayActions().read('previous-registration-details',
                                                  params={'application_id': application_id})

        if api_response.status_code == 200:
            previous_registration_record = api_response.record
            individual_id = previous_registration_record['individual_id']
            if individual_id is not None:
                linking_complete = True

        # If not saved, then linking incomplete - further update to review status
        if not linking_complete:
            arc_application = Arc.objects.get(application_id=application_id)
            setattr(arc_application, reviewed_task, 'IN PROGRESS')
            arc_application.save()
