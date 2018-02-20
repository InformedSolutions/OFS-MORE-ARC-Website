"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- urls.py --

@author: Informed Solutions
"""
import re

from arc_application.review import contact_summary, task_list, type_of_childcare_age_groups, personal_details_summary, \
    first_aid_training_summary, dbs_check_summary, references_summary, other_people_summary, health_check_answers, \
    declaration, review, comments, arc_summary
from arc_application.views import assign_new_application, custom_login, delete_all, release_application, summary_page
from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth.views import logout

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^release/(?P<application_id>[\w\- ]+)', release_application),
    url(r'^accounts/profile/', assign_new_application),
    url(r'^login/', custom_login),
    url(r'^logout/', logout, {'next_page': settings.URL_PREFIX + '/login/'}),
    url(r'^summary/', summary_page),
    url(r'^delete/', delete_all),
    url(r'^review/', task_list),
    url(r'^account/summary/', contact_summary),
    url(r'^childcare/age-groups/', type_of_childcare_age_groups),
    url(r'^personal-details/summary/', personal_details_summary),
    url(r'^first-aid/summary/', first_aid_training_summary),
    url(r'^dbs-check/summary/', dbs_check_summary),
    url(r'^references/summary/', references_summary),
    url(r'^other-people/summary/', other_people_summary),
    url(r'^health/check-answers/', health_check_answers),
    url(r'^declaration/', declaration),
    url(r'^confirmation/', review),
    url(r'^comments/', comments),
    url(r'^arc-summary/', arc_summary),

]

if settings.URL_PREFIX:
    prefixed_url_pattern = []
    for pat in urlpatterns:
        pat.regex = re.compile(r"^%s/%s" % (settings.URL_PREFIX[1:], pat.regex.pattern[1:]))
        prefixed_url_pattern.append(pat)
    urlpatterns = prefixed_url_pattern
