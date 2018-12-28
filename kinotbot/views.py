#from django.conf import settings
#from django.shortcuts import render
from django.http import HttpResponse
from django.urls import path
import logging
from django.apps import apps

app = apps.get_app_config("kinotbot")


def index(request):
    """
    app request handler
    :param request:
    :return:
    """
    try:
        logging.debug(str(request.body))
        app.tbot.handle_request(request)
    except Exception as e:
        logging.debug("Kinotbot request: {}".format(e))
    return HttpResponse("")


#   list of path`s
add_path = [path(app.secret_path, index)]
