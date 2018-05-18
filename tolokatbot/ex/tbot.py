import threading, time, os
import logging

from ..models import TbotChatModel
from ..models import TbotStoreModel
from project.modules.tbot import TBot


class TolokaTBot(TBot):
    scheduler_thread = None
    interval = 30
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
        logging.info("Start toloka scheduler")
        while True:
            try:
                a = TbotChatModel.user_list()

                logging.debug("Sheduler toloka update")
                delta = TbotStoreModel.update_posts()

                if delta:
                    for key, value in TbotChatModel.get_notification_list().items():
                        try:
                            for post in value:
                                try:
                                    text = "<a href='{0}'>{1} / {2} / {3}</a> <b>{4}</b>". \
                                        format(post.link,
                                               post.title_a,
                                               post.title_b,
                                               post.year,
                                               "HD" if bool(post.tag & 1) else "SD")
                                    if post.poster:
                                        self.send_photo(self.PhotoResponse(caption=text,
                                                                           photo=post.poster,
                                                                           uid=key))
                                    else:
                                        self.send_message(self.MessageResponse(text=text,
                                                                               uid=key))
                                except Exception:
                                    pass

                            TbotChatModel.up_date(key)
                        except Exception:
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

    def _dispatch_cmd_stop(self, chat_id):
        try:
            TbotChatModel.remove_user(chat_id)
        except Exception:
            logging.exception("Error cmd stop")

    def _dispatch_cmd_unknown(self):
        return super().MessageResponse(text="I dont understand you")

    @staticmethod
    def render_data(data):
        return "\n".join(
            ["<a href='{0}'>{1} / {2} / {3}</a> <b>{4}</b>".format(
                item.link,
                item.title_a,
                item.title_b,
                item.year,
                "HD" if bool(item.tag & 1) else "SD"
            ) for item in data])
