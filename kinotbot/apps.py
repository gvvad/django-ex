from django.apps import AppConfig
import random, string, os, logging

from project.modules.scheduler import Scheduler
from project.modules.tbot import InvalidToken


class KinotbotConfig(AppConfig):
    name = 'kinotbot'
    secret_path = None
    host_url = None
    scheduler = None
    tbot = None

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.secret_path = os.getenv("KINO_TBOT_PATH") or "".join(random.choices(string.ascii_lowercase + string.digits, k=32))
        self.secret_path += "/"
        #   server url for telegram webhook
        self.host_url = os.getenv("HOST_URL") or "https://0.0.0.0:8443/"

    def ready(self):
        from .ex.tbot import KinoTBot
        try:
            self.tbot = KinoTBot(token=os.getenv("KINO_TBOT_TOKEN") or None,
                                 master_user=os.getenv("KINO_TBOT_MASTER") or None)

            self.tbot.set_webhook_url(self.host_url + self.secret_path, str(os.getenv("CERT_FILE_PATH")), attempt=3)
            logging.info("kinotbot sets webhook")
            self.scheduler = Scheduler(handler=self.tbot.handle_update,
                                       sleep_time=60 * int(os.getenv("KINO_TBOT_INTERVAL") or 30),
                                       start=True,
                                       is_daemon=True)
        except InvalidToken:
            logging.info("KINO_TBOT_TOKEN invalid")
        except Exception as e:
            logging.exception("Kino tbot initialize")
