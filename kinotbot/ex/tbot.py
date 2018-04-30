from django.conf import settings
import json, threading, time, os
import logging
import telegram

from ..models import TbotChatModel
from ..models import TbotStoreModel

logging.basicConfig(level=logging.DEBUG if settings.DEBUG else logging.INFO)

class TBot():
    scheduler_thread = None
    storage = None
    token = ""
    interval = 30
    master_user = None

    def __init__(self, token):
        self.token = token
        self.bot = telegram.Bot(token=token)

        try:
            self.interval = int(os.getenv("KINO_TBOT_INTERVAL"))
        except Exception:
            self.interval = 30

        try:
            self.master_user = os.getenv("KINO_TBOT_MASTER")
        except Exception:
            pass

        self.scheduler_thread = threading.Thread(target=self._scheduler, daemon=True)
        self.scheduler_thread.start()

    # Class for return result from cmd dispatcher
    class CmdResponse:
        def __init__(self, text, buttons=None, no_notif=False):
            self.text = text
            self.buttons = buttons
            self.no_notif = no_notif

    #   background daemon worker
    def _scheduler(self):
        logging.info("Start scheduler")
        while True:
            try:
                logging.debug("Sheduler call update")
                delta = TbotStoreModel.update()

                if delta:
                    delta_tag = 0
                    for d in delta:
                        delta_tag |= d.tag

                    for chat in TbotChatModel.chat_list():
                        for post in TbotStoreModel.get_last(not_earlier=chat.notif_date):
                            text = "<a href='{0}'>{1} / {2} / {3}</a> <b>{4}</b>". \
                                format(post.link,
                                       post.title_ru,
                                       post.title_en,
                                       post.year,
                                       "HD" if bool(post.tag & 1) else "SD")
                            self._send_photo(chat.chat_id,
                                             url=post.poster,
                                             text=text,
                                             no_notif=not bool(delta_tag & chat.tag_mask))
                    '''
                    for post in delta:
                        text = "<a href='{0}'>{1} / {2} / {3}</a> <b>{4}</b>". \
                            format(post.link,
                                   post.title_ru,
                                   post.title_en,
                                   post.year,
                                   "HD" if bool(post.tag & 1) else "SD")
                        for item in TbotChatModel.chat_list():
                            self._send_photo(item.chat_id,
                                             url=post.poster,
                                             text=text,
                                             no_notif=not bool(delta_tag & item.tag_mask))
                    '''
                    TbotStoreModel.remove_last(200)
            except Exception:
                logging.exception("Scheduler error:")

            time.sleep(60 * self.interval)

    #   Webhook update data handler
    def put_update(self, update):
        if "message" in update:
            text = update["message"]["text"]
            username = update["message"]["from"]["username"]
            user_id = update["message"]["from"]["id"]
            cmd, *arg = text.split(" ")
            res = None
            if cmd == "/help":
                res = self._dispatch_cmd_help(user_id)
            elif cmd == "/start":
                res = self._dispatch_cmd_start(user_id)
            elif cmd == "/stop":
                res = self._dispatch_cmd_stop(user_id)
            elif cmd == "/re":
                res = self._dispatch_cmd_re(user_id, text, username=username)
            else:
                pass
                #res = self._dispatch_cmd_unknown(user_id)
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
        res = TBot.CmdResponse(text="Вы подписаны!\n" if TbotChatModel.is_chat_id(chat_id) else "Вы не подписаны.\n")
        res.no_notif = True
        res.text += "/start - Подписаться на рассылку\n" \
                    "/stop - Отписаться\n" \
                    "/re {message} - Написать отзыв\n" \
                    "/help - Справка"
        return res

    def _dispatch_cmd_re(self, user_id, text, username=""):
        self.bot.send_message(chat_id=self.master_user, text="From: {}\n{}".format(username, text))
        res = TBot.CmdResponse(text="Спасибо за Ваш отзыв.")
        return res

    def _dispatch_cmd_start(self, chat_id):
        try:
            TbotChatModel.update_chat_id(chat_id)
            res = self._dispatch_cmd_help(chat_id)
            res.text += "\nПоследние новости:\n" + TBot.render_data(TbotStoreModel.get_last())
            return res
        except Exception:
            logging.exception("Error cmd start")

    def _dispatch_cmd_stop(self, chat_id):
        try:
            TbotChatModel.remove_chat_id(chat_id)
            return TBot.CmdResponse(text="Bye.")
        except Exception:
            logging.exception("Error cmd stop")

    def _dispatch_cmd_unknown(self, chat_id):
        return TBot.CmdResponse(text="I dont understand you")

    def _send_photo(self, chat_id, url, text, no_notif=False):
        self.bot.send_photo(chat_id=chat_id,
                            photo=url,
                            caption=text,
                            parse_mode=telegram.ParseMode.HTML,
                            disable_notification=no_notif)

    @staticmethod
    def render_data(data):
        return "\n".join(
            ["<a href='{0}'>{1} / {2} / {3}</a> <b>{4}</b>".format(
                item.link,
                item.title_ru,
                item.title_en,
                item.year,
                "HD" if bool(item.tag & 1) else "SD"
            ) for item in data])
