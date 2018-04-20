import json, threading, time
import logging
import telegram

from tbstorage import RustorkaHotStorage as Storage

logging.basicConfig(level=logging.INFO)

class TBot():
    FILE_NAME = "tbot.json"
    settings = dict()
    chatlist = set()
    updater_thread = None
    scheduler_thread = None
    storage = None
    token = ""

    def __init__(self, token):
        self.token = token
        try:
            logging.info("Load storage: {}".format(self.FILE_NAME))
            self.storage = Storage()

            logging.info("Load settings")
            with open(self.FILE_NAME, "r") as file:
                buf = json.load(file)
                self.chatlist = set(buf["chatlist"])
                self.settings = dict(buf["settings"])
        except Exception:
            logging.exception("Error load settings:{}".format(self.FILE_NAME))

        self.bot = telegram.Bot(token=token)

        self.scheduler_thread = threading.Thread(target=self._scheduler)
        self.scheduler_thread.start()

    def _scheduler(self):
        logging.info("Start scheduler")
        while True:
            try:
                delta = self.storage.update()
                if len(delta):
                    self.dispatch_rustorka_data(delta, self.chatlist)
            except Exception:
                logging.exception("Scheduler error:")

            time.sleep(60 * 30)

    #
    #   External update data handler
    def put_update(self, update):
        if "message" in update:
            text = update["message"]["text"]
            chat_id = update["message"]["chat"]["id"]
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
    def set_webhook_url(self, url):
        self.bot.setWebhook(url)

    #
    #   Remove binded webhook
    def delete_webhook_url(self):
        self.bot.deleteWebhook()

    #
    #   Dispatch bot commands
    def _dispatch_cmd_help(self, chat_id):
        text = "You is subscribed!\n" if chat_id in self.chatlist else "You is not subscribed!\n"
        text += "/start - subscribe\n/stop - unsubscribe\n/help - see help"
        self.bot.send_message(chat_id=chat_id, text=text)

    def _dispatch_cmd_start(self, chat_id):
        try:
            self.chatlist.add(chat_id)
            self._store_settings()
            self._dispatch_cmd_help(chat_id)
            self.dispatch_rustorka_data(self.storage.get_data(), [chat_id], "Here is last update:")
        except Exception:
            logging.exception("Error cmd start")

    def _dispatch_cmd_stop(self, chat_id):
        try:
            self.chatlist.remove(chat_id)
            self._store_settings()
            self.bot.send_message(chat_id=chat_id, text="Bye.")
        except Exception:
            logging.exception("Error cmd stop")

    def _dispatch_cmd_unknown(self, chat_id):
        self.bot.send_message(chat_id=chat_id, text="I dont understand you.")

    ###

    def _store_settings(self):
        try:
            with open(self.FILE_NAME, "w") as file:
                file.write(json.dumps({
                    "settings": self.settings,
                    "chatlist": list(self.chatlist)
                }))
        except Exception:
            logging.exception("Error store settings:{}".format(self.FILE_NAME))

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
