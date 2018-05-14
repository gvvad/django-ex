import threading, time, os
import logging

from ..models import RusTbotChat
from ..models import RusTbotStore
from project.modules.tbot import TBot


class RusTBot(TBot):
    scheduler_thread = None
    interval = 30

    def __init__(self, token):
        super(RusTBot, self).__init__(token)

        try:
            self.interval = int(os.getenv("RUS_TBOT_INTERVAL"))
        except Exception:
            self.interval = 30

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

                    text = self.render_data(delta)

                    for item in RusTbotChat.chat_list():
                        try:
                            self.send_message(self.MessageResponse(
                                text=text,
                                uid=item.chat_id,
                                no_notif=not bool(delta_tag & item.tag_mask)
                            ))
                        except Exception:
                            logging.exception("scheduler dispatch")

                    RusTbotStore.remove_last(200)
            except Exception:
                logging.exception("Scheduler error:")

            time.sleep(60 * self.interval)

    #   Dispatch bot commands
    def _dispatch_cmd_help(self, chat_id):
        is_subscribed = RusTbotChat.is_chat_id(chat_id)
        res = self.MessageResponse(
            text="Вы подписаны!\n" if is_subscribed else "Вы не подписаны.\n",
            no_notif=True,
            uid=chat_id,
            inline_buttons=[[
                super().InlineKeyboardButton(text="Отписаться",
                                             callback_data="stop") if is_subscribed else
                super().InlineKeyboardButton(text="Подписаться",
                                             callback_data="start")
            ]]
        )
        res.text += "/start - Подписаться на рассылку\n" \
                    "/stop - Отписаться\n" \
                    "/help - Справка"
        return res

    def _dispatch_cmd_start(self, chat_id):
        try:
            RusTbotChat.update_chat_id(chat_id)
            res = self._dispatch_cmd_help(chat_id)
            res.text += "\nПоследние новости:\n" + self.render_data(RusTbotStore.get_last())
            return res
        except Exception:
            logging.exception("Error cmd start")

    def _dispatch_cmd_stop(self, chat_id):
        try:
            RusTbotChat.remove_chat_id(chat_id)
            return self.MessageResponse(text="Bye.", uid=chat_id)
        except Exception:
            logging.exception("Error cmd stop")

    @staticmethod
    def render_data(data):
        return "\n".join(
            ["<a href='{0}'>{1}</a> by: <i>{2}</i>".format(
                item.link,
                item.title,
                item.author
            ) for item in data])
