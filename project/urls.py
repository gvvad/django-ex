from django.conf import settings
from django.conf.urls import include, url
from django.urls import path
from django.contrib import admin
from django.http import HttpResponse

from rustbot.views import add_path

def index(val):
    return HttpResponse("Index page for app!")

urlpatterns = [
    # Examples:
    # url(r'^$', 'project.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    path("", index),
    url(r'^admin/', admin.site.urls),
] + add_path

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
