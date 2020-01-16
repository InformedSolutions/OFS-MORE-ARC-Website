import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import FormView

from ...forms.update_detail_forms.update_contact_details import NannyUpdateEmail, NannyUpdatePhoneNumber
from ...review_util import build_url
from ...services.db_gateways import IdentityGatewayActions, HMGatewayActions
from ...views.base import has_group

# Initiate logging
log = logging.getLogger()


@method_decorator(login_required, name='dispatch')
class HMChangeDetails(FormView):
    form_class = None
    page_title = None
    pre_text = ''
    post_text = ''
    alt_text = ''
    field = ('email', 'mobile_number', 'add_phone_number')
    template_name = 'update_details/update_field.html'

    def get_context_data(self, **kwargs):
        app_id = get_token_id_from_request(self.request)

        context = {
            'application_id': app_id,
            'page_title': self.page_title,
            'pre_text': self.pre_text,
            'post_text': self.post_text,
            'submit_alt_text': self.alt_text,
            'cc_user': has_group(self.request.user, settings.CONTACT_CENTRE)
        }

        return super().get_context_data(**context)

    def get_initial(self):
        app_id = get_token_id_from_request(self.request)
        identity_actions = IdentityGatewayActions()

        user_record = identity_actions.read('user', params={'application_id': app_id}).record

        return {self.field: user_record[self.field]}

    def form_valid(self, form):
        app_id = get_token_id_from_request(self.request)
        identity_actions = IdentityGatewayActions()

        updates = {'application_id': app_id,
                   self.field: form.cleaned_data[self.field]}
        patch_response = identity_actions.patch('user', updates)
        log.debug("Handling submissions for nanny change details page")
        return super().form_valid(form)

    def get_success_url(self):
        app_id = self.request.GET.get('id')
        return build_url('search_summary', get={'id': app_id, 'app_type': 'Association'})


class HMUpdateEmailView(HMChangeDetails):
    field = HMChangeDetails.field[0]
    form_class = NannyUpdateEmail
    page_title = "Update the applicant's email"


class HMUpdatePhoneNumberView(HMChangeDetails):
    field = HMChangeDetails.field[1]
    form_class = NannyUpdatePhoneNumber
    page_title = "Update the applicant's mobile phone number"


def get_token_id_from_request(request):
    """
    method to get the token id associated with the adult
    :param request: the request
    :return: the token id associated with the adult
    """
    adult_id = request.GET.get('id')
    adult_record = HMGatewayActions().read('adult', params={'adult_id': adult_id}).record
    token_id = adult_record['token_id']

    return token_id
