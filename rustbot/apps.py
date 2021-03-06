from django.apps import AppConfig
import random, string, os, logging
import time
# from project.modules.scheduler import Scheduler
from project.modules.tbot import InvalidToken


class RustbotConfig(AppConfig):
    name = 'rustbot'
    secret_path = None
    host_url = None
    scheduler = None
    tbot = None
    s_sleep = 30 * 60

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.secret_path = \
            os.getenv("RUS_TBOT_PATH") or \
            "".join([random.choice(string.digits + string.ascii_lowercase) for i in range(32)])
        self.secret_path += "/"

        self.host_url = os.getenv("HOST_URL") or "https://0.0.0.0:8443/"

    def run_schedule(self):
        while True:
            try:
                self.tbot.handle_update()
            except Exception as e:
                logging.exception("Scheduler: {}".format(e))
                break
            time.sleep(self.s_sleep)

    def set_webhook(self):
        if self.tbot:
            self.tbot.set_webhook_url(self.host_url + self.secret_path, str(os.getenv("CERT_FILE_PATH")), attempt=3)

    def ready(self):
        from .ex.tbot import RusTBot
        try:
            self.tbot = RusTBot(token=os.getenv("RUS_TBOT_TOKEN") or None)
        except InvalidToken:
            logging.info("RUS_TBOT_TOKEN invalid")
        except Exception as e:
            logging.exception("Rus tbot initialize: {}".format(e))
