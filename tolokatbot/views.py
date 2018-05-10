from django.conf import settings
#from django.shortcuts import render
from django.http import HttpResponse
from django.urls import path
import logging
import os

from .ex.tbot import TolokaTBot

logging.basicConfig(level=logging.DEBUG if settings.DEBUG else logging.INFO)
logging.info("tbot views START")

#   path to app
secret_path = os.getenv("TOLOKA_TBOT_PATH") or "f90a8802866541d489d1db5d78e90782"
secret_path += "/"
#   server url for telegram webhook
host_url = os.getenv("HOST_URL") or "https://0.0.0.0:8443/"
tbot_token = os.getenv("TOLOKA_TBOT_TOKEN") or "000-xxx"
try:
    pass
    tbot = TolokaTBot(tbot_token)
    tbot.set_webhook_url(host_url + secret_path, str(os.getenv("CERT_FILE_PATH")))
except Exception:
    logging.exception("Toloka tbot initialize")


#   app request handler
def index(request):
    tbot.handle_request(request)
    return HttpResponse("")


#   list of path`s
add_path = [path(secret_path, index)]
logging.info("tbot views END")
