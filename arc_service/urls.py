"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- urls.py --

@author: Informed Solutions
"""
import re

from arc_application.views import assign_new_application, custom_login, error_404, error_500, release, \
    summary_page, arc_summary, comments, contact_summary, dbs_check_summary, first_aid_training_summary, \
    health_check_answers, personal_details_summary, references_summary, review, task_list, \
    type_of_childcare_age_groups, AuditlogListView, cc_summary
from arc_application.views.other_people_addresses import address_state_dispatcher
from arc_application.views.other_people_in_home import other_people_summary, add_previous_name
from arc_application.contact_centre import search
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.views import logout

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^release/(?P<application_id>[\w\- ]+)', release, name='release'),
    url(r'^accounts/profile/', assign_new_application, name='new_application'),
    url(r'^login/', custom_login, name='login'),
    url(r'^logout/', logout, {'next_page': settings.URL_PREFIX + '/login/'}),
    url(r'^summary/', summary_page, name='summary'),
    url(r'^review/', task_list, name='task_list'),
    url(r'^account/summary/', contact_summary, name='contact_summary'),
    url(r'^childcare/age-groups/', type_of_childcare_age_groups, name='type_of_childcare_age_groups'),
    url(r'^personal-details/summary/', personal_details_summary, name='personal_details_summary'),
    url(r'^first-aid/summary/', first_aid_training_summary, name='first_aid_training_summary'),
    url(r'^dbs-check/summary/', dbs_check_summary, name='dbs_check_summary'),
    url(r'^references/summary/', references_summary, name='references_summary'),
    url(r'^other-people/summary/', other_people_summary, name='other_people_summary'),
    url(r'^people-in-home/previous_names', add_previous_name, name='other-people-previous-names'),
    url(r'^people-in-home/previous_addresses', address_state_dispatcher, name='other-people-previous-addresses'),
    url(r'^health/check-answers/', health_check_answers, name='health_check_answers'),
    url(r'^confirmation/', review, name='review'),
    url(r'^comments/', comments, name='comments'),
    url(r'^arc-summary/', arc_summary, name='arc-summary'),
    url(r'^auditlog/', AuditlogListView.as_view(), name='auditlog'),
    url(r'^search/', search, name='search'),
    url(r'^search-summary/', cc_summary, name='search_summary'),

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

handler404 = error_404
handler500 = error_500
