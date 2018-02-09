

from django.conf.urls import url, include
from django.contrib import admin
from application.views import assign_new_application, custom_login, summary_page, delete_all
from django.contrib.auth.views import logout

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^test/', assign_new_application),
    url('^accounts/profile/', assign_new_application),
    url('^login/', custom_login),
    url('^logout/', logout, {'next_page': '/login/'}),
    url('^summary/', summary_page),
    url('^delete/', delete_all),
]
