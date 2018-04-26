from django.conf import settings
#from django.shortcuts import render
from django.http import HttpResponse
from django.urls import path
import logging
import json
import os

from .ex.tbot import TBot

logging.basicConfig(level=logging.DEBUG if settings.DEBUG else logging.INFO)
logging.info("tbot views START")

#   path to app
secret_path = os.getenv("RUS_TBOT_PATH") or "c8081a0e49194d6db60b6ef0d975a7c5"
secret_path += "/"
#   server url for telegram webhook
host_url = os.getenv("HOST_URL") or "https://0.0.0.0:8443/"
tbot_token = os.getenv("RUS_TBOT_TOKEN") or "000-xxx"

tbot = TBot(tbot_token)
tbot.set_webhook_url(host_url + secret_path, str(os.getenv("CERT_FILE_PATH")))

#   app request handler
def index(request):
    if request.method == "GET":
        return HttpResponse("rustbot OK")
    elif request.method == "POST":
        try:
            logging.debug(request.body)
            tbot.put_update(json.loads(request.body))
        except Exception:
            logging.exception("POST response")
        return HttpResponse("")

#   list of path`s
add_path = [path(secret_path, index)]
logging.info("tbot views END")
