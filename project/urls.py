from django.conf import settings
from django.conf.urls import include, url
from django.urls import path
from django.contrib import admin
from django.http import HttpResponse
# import logging

from rustbot.views import add_path as rustbot_add_path
from kinotbot.views import add_path as kinotbot_add_path
from tolokatbot.views import add_path as toloka_add_path

# logging.debug("urls.py START")

#   index app page
def index(val):
    return HttpResponse("Index page for app!")


urlpatterns = [
    path("", index),
    url(r'^admin/', admin.site.urls),
] + rustbot_add_path + kinotbot_add_path + toloka_add_path

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

# logging.debug("urls.py END")
