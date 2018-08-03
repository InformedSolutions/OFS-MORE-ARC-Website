"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- urls.py --

@author: Informed Solutions
"""
import re

from arc_application.views.base import assign_new_application, custom_login, error_403, error_404, error_500, release, \
    summary_page, AuditlogListView
from arc_application.views.arc_user_summary import ARCUserSummaryView
from arc_application.contact_centre import search

# Childminder Views

from arc_application.views.childminder_views.contact_details import contact_summary
from arc_application.views.childminder_views.dbs_check import dbs_check_summary
from arc_application.views.childminder_views.eyfs_check import EFYSCheckSummaryView
from arc_application.views.childminder_views.first_aid_training import first_aid_training_summary
from arc_application.views.childminder_views.health_declaration_booklet import health_check_answers
from arc_application.views.childminder_views.other_people_addresses import address_state_dispatcher
from arc_application.views.childminder_views.other_people_in_home import other_people_summary, add_previous_name
from arc_application.views.childminder_views.personal_details import personal_details_summary, add_applicant_previous_name
from arc_application.views.childminder_views.references import references_summary
from arc_application.views.childminder_views import review, task_list, PreviousRegistrationDetailsView, OtherPersonPreviousRegistrationDetailsView
from arc_application.views.childminder_views.type_of_childcare import type_of_childcare_age_groups
from arc_application.views.childminder_views.arc_summary import cc_summary, arc_summary
from arc_application.views.contact_centre.change_details import UpdateEmailView, UpdatePhoneNumberView, \
    UpdateAddPhoneNumberView

# Nanny Views

from arc_application.views.nanny_views.nanny_review import NannyTaskList
from arc_application.views.nanny_views.nanny_contact_details import NannyContactDetailsSummary
from arc_application.views.nanny_views.nanny_personal_details import NannyPersonalDetailsSummary
from arc_application.views.nanny_views.nanny_childcare_address import NannyChildcareAddressSummary
from arc_application.views.nanny_views.nanny_first_aid import NannyFirstAidTrainingSummary
from arc_application.views.nanny_views.nanny_childcare_training import NannyChildcareTrainingSummary
from arc_application.views.nanny_views.nanny_dbs_check import NannyDbsCheckSummary
from arc_application.views.nanny_views.nanny_insurance_cover import NannyInsuranceCoverSummary
from arc_application.views.nanny_views.nanny_arc_summary import NannyArcSummary

from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import logout

from arc_application.views.childminder_views.personal_details_addresses import personal_details_previous_address

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^release/(?P<application_id>[\w\- ]+)', release, name='release'),
    url(r'^accounts/profile/', assign_new_application, name='new_application'),
    url(r'^login/', custom_login, name='login'),
    url(r'^logout/', logout, {'next_page': settings.URL_PREFIX + '/login/'}),
    url(r'^summary/', ARCUserSummaryView.as_view(), name='summary'),
    url(r'^review/', task_list, name='task_list'),
    url(r'^account/summary/', contact_summary, name='contact_summary'),
    url(r'^childcare/age-groups/', type_of_childcare_age_groups, name='type_of_childcare_age_groups'),
    url(r'^personal-details/summary/', personal_details_summary, name='personal_details_summary'),
    url(r'^personal-details/previous-names/', add_applicant_previous_name, name='personal_details_previous_names'),
    url(r'^personal-details/previous-addresses', personal_details_previous_address,
        name='personal_details_previous_addresses'),
    url(r'^first-aid/summary/', first_aid_training_summary, name='first_aid_training_summary'),
    url(r'^dbs-check/summary/', dbs_check_summary, name='dbs_check_summary'),
    url(r'^eyfs-check/summary/', EFYSCheckSummaryView.as_view(), name='eyfs_check_summary'),
    url(r'^references/summary/', references_summary, name='references_summary'),
    url(r'^people/summary/', other_people_summary, name='other_people_summary'),
    url(r'^people/previous-names', add_previous_name, name='other-people-previous-names'),
    url(r'^people/previous-addresses', address_state_dispatcher, name='other-people-previous-addresses'),
    url(r'^people/previous-registration$', OtherPersonPreviousRegistrationDetailsView.as_view(), name='other-people-previous-registration'),
    url(r'^health/check-answers/', health_check_answers, name='health_check_answers'),
    url(r'^confirmation/', review, name='review'),
    url(r'^arc-summary/', arc_summary, name='arc-summary'),
    url(r'^auditlog/', login_required(AuditlogListView.as_view()), name='auditlog'),
    url(r'^search/', search, name='search'),
    url(r'^search-summary/', cc_summary, name='search_summary'),
    url(r'^contact-centre/contact-details/email-address', UpdateEmailView.as_view(), name='update_email'),
    url(r'^contact-centre/contact-details/phone-number', UpdatePhoneNumberView.as_view(), name='update_phone_number'),
    url(r'^contact-centre/contact-details/add-phone-number', UpdateAddPhoneNumberView.as_view(),
        name='update_add_number'),
    url(r'^personal-details/previous-registration', PreviousRegistrationDetailsView.as_view(),
        name='previous_registration_details'),
    url(r'^nanny/review', NannyTaskList.as_view(), name='nanny_task_list'),
    url(r'^nanny/contact-details', NannyContactDetailsSummary.as_view(), name='nanny_contact_summary'),
    url(r'^nanny/personal-details', NannyPersonalDetailsSummary.as_view(), name='nanny_personal_details_summary'),
    url(r'^nanny/childcare-address', NannyChildcareAddressSummary.as_view(), name='nanny_childcare_address_summary'),
    url(r'^nanny/first-aid-training', NannyFirstAidTrainingSummary.as_view(), name='nanny_first_aid_training_summary'),
    url(r'^nanny/childcare-training', NannyChildcareTrainingSummary.as_view(), name='nanny_childcare_training_summary'),
    url(r'^nanny/dbs', NannyDbsCheckSummary.as_view(), name='nanny_dbs_summary'),
    url(r'^nanny/insurance-cover', NannyInsuranceCoverSummary.as_view(), name='nanny_insurance_cover_summary'),
    url(r'^nanny/arc-summary', NannyArcSummary.as_view(), name='nanny_arc_summary'),
]

if settings.URL_PREFIX:
    prefixed_url_pattern = []
    for pat in urlpatterns:
        pat.regex = re.compile(r"^%s/%s" % (settings.URL_PREFIX[1:], pat.regex.pattern[1:]))
        prefixed_url_pattern.append(pat)
    urlpatterns = prefixed_url_pattern

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
                      url(r'^__debug__/', include(debug_toolbar.urls)),
                  ] + urlpatterns

handler403 = error_403
handler404 = error_404
handler500 = error_500
