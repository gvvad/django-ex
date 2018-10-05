from django.conf import settings
#from django.shortcuts import render
from django.http import HttpResponse
from django.urls import path
import logging
import os
import string
import random

from .ex.tbot import KinoTBot
from project.modules.scheduler import Scheduler
from project.modules.tbot import InvalidToken

logging.basicConfig(level=logging.DEBUG if settings.DEBUG else logging.INFO)
logging.info("tbot views START")

#   path to app
secret_path = os.getenv("KINO_TBOT_PATH") or "".join(random.choices(string.ascii_lowercase + string.digits, k=32))
secret_path += "/"
#   server url for telegram webhook
host_url = os.getenv("HOST_URL") or "https://0.0.0.0:8443/"
try:
    tbot = KinoTBot(token=os.getenv("KINO_TBOT_TOKEN") or None,
                    master_user=os.getenv("KINO_TBOT_MASTER") or None)

    tbot.set_webhook_url(host_url + secret_path, str(os.getenv("CERT_FILE_PATH")), attempt=3)

    sched = Scheduler(handler=tbot.handle_update,
                      sleep_time=60*int(os.getenv("KINO_TBOT_INTERVAL") or 30),
                      start=True,
                      is_daemon=True)

except InvalidToken:
    logging.info("KINO_TBOT_TOKEN invalid")
except Exception as e:
    logging.exception("Kino tbot initialize", e)


def index(request):
    """
    app request handler
    :param request:
    :return:
    """
    tbot.handle_request(request)
    return HttpResponse("")


#   list of path`s
add_path = [path(secret_path, index)]
logging.info("tbot views END")
