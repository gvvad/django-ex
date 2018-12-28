# from django.conf import settings
#from django.shortcuts import render
from django.http import HttpResponse
from django.urls import path
import logging
from django.apps import apps
from django.views.decorators.csrf import csrf_exempt

app = apps.get_app_config("tolokatbot")


@csrf_exempt
def index(request):
    """
    App request handler
    :param request: Request object
    :return: Http response object
    """
    try:
        logging.debug(str(request.body))
        app.tbot.handle_request(request)
    except Exception as e:
        logging.debug("Tolokatbot request: {}".format(e))
    return HttpResponse("")


#   list of path`s
add_path = [path(app.secret_path, index)]
