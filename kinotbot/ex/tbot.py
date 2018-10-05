import threading, time, os
import logging

from ..models import TbotChatModel
from ..models import TbotStoreModel
from project.modules.tbot import TBot, InlineKeyboardMarkup, InlineKeyboardButton, BadRequest


class KinoTBot(TBot):
    scheduler_thread = None
    interval = 30
    master_user = None

    def __init__(self, token, master_user=None):
        super(KinoTBot, self).__init__(token)
        self.master_user = master_user

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

        if data == "start":
            return [self.CallbackResponse(),
                    self._dispatch_cmd_start(user_id),
                    ]
        elif data == "stop":
            self._dispatch_cmd_stop(user_id)
            return [self.CallbackResponse(),
                    self._dispatch_cmd_help(user_id),
                    ]

    def handle_update(self):
        try:
            logging.debug("Sheduler call update")
            delta = TbotStoreModel.update()

            if delta:
                for user in TbotChatModel.user_list():
                    try:
                        for post in delta:
                            try:
                                resp = self.send(self.PhotoResponse(caption=self.get_post_text(post),
                                                                    photo=post.poster,
                                                                    uid=user.user_id))
                                post.poster = resp.photo[-1].file_id
                            except BadRequest:
                                self.send(self.MessageResponse(text=self.get_post_text(post),
                                                               uid=user.user_id))

                    except Exception as e:
                        logging.exception("schedule notif", e)
                    TbotChatModel.set_up_date(user.user_id)

                TbotStoreModel.remove_last()
        except Exception as e:
            logging.exception("Scheduler error:", e)

    #   Dispatch bot commands
    def _dispatch_cmd_help(self, chat_id):
        is_subscribed = TbotChatModel.is_user(chat_id)
        res = self.MessageResponse(text="Вы подписаны!\n" if is_subscribed else "Вы не подписаны.\n",
                                   reply_markup=InlineKeyboardMarkup(
                                       [[InlineKeyboardButton(text="Отписаться", callback_data="stop")]]
                                       if is_subscribed else
                                       [[InlineKeyboardButton(text="Подписаться", callback_data="start")]]),
                                   no_notif=True
                                   )
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
            TbotChatModel.remove_user(chat_id)
        except Exception:
            logging.exception("Error cmd stop")

    def _dispatch_cmd_unknown(self):
        return super().MessageResponse(text="I dont understand you")
    
    @classmethod
    def get_post_text(cls, post):
        return "<a href='{0}'>{1} / {2} / {3}</a> <b>{4}</b>".format(
                post.link,
                post.title_ru,
                post.title_en,
                post.year,
                "HD" if bool(post.tag & 1) else "SD")
    
    @classmethod
    def render_data(cls, data):
        return "\n".join([cls.get_post_text(item) for item in data])
