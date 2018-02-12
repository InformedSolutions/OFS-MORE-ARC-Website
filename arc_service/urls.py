"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- urls.py --

@author: Informed Solutions
"""
import re

from arc_application.views import assign_new_application, custom_login, delete_all, release_application, summary_page
from arc_application.review import review_application
from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth.views import logout

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^release/(?P<application_id>[\w\- ]+)', release_application),
    url(r'^review/(?P<application_id>[\w\- ]+)', review_application),
    url(r'^accounts/profile/', assign_new_application),
    url(r'^login/', custom_login),
    url(r'^logout/', logout, {'next_page': settings.URL_PREFIX + '/login/'}),
    url(r'^summary/', summary_page),
    url(r'^delete/', delete_all),
]

if settings.URL_PREFIX:
    prefixed_url_pattern = []
    for pat in urlpatterns:
        pat.regex = re.compile(r"^%s/%s" % (settings.URL_PREFIX[1:], pat.regex.pattern[1:]))
        prefixed_url_pattern.append(pat)
    urlpatterns = prefixed_url_pattern
