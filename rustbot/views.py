# from django.conf import settings
#from django.shortcuts import render
from django.http import HttpResponse
from django.urls import path
from django.apps import apps
import logging

app = apps.get_app_config("rustbot")


def index(request):
    """
    app request handler
    """
    try:
        logging.debug(str(request.body))
        app.tbot.handle_request(request)
    except Exception as e:
        logging.debug("Rustbot request: {}".format(e))
    return HttpResponse("")


#   list of path`s
add_path = [path(app.secret_path, index)]
