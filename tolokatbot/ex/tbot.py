import threading, time, os
import logging

from urllib.parse import urlencode

from ..models import TbotChatModel
from ..models import TbotStoreModel
from project.modules.tbot import TBot


class TolokaTBot(TBot):
    scheduler_thread = None
    interval = None
    master_user = None

    def __init__(self, token):
        super(TolokaTBot, self).__init__(token)

        try:
            self.interval = int(os.getenv("TOLOKA_TBOT_INTERVAL"))
        except Exception:
            self.interval = 30

        try:
            self.master_user = os.getenv("TOLOKA_TBOT_MASTER")
        except Exception:
            pass

        self.scheduler_thread = threading.Thread(target=self._scheduler, daemon=True)
        self.scheduler_thread.start()

    def _handle_message(self, message):
        """Replacing method for handle messages"""
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

    def _handle_callback(self, query):
        """Replacing method for handle queries"""
        data = query["data"]
        user_id = query["from"]["id"]

        if data == "start":
            return [self.CallbackResponse(),
                    self._dispatch_cmd_start(user_id),
                    ]
        elif data == "stop":
            self._dispatch_cmd_stop(user_id)
            return [self.CallbackResponse(),
                    self._dispatch_cmd_help(user_id),
                    ]

    def _scheduler(self):
        """background daemon worker"""
        logging.info("Start toloka scheduler")
        while True:
            try:
                logging.debug("Sheduler toloka BEGIN update")
                delta = TbotStoreModel.update_posts()

                if delta:
                    for key, value in TbotChatModel.get_notification_list().items():
                        try:
                            for post in value:
                                try:
                                    # Html of post
                                    text = self.get_html_post(post)
                                    if post.poster:
                                        self.send_photo(self.PhotoResponse(caption=text,
                                                                           photo=post.poster,
                                                                           uid=key))
                                    else:
                                        self.send_message(self.MessageResponse(text=text,
                                                                               uid=key))
                                except Exception:
                                    pass

                            TbotChatModel.set_up_date(key)
                        except Exception:
                            logging.exception("Sheduler toloka set up date")
                            pass

                    TbotStoreModel.remove_last()
            except Exception:
                logging.exception("Scheduler error:")

            time.sleep(60 * self.interval)

    #   Dispatch bot commands
    def _dispatch_cmd_help(self, chat_id):
        is_subscribed = TbotChatModel.is_user(chat_id)
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
            self.send_message(self.MessageResponse(text="From: {}\n{}".format(username, text), uid=self.master_user))
            return self.MessageResponse(text="Спасибо за Ваш отзыв.")
        else:
            return None

    def _dispatch_cmd_start(self, chat_id):
        try:
            TbotChatModel.update_user(chat_id)
            res = self._dispatch_cmd_help(chat_id)
            res.text += "\nПоследние новости:\n" + self.render_data(TbotStoreModel.get_last())
            return res
        except Exception:
            logging.exception("Error cmd start")

    @staticmethod
    def _dispatch_cmd_stop(chat_id):
        try:
            TbotChatModel.remove_user(chat_id)
        except Exception:
            logging.exception("Error cmd stop")

    def _dispatch_cmd_unknown(self):
        return super().MessageResponse(text="I don`t understand you")

    @staticmethod
    def get_html_post(data):
        """Return html text for post item"""
        return "<a href='{0}'>{1} / {2} / {3}</a> <b>{4}</b> <a href='https://toloka.to/tracker.php?{5}'>Найти</a>".format(
            data.link,
            data.title_a,
            data.title_b,
            data.year,
            "HD" if bool(data.tag & 1) else "SD",
            urlencode({"f": "96",
                       "nm": str(data.title_b) + " " + str(data.year)
                       })
            )

    @classmethod
    def render_data(cls, data):
        """Return html for post`s array"""
        return "\n".join([cls.get_html_post(item) for item in data])
