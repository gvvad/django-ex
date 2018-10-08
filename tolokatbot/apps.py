from django.apps import AppConfig
import random, string, os, logging

from project.modules.scheduler import Scheduler
from project.modules.tbot import InvalidToken


class TolokatbotConfig(AppConfig):
    name = 'tolokatbot'
    secret_path = None
    host_url = None
    scheduler = None
    tbot = None

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.secret_path = os.getenv("TOLOKA_TBOT_PATH") or "".join(random.choices(string.ascii_lowercase + string.digits, k=32))
        self.secret_path += "/"
        self.host_url = os.getenv("HOST_URL") or "https://0.0.0.0:8443/"

    def ready(self):
        from .ex.tbot import TolokaTBot
        try:
            self.tbot = TolokaTBot(token=os.getenv("TOLOKA_TBOT_TOKEN") or None,
                                   master_user=os.getenv("TOLOKA_TBOT_MASTER") or None)

            self.tbot.set_webhook_url(self.host_url + self.secret_path, str(os.getenv("CERT_FILE_PATH")), attempt=3)
            logging.info("tolokatbot sets webhook")
            self.scheduler = Scheduler(self.tbot.handle_update,
                                       60 * int(os.getenv("TOLOKA_TBOT_INTERVAL") or 30),
                                       start=True,
                                       is_daemon=True)
        except InvalidToken:
            logging.info("TOLOKA_TBOT_TOKEN invalid")
        except Exception as e:
            logging.exception("Toloka tbot initialize")