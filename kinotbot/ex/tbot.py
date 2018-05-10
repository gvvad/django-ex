import threading, time, os
import logging

from ..models import TbotChatModel
from ..models import TbotStoreModel
from project.modules.tbot import TBot


class KinoTBot(TBot):
    scheduler_thread = None
    interval = 30
    master_user = None

    def __init__(self, token):
        super(KinoTBot, self).__init__(token)

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

    #   Virtual method replace
    def _handle_message(self, message):
        text = message["text"]
        username = message["from"]["username"]
        user_id = message["from"]["id"]
        cmd, *arg = text.split(" ", maxsplit=3)

        if cmd == "/help":
            return self._dispatch_cmd_help(user_id)
        elif cmd == "/start":
            return self._dispatch_cmd_start(user_id)
        elif cmd == "/stop":
            return self._dispatch_cmd_stop(user_id)
        elif cmd == "/re":
            return self._dispatch_cmd_re(user_id, text[4:], username=username)

    #   Virtual method replace
    def _handle_callback(self, query):
        data = query["data"]
        user_id = query["from"]["id"]
        res = None

        if data == "start":
            return [self.CallbackResponse(),
                    self._dispatch_cmd_start(user_id),
                    ]
        elif data == "stop":
            self._dispatch_cmd_stop(user_id)
            return [self.CallbackResponse(),
                    self._dispatch_cmd_help(user_id),
                    ]

    #   background daemon worker
    def _scheduler(self):
        logging.info("Start scheduler")
        while True:
            try:
                logging.debug("Sheduler call update")
                delta = TbotStoreModel.update()

                if delta:
                    for chat in TbotChatModel.chat_list():
                        try:
                            for post in TbotStoreModel.get_not_earlier(chat.notif_date):
                                text = "<a href='{0}'>{1} / {2} / {3}</a> <b>{4}</b>". \
                                    format(post.link,
                                           post.title_ru,
                                           post.title_en,
                                           post.year,
                                           "HD" if bool(post.tag & 1) else "SD")
                                self.send_photo(self.PhotoResponse(caption=text,
                                                                   photo=post.poster,
                                                                   uid=chat.chat_id))

                            TbotChatModel.notif_user(chat.chat_id)
                        except Exception:
                            logging.exception("schedule notif")
                            pass

                    TbotStoreModel.remove_last()
            except Exception:
                logging.exception("Scheduler error:")

            time.sleep(60 * self.interval)

    #   Dispatch bot commands
    def _dispatch_cmd_help(self, chat_id):
        is_subscribed = TbotChatModel.is_chat_id(chat_id)
        res = super().MessageResponse(text="Вы подписаны!\n" if is_subscribed else "Вы не подписаны.\n",
                                      inline_buttons=[[
                                          super().InlineKeyboardButton(text="Отписаться",
                                                                       callback_data="stop") if is_subscribed else
                                          super().InlineKeyboardButton(text="Подписаться",
                                                                       callback_data="start")
                                      ]])
        res.no_notif = True
        res.text += "/start - Подписаться на рассылку\n" \
                    "/stop - Отписаться\n" \
                    "/re {message} - Написать отзыв\n" \
                    "/help - Справка"
        return res

    def _dispatch_cmd_re(self, user_id, text, username=""):
        if text:
            self.bot.send_message(chat_id=self.master_user, text="From: {}\n{}".format(username, text))
            return super().MessageResponse(text="Спасибо за Ваш отзыв.")
        else:
            return None

    def _dispatch_cmd_start(self, chat_id):
        try:
            TbotChatModel.update_chat_id(chat_id)
            res = self._dispatch_cmd_help(chat_id)
            res.text += "\nПоследние новости:\n" + self.render_data(TbotStoreModel.get_last())
            return res
        except Exception:
            logging.exception("Error cmd start")

    def _dispatch_cmd_stop(self, chat_id):
        try:
            TbotChatModel.remove_chat_id(chat_id)
        except Exception:
            logging.exception("Error cmd stop")

    def _dispatch_cmd_unknown(self):
        return super().MessageResponse(text="I dont understand you")

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
