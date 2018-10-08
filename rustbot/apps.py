from django.apps import AppConfig
import random, string, os, logging

from project.modules.scheduler import Scheduler
from project.modules.tbot import InvalidToken


class RustbotConfig(AppConfig):
    name = 'rustbot'
    secret_path = None
    host_url = None
    scheduler = None
    tbot = None

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.secret_path = os.getenv("RUS_TBOT_PATH") or "".join(random.choices(string.ascii_lowercase + string.digits, k=32))
        self.secret_path += "/"

        self.host_url = os.getenv("HOST_URL") or "https://0.0.0.0:8443/"

    def ready(self):
        from .ex.tbot import RusTBot
        try:
            self.tbot = RusTBot(token=os.getenv("RUS_TBOT_TOKEN") or None)

            self.tbot.set_webhook_url(self.host_url + self.secret_path, str(os.getenv("CERT_FILE_PATH")), attempt=3)

            self.scheduler = Scheduler(handler=self.tbot.handle_update,
                                       sleep_time=60 * int(os.getenv("") or 30),
                                       start=True,
                                       is_daemon=True)
        except InvalidToken:
            logging.info("RUS_TBOT_TOKEN invalid")
        except Exception as e:
            logging.exception("Rus tbot initialize", e)
