import logging

from urllib.parse import urlencode

from ..models import TbotChatModel
from ..models import TbotStoreModel
from project.modules.tbot import TBot, InlineKeyboardMarkup, InlineKeyboardButton, BadRequest
from .parser import TolokaWebParser


class TolokaTBot(TBot):
    scheduler_thread = None
    master_user = None

    def __init__(self, token, master_user=None):
        """
        Create bot object
        :param token: telegram token
        :param master_user: master-user id(feedback)
        """
        super(TolokaTBot, self).__init__(token)
        self.master_user = master_user

    def _handle_message(self, message):
        """
        Replacing method for handle messages
        :param message:
        :return:
        """
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
        """
        Replacing method for handle queries
        :param query:
        :return:
        """
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
        """
        Check update and dispatch
        """
        try:
            logging.debug("Sheduler toloka BEGIN update")
            delta = TbotStoreModel.update_posts()

            if delta:
                for user in TbotChatModel.user_list():
                    try:
                        for post in delta:
                            try:
                                if not post.poster:
                                    raise BadRequest("no poster")
                                resp = self.send(self.PhotoResponse(caption=self.get_html_post(post),
                                                                    photo=post.poster,
                                                                    uid=user.user_id))
                                post.poster = resp.photo[-1].file_id
                            except BadRequest:
                                self.send(self.MessageResponse(text=self.get_html_post(post),
                                                               uid=user.user_id))
                        TbotChatModel.set_up_date(user.user_id)
                    except Exception as e:
                        logging.exception("Scheduler toloka set up date", e)

                TbotStoreModel.remove_last()
        except Exception as e:
            logging.exception("Toloka handle update", e)

    def send_post(self, uid, post):
        """Send post data to user"""
        html = self.get_html_post(post)
        if post.poster:
            self.send(self.PhotoResponse(caption=html,
                                         photo=post.poster,
                                         uid=uid))
        else:
            self.send(self.MessageResponse(text=html,
                                           uid=uid))

    #   Dispatch bot commands
    def _dispatch_cmd_help(self, chat_id):
        """
        :param chat_id: user|chat id
        :return: MessageResponse
        """
        is_subscribed = TbotChatModel.is_user(chat_id)
        res = self.MessageResponse(text=("Вы подписаны!\n"
                                         if is_subscribed else
                                         "Вы не подписаны.\n"),
                                   reply_markup=InlineKeyboardMarkup(
                                       [[InlineKeyboardButton(text="Отписаться", callback_data="stop")]]
                                       if is_subscribed else
                                       [[InlineKeyboardButton(text="Подписаться", callback_data="start")]]
                                                                 ),
                                   no_notif=True
                                   )
        res.text += "/start - Подписаться на рассылку\n" \
                    "/stop - Отписаться\n" \
                    "/re {message} - Написать отзыв\n" \
                    "/help - Справка"
        return res

    def _dispatch_cmd_re(self, user_id, text, username=""):
        if text:
            self.send(self.MessageResponse(text="From: {}\n{}".format(username, text), uid=self.master_user))
            return self.MessageResponse(text="Спасибо за Ваш отзыв.")
        else:
            return None

    def _dispatch_cmd_start(self, chat_id):
        try:
            TbotChatModel.update_user(chat_id)
            res = self._dispatch_cmd_help(chat_id)
            res.text += "\nПоследние новости:\n" + self.render_data(TbotStoreModel.get_last())
            return res
        except Exception as e:
            logging.exception("Error cmd start", e)

    @staticmethod
    def _dispatch_cmd_stop(chat_id):
        try:
            TbotChatModel.remove_user(chat_id)
        except Exception as e:
            logging.exception("Error cmd stop", e)

    def _dispatch_cmd_unknown(self):
        return super().MessageResponse(text="I don`t understand you")

    @staticmethod
    def get_html_post(post):
        """Return html text for post item"""
        return "<a href='{0}'>{1} / {2} / {3}</a> <b>{4}</b> <a href='{5}/tracker.php?{6}'>Найти</a>".\
            format(
                post.link,
                post.title_a,
                post.title_b,
                post.year,
                "HD" if bool(post.tag & 1) else "SD",
                TolokaWebParser.HOST,
                urlencode({"nm": str(post.title_b or post.title_a) + " " + str(post.year)}))

    @classmethod
    def render_data(cls, data):
        """Return html for post`s array"""
        return "\n".join([cls.get_html_post(item) for item in data])
