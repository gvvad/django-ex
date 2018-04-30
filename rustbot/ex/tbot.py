from django.conf import settings
import json, threading, time, os
import logging
import telegram

from ..models import RusTbotChat
from ..models import RusTbotStore

logging.basicConfig(level=logging.DEBUG if settings.DEBUG else logging.INFO)

class TBot():
    scheduler_thread = None
    storage = None
    token = ""
    interval = 30

    def __init__(self, token):
        self.token = token
        self.bot = telegram.Bot(token=token)

        try:
            self.interval = int(os.getenv("RUS_TBOT_INTERVAL"))
        except Exception:
            self.interval = 30

        self.scheduler_thread = threading.Thread(target=self._scheduler, daemon=True)
        self.scheduler_thread.start()

    # Class for return result from cmd dispatcher
    class CmdResponse:
        def __init__(self, text="", buttons=None, no_notif=False):
            self.text = text
            self.buttons = buttons
            self.no_notif = no_notif

    #   background daemon worker
    def _scheduler(self):
        logging.info("Start scheduler")
        while True:
            try:
                logging.debug("Sheduler call update")
                delta = RusTbotStore.update()

                if delta:
                    delta_tag = 0
                    for item in delta:
                        delta_tag |= item.tag

                    text = TBot.render_data(delta)

                    for item in RusTbotChat.chat_list():
                        self.bot.send_message(item.chat_id,
                                              text=text,
                                              disable_notification=not bool(delta_tag & item.tag_mask),
                                              parse_mode=telegram.ParseMode.HTML)
            except Exception:
                logging.exception("Scheduler error:")

            time.sleep(60 * self.interval)

    #   Webhook update data handler
    def put_update(self, update):
        if "message" in update:
            text = update["message"]["text"]
            user_id = update["message"]["from"]["id"]
            cmd, *arg = text.split(" ")
            res = None
            if cmd == "/help":
                res = self._dispatch_cmd_help(user_id)
            elif cmd == "/start":
                res = self._dispatch_cmd_start(user_id)
            elif cmd == "/stop":
                res = self._dispatch_cmd_stop(user_id)
            elif cmd == "/notif":
                res = TBot.CmdResponse()
                if not arg or arg[0] == "all":
                    RusTbotChat.update_chat_id(user_id, -1)
                    res.text = "Все уведомления."
                elif arg[0] == "hot":
                    RusTbotChat.update_chat_id(user_id, 1)
                    res.text = "Уведомления только для 'Горячих' тем."
            else:
                res = self._dispatch_cmd_unknown(user_id)
            if res:
                self.bot.send_message(chat_id=user_id,
                                      text=res.text,
                                      parse_mode=telegram.ParseMode.HTML,
                                      disable_notification=res.no_notif
                                      )

    #   Dispatch webhook url to telegram server
    def set_webhook_url(self, url, cert_file_path=""):
        try:
            with open(cert_file_path, "rb") as cert_file:
                self.bot.setWebhook(url, cert_file)
                logging.debug("Cert is send")
        except FileNotFoundError:
            self.bot.setWebhook(url)

    #   Remove binded webhook
    def delete_webhook_url(self):
        self.bot.deleteWebhook()

    #   Dispatch bot commands
    def _dispatch_cmd_help(self, chat_id):
        res = TBot.CmdResponse(text="Вы подписаны!\n" if RusTbotChat.is_chat_id(chat_id) else "Вы не подписаны.\n")
        res.no_notif = True
        res.text += "/start - Подписаться на рассылку\n" \
                    "/stop - Отписаться\n" \
                    "/notif [all | hot] - Уведомления для всех/важных\n" \
                    "/help - Справка"
        return res

    def _dispatch_cmd_start(self, chat_id):
        try:
            RusTbotChat.update_chat_id(chat_id)
            res = self._dispatch_cmd_help(chat_id)
            res.text += "\nПоследние новости:\n" + TBot.render_data(RusTbotStore.get_last())
            return res
        except Exception:
            logging.exception("Error cmd start")

    def _dispatch_cmd_stop(self, chat_id):
        try:
            RusTbotChat.remove_chat_id(chat_id)
            return TBot.CmdResponse(text="Bye.")
        except Exception:
            logging.exception("Error cmd stop")

    def _dispatch_cmd_unknown(self, chat_id):
        return TBot.CmdResponse(text="I dont understand you")

    @staticmethod
    def render_data(data):
        return "\n".join(
            ["<a href='{0}'>{1}</a> by: <i>{2}</i>".format(
                item.link,
                item.title,
                item.author
            ) for item in data])
