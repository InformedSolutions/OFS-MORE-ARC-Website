from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views import View
from django.utils.decorators import method_decorator

from arc_application.models import Arc
from arc_application.views.nanny_views.nanny_view_helpers import nanny_all_completed


@method_decorator(login_required, name='get')
class NannyArcSummaryConfirmation(View):
    TEMPLATE_NAMES = ('review-confirmation.html', 'review-sent-back.html')
    FORM_NAME = ''

    def get(self, request):

        # Get application ID
        application_id = request.GET["id"]

        # Choose which template to display
        template = self.get_template(application_id)

        # Render chosen template
        return render(request, template)

    def get_template(self, application_id):

        # Get applications
        arc_application = Arc.objects.get(application_id=application_id)

        # Get possible templates
        confirmation, sent_back = self.TEMPLATE_NAMES

        # If all sections are marked 'COMPLETED'
        if nanny_all_completed(arc_application):
            return confirmation
        else:
            return sent_back
