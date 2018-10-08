from django.conf import settings
#from django.shortcuts import render
from django.http import HttpResponse
from django.urls import path
import logging
import os
import random
import string
from project.modules.scheduler import Scheduler
from project.modules.tbot import InvalidToken

from .ex.tbot import TolokaTBot

logging.info("tbot views START")

#   path to app
secret_path = os.getenv("TOLOKA_TBOT_PATH") or "".join(random.choices(string.ascii_lowercase + string.digits, k=32))
secret_path += "/"

#   server url for telegram webhook
host_url = os.getenv("HOST_URL") or "https://0.0.0.0:8443/"
tbot = None
sch = None
try:
    tbot = TolokaTBot(token=os.getenv("TOLOKA_TBOT_TOKEN") or None,
                      master_user=os.getenv("TOLOKA_TBOT_MASTER") or None)

    tbot.set_webhook_url(host_url + secret_path, str(os.getenv("CERT_FILE_PATH")), attempt=3)

    sch = Scheduler(tbot.handle_update,
                    60*int(os.getenv("TOLOKA_TBOT_INTERVAL") or 30),
                    start=True,
                    is_daemon=True)
except InvalidToken:
    logging.info("TOLOKA_TBOT_TOKEN invalid")
except Exception as e:
    logging.exception("Toloka tbot initialize", e)


def index(request):
    """
    App request handler
    :param request: Request object
    :return: Http response object
    """
    tbot.handle_request(request)
    return HttpResponse("")


#   list of path`s
add_path = [path(secret_path, index)]
logging.info("tbot views END")
