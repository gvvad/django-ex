import logging

from ..models import RusTbotChat
from ..models import RusTbotStore
from project.modules.tbot import TBot, InlineKeyboardMarkup, InlineKeyboardButton, BadRequest


class RusTBot(TBot):
    scheduler_thread = None
    interval = 30

    def __init__(self, token):
        super(RusTBot, self).__init__(token)

    #   Virtual method replace
    def _handle_message(self, message):
        text = message["text"]
        # username = message["from"]["username"]
        user_id = message["from"]["id"]
        cmd, *arg = text.split(" ", maxsplit=3)

        if cmd == "/help":
            return self._dispatch_cmd_help(user_id)
        elif cmd == "/start":
            return self._dispatch_cmd_start(user_id)
        elif cmd == "/stop":
            return self._dispatch_cmd_stop(user_id)

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
            delta = RusTbotStore.update()

            if delta:
                for item in RusTbotChat.user_list():
                    try:
                        for post in delta:
                            try:
                                if not post.poster:
                                    raise BadRequest("no poster")
                                resp = self.send(self.PhotoResponse(caption=self.get_post_text(post),
                                                                    photo=post.poster,
                                                                    uid=item.user_id))
                                post.poster = resp.photo[-1].file_id
                            except BadRequest:
                                self.send(self.MessageResponse(text=self.get_post_text(post),
                                                               uid=item.user_id))
                    except Exception as e:
                        logging.exception("user delivered", e)

                RusTbotStore.remove_last(200)
        except Exception as e:
            logging.exception("Scheduler error:", e)

    #   Dispatch bot commands
    def _dispatch_cmd_help(self, chat_id):
        is_subscribed = RusTbotChat.is_user(chat_id)
        res = self.MessageResponse(
            text="Вы подписаны!\n" if is_subscribed else "Вы не подписаны.\n",
            no_notif=True,
            uid=chat_id,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(text="Отписаться",
                                     callback_data="stop")
                if is_subscribed else
                InlineKeyboardButton(text="Подписаться",
                                     callback_data="start")
            ]])
        )
        res.text += "/start - Подписаться на рассылку\n" \
                    "/stop - Отписаться\n" \
                    "/help - Справка"
        return res

    def _dispatch_cmd_start(self, chat_id):
        try:
            RusTbotChat.update_user_id(chat_id)
            res = self._dispatch_cmd_help(chat_id)
            res.text += "\nПоследние новости:\n" + self.render_data(RusTbotStore.get_last())
            return res
        except Exception as e:
            logging.exception("Error cmd start", e)

    def _dispatch_cmd_stop(self, chat_id):
        try:
            RusTbotChat.remove_user(chat_id)
            return self.MessageResponse(text="Bye.", uid=chat_id)
        except Exception as e:
            logging.exception("Error cmd stop", e)

    @classmethod
    def get_post_text(cls, post: RusTbotStore.Container) -> str:
        return "<a href='{0}'>{1}</a> by: <i>{2}</i>".format(
                post.link,
                post.title,
                post.author)

    @classmethod
    def render_data(cls, data: list) -> str:
        return "\n".join([cls.get_post_text(item) for item in data])
