import json, threading, time
import logging
import telegram

from ..models import RusTbotChat
from ..models import RusTbotStore

logging.basicConfig(level=logging.DEBUG)

class TBot():
    updater_thread = None
    scheduler_thread = None
    storage = None
    token = ""

    def __init__(self, token):
        self.token = token
        self.bot = telegram.Bot(token=token)

        self.scheduler_thread = threading.Thread(target=self._scheduler, daemon=True)
        self.scheduler_thread.start()

    def _scheduler(self):
        logging.info("Start scheduler")
        while True:
            try:
                logging.debug("Sheduler call update")
                delta = RusTbotStore.update()
                if delta:
                    self.dispatch_rustorka_data(delta, RusTbotChat.chat_list())
            except Exception:
                logging.exception("Scheduler error:")

            time.sleep(60 * 30) #30 minutes interval

    #
    #   Webhook update data handler
    def put_update(self, update):
        if "message" in update:
            text = update["message"]["text"]
            chat_id = update["message"]["from"]["id"]
            if text == "/help":
                self._dispatch_cmd_help(chat_id)
            elif text == "/start":
                self._dispatch_cmd_start(chat_id)
            elif text == "/stop":
                self._dispatch_cmd_stop(chat_id)
            else:
                self._dispatch_cmd_unknown(chat_id)

    #
    #   Dispatch webhook url to telegram server
    def set_webhook_url(self, url, cert_file_path=""):
        try:
            with open(cert_file_path, "rb") as cert_file:
                self.bot.setWebhook(url, cert_file)
                logging.debug("Cert is send")
        except FileNotFoundError:
            self.bot.setWebhook(url)

    #
    #   Remove binded webhook
    def delete_webhook_url(self):
        self.bot.deleteWebhook()

    #
    #   Dispatch bot commands
    def _dispatch_cmd_help(self, chat_id):
        text = "You is subscribed!\n" if RusTbotChat.is_chat_id(chat_id) else "You is not subscribed!\n"
        text += "/start - subscribe\n/stop - unsubscribe\n/help - see help"
        self.bot.send_message(chat_id=chat_id, text=text)

    def _dispatch_cmd_start(self, chat_id):
        try:
            RusTbotChat.store_chat_id(chat_id)
            self._dispatch_cmd_help(chat_id)
            self.dispatch_rustorka_data(RusTbotStore.get_last(), [chat_id], "Here is last update:")
        except Exception:
            logging.exception("Error cmd start")

    def _dispatch_cmd_stop(self, chat_id):
        try:
            RusTbotChat.remove_chat_id(chat_id)
            self.bot.send_message(chat_id=chat_id, text="Bye.")
        except Exception:
            logging.exception("Error cmd stop")

    def _dispatch_cmd_unknown(self, chat_id):
        self.bot.send_message(chat_id=chat_id, text="I dont understand you.")

    ###

    def dispatch_rustorka_data(self, datas, chats, prefix=""):
        text = prefix + "\n" if prefix else ""
        text += "\n".join(
            ["<a href='{0}'>{1}</a> by:<i>{2}</i>".format(
                item["link"],
                item["title"],
                item["author"]
            ) for item in datas])

        for ch_id in chats:
            self.bot.send_message(ch_id, text, parse_mode="html")
