"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- urls.py --

@author: Informed Solutions
"""
import re

from arc_application.views.base import  custom_login, error_403, error_404, error_500, release
from arc_application.views.audit_log import audit_log_dispatcher, NannyAuditLog
from arc_application.views.arc_user_summary import ARCUserSummaryView

# Childminder Views

from arc_application.views.childminder_views.contact_details import contact_summary
from arc_application.views.childminder_views.dbs_check import dbs_check_summary
from arc_application.views.childminder_views.childcare_training_check import ChildcareTrainingCheckSummaryView
from arc_application.views.childminder_views.first_aid_training import first_aid_training_summary
from arc_application.views.childminder_views.health_declaration_booklet import health_check_answers
from arc_application.views.childminder_views.other_people_addresses import people_in_the_home_previous_address, people_in_the_home_previous_address_change
from arc_application.views.childminder_views.other_people_in_home import other_people_summary
from arc_application.views.childminder_views.previous_names import add_previous_name
from arc_application.views.childminder_views.personal_details import personal_details_summary
from arc_application.views.childminder_views.references import references_summary
from arc_application.views.childminder_views.review import review, PreviousRegistrationDetailsView, \
    OtherPersonPreviousRegistrationDetailsView
from arc_application.views.childminder_views.task_list import task_list
from arc_application.views.childminder_views.type_of_childcare import type_of_childcare_age_groups
from arc_application.views.childminder_views.arc_summary import arc_summary
from arc_application.views.contact_centre.change_details import UpdateEmailView, UpdatePhoneNumberView, \
    UpdateAddPhoneNumberView
from arc_application.contact_centre import search
from arc_application.views.contact_centre.nanny_change_details import NannyUpdateEmailView, \
    NannyUpdateAddPhoneNumberView, NannyUpdatePhoneNumberView
from arc_application.views.search_router import SearchRouter
from arc_application.views import upload_capita_dbs
from arc_application.views.applications_summary import ApplicationsSummaryView
from arc_application.views.adult_update_views.adult_update_view import new_adults_summary
from arc_application.views.adult_update_views.adult_previous_registration import adult_previous_registration_view
from arc_application.views.adult_update_views.adult_update_summary import arc_summary as adult_arc_summary
from arc_application.views.adult_update_views.confirmation import review as adult_review

# Nanny Views

from arc_application.views.nanny_views import (
    NannyTaskList, NannyContactDetailsSummary, NannyPersonalDetailsSummary, NannyPreviousRegistrationView,
    NannyChildcareAddressSummary, NannyFirstAidTrainingSummary, NannyChildcareTrainingSummary,
    NannyDbsCheckSummary, NannyInsuranceCoverSummary, NannyArcSummary, NannyArcSummaryConfirmation,
    NannyChangePreviousAddressView, NannyAddPreviousAddressSearchView, NannyAddPreviousAddressSelectView,
    NannyAddPreviousAddressManualView, nanny_add_previous_name
)

from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import logout

from arc_application.views.childminder_views.personal_details_addresses import personal_details_previous_address, personal_details_previous_address_change

urlpatterns = [

    url(r'^admin/', admin.site.urls),
    url(r'^release/(?P<application_id>[\w\- ]+)', release, name='release'),
    url(r'^login', custom_login, name='login'),
    url(r'^logout/', logout, {'next_page': settings.URL_PREFIX + '/login'}),
    url(r'^summary/', ARCUserSummaryView.as_view(), name='summary'),
    url(r'^upload-capita-dbs/$', upload_capita_dbs, name='Upload-Capita-DBS'),
    url(r'^applications-summary/$', ApplicationsSummaryView.as_view(), name='applications-summary'),

    # childminder application review
    url(r'^review/$', task_list, name='task_list'),
    url(r'^account/summary/', contact_summary, name='contact_summary'),
    url(r'^childcare/age-groups/', type_of_childcare_age_groups, name='type_of_childcare_age_groups'),
    url(r'^personal-details/summary/', personal_details_summary, name='personal_details_summary'),
    url(r'^personal-details/previous-names/', add_previous_name, name='personal_details_previous_names'),
    url(r'^personal-details/previous-addresses', personal_details_previous_address,
        name='personal_details_previous_addresses'),
    url(r'^personal-details/previous-address$', personal_details_previous_address_change, name='personal_details_previous_addresses_change'),
    url(r'^first-aid/summary/', first_aid_training_summary, name='first_aid_training_summary'),
    url(r'^dbs-check/summary/', dbs_check_summary, name='dbs_check_summary'),
    url(r'^childcare-training-check/summary/', ChildcareTrainingCheckSummaryView.as_view(),
        name='childcare_training_check_summary'),
    url(r'^references/summary/', references_summary, name='references_summary'),
    url(r'^people/summary/', other_people_summary, name='other_people_summary'),
    url(r'^people/previous-names', add_previous_name, name='other-people-previous-names'),
    url(r'^people/previous-addresses', people_in_the_home_previous_address, name='other-people-previous-addresses'),
    url(r'^people/previous-address', people_in_the_home_previous_address_change, name='other-people-previous-addresses-change'),
    url(r'^people/previous-registration$', OtherPersonPreviousRegistrationDetailsView.as_view(),
        name='other-people-previous-registration'),
    url(r'^health/check-answers/', health_check_answers, name='health_check_answers'),
    url(r'^confirmation/', review, name='review'),
    url(r'^arc-summary/', arc_summary, name='arc-summary'),

    # audit log
    url(r'^auditlog/$', login_required(audit_log_dispatcher), name='auditlog'),
    url(r'^audit-log/index', login_required(NannyAuditLog.as_view()), name='nanny-auditlog'),

    # search
    url(r'^search/', search, name='search'),
    url(r'^search-summary/', SearchRouter.as_view(), name='search_summary'),

    url(r'^contact-centre/contact-details/email-address', UpdateEmailView.as_view(), name='update_email'),
    url(r'^contact-centre/contact-details/phone-number', UpdatePhoneNumberView.as_view(), name='update_phone_number'),
    url(r'^contact-centre/contact-details/add-phone-number', UpdateAddPhoneNumberView.as_view(),
        name='update_add_number'),
    url(r'^contact-centre/nanny/contact-details/email-address', NannyUpdateEmailView.as_view(),
        name='nanny_update_email_address'),
    url(r'^contact-centre/nanny/contact-details/phone-number', NannyUpdatePhoneNumberView.as_view(),
        name='nanny_update_phone_number'),
    url(r'^contact-centre/nanny/contact-details/add-phone-number', NannyUpdateAddPhoneNumberView.as_view(),
        name='nanny_update_add_number'),
    url(r'^personal-details/previous-registration', PreviousRegistrationDetailsView.as_view(),
        name='previous_registration_details'),

    # adult update urls
    url(r'^review/new-adults', new_adults_summary,
        name='new_adults_summary'),
    url(r'^review/new-adult-summary', adult_arc_summary,
        name='new_adults'),
    url(r'^review/confirmation', adult_review,
        name='adults-confirmation'),
    url(r'^new-adult/previous-registration', adult_previous_registration_view,
        name='adults-previous-registration'),
]

# nanny application review
if settings.ENABLE_NANNIES:
    urlpatterns += [
        url(r'^nanny/review/', NannyTaskList.as_view(), name='nanny_task_list'),
        url(r'^nanny/contact-details/', NannyContactDetailsSummary.as_view(), name='nanny_contact_summary'),
        url(r'^nanny/personal-details/review/', NannyPersonalDetailsSummary.as_view(),
            name='nanny_personal_details_summary'),
        url(r'^nanny/personal-details/previous-address/', NannyChangePreviousAddressView.as_view(),
            name='nanny_change_previous_address'),
        url(r'^nanny/personal-details/previous-addresses/select/', NannyAddPreviousAddressSelectView.as_view(),
            name='nanny_add_previous_address_select'),
        url(r'^nanny/personal-details/previous-addresses/manual/', NannyAddPreviousAddressManualView.as_view(),
            name='nanny_add_previous_address_manual'),
        url(r'^nanny/personal-details/previous-addresses/', NannyAddPreviousAddressSearchView.as_view(),
            name='nanny_add_previous_address_search'),
        url(r'^nanny/personal-details/previous-registration/', NannyPreviousRegistrationView.as_view(),
            name='nanny_previous_registration'),
        url(r'^nanny/personal-details/previous-names/', nanny_add_previous_name,
            name='nanny_previous_names'),
        url(r'^nanny/childcare-address/', NannyChildcareAddressSummary.as_view(),
            name='nanny_childcare_address_summary'),
        url(r'^nanny/first-aid-training/', NannyFirstAidTrainingSummary.as_view(),
            name='nanny_first_aid_training_summary'),
        url(r'^nanny/childcare-training/', NannyChildcareTrainingSummary.as_view(),
            name='nanny_childcare_training_summary'),
        url(r'^nanny/dbs/', NannyDbsCheckSummary.as_view(), name='nanny_dbs_summary'),
        url(r'^nanny/insurance-cover/', NannyInsuranceCoverSummary.as_view(), name='nanny_insurance_cover_summary'),
        url(r'^nanny/arc-summary/$', NannyArcSummary.as_view(), name='nanny_arc_summary'),
        url(r'^nanny/arc-summary/confirmation', NannyArcSummaryConfirmation.as_view(), name='nanny_confirmation')
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
