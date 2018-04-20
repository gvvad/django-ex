from django.shortcuts import render
from django.http import HttpResponse
from django.urls import path
import json
import os

from .ex.tbot import TBot

from .models import RusTbotStore

secret_path = str(os.getenv("RUS_TBOT_PATH"))+"/" or "c8081a0e49194d6db60b6ef0d975a7c5/"
host_url = os.getenv("HOST_URL") or "https://123.123.123.123/"
tbot_token = os.getenv("RUS_TBOT_TOKEN") or "000000000:xxxxxxxxxxxxxxxxxxxxxxxxxxx-xxxxxxx"

tbot = TBot(tbot_token)
tbot.set_webhook_url(host_url + secret_path)

def debug(request):
    s = "{}<br>{}<br>{}".format(str(RusTbotStore.get_last()), secret_path, host_url)
    return HttpResponse(s)

def index(request):
    if request.method == "GET":
        return HttpResponse("rustbot OK")
    elif request.method == "POST":
        try:
            tbot.put_update(json.loads(request.body))
        except Exception:
            pass
        return HttpResponse("")

add_path = [path(secret_path, index), path("debug", debug)]
