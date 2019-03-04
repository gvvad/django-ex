from django.apps import AppConfig
import random, string, os, logging, time

from project.modules.scheduler import Scheduler
from project.modules.tbot import InvalidToken


class TolokatbotConfig(AppConfig):
    name = 'tolokatbot'
    secret_path = None
    host_url = None
    scheduler = None
    tbot = None
    s_sleep = 30 * 60

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.secret_path =\
            os.getenv("TOLOKA_TBOT_PATH") or\
            "".join([random.choice(string.digits+string.ascii_lowercase) for i in range(32)])
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
        from .ex.tbot import TolokaTBot
        try:
            self.tbot = TolokaTBot(token=os.getenv("TOLOKA_TBOT_TOKEN") or None,
                                   master_user=os.getenv("TOLOKA_TBOT_MASTER") or None)

            self.s_sleep = 60 * int(os.getenv("TOLOKA_TBOT_INTERVAL") or 30)
        except InvalidToken:
            logging.info("TOLOKA_TBOT_TOKEN invalid")
        except Exception as e:
            logging.exception("Toloka tbot initialize: {}".format(e))
