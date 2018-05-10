import telegram
import json
import logging


class TBot(object):
    token = ""

    class InlineKeyboardButton(telegram.InlineKeyboardButton):
        def __init__(self, *args, **kwargs):
            super(TBot.InlineKeyboardButton, self).__init__(*args, **kwargs)

    class MessageResponse:
        def __init__(self, text, uid=None, buttons=None, inline_buttons=None, parse_mode=telegram.ParseMode.HTML, no_notif=False):
            self.reply_markup = None
            if buttons:
                self.reply_markup = telegram.ReplyKeyboardMarkup(buttons)
            elif inline_buttons:
                self.reply_markup = telegram.InlineKeyboardMarkup(inline_buttons)
            self.uid = uid
            self.text = text
            self.no_notif = no_notif
            self.parse_mode = parse_mode

    class CallbackResponse:
        def __init__(self, cid=None, text=None, url=None, alert=False):
            self.cid = cid
            self.text = text
            self.url = url
            self.alert = alert

    class PhotoResponse:
        def __init__(self, caption, photo, uid=None, buttons=None, parse_mode=telegram.ParseMode.HTML, no_notif=False):
            self.uid = uid
            self.caption = caption
            self.photo = photo
            self.no_notif = no_notif
            self.parse_mode = parse_mode

    def __init__(self, token):
        self.token = token
        self.bot = telegram.Bot(token=token)

    def send_message(self, resp):
        return self.bot.send_message(
            chat_id=resp.uid,
            text=resp.text,
            parse_mode=resp.parse_mode,
            reply_markup=resp.reply_markup,
            disable_notification=resp.no_notif
        )

    def send_photo(self, resp):
        return self.bot.send_photo(
            chat_id=resp.uid,
            photo=resp.photo,
            caption=resp.caption,
            parse_mode=resp.parse_mode,
            disable_notification=resp.no_notif
        )

    def answer_callback_query(self, resp):
        return self.bot.answer_callback_query(
            callback_query_id=resp.cid,
            text=resp.text,
            show_alert=resp.alert,
            url=resp.url
        )

    def handle_request(self, request):
        if request.method == "GET":
            return
        elif request.method == "POST":
            try:
                logging.debug(request.body)
                update = json.loads(request.body)
                resp = None
                uid = None
                cid = None

                if "message" in update:
                    uid = update["message"]["from"]["id"]
                    resp = self._handle_message(message=update["message"])
                elif "callback_query" in update:
                    uid = update["callback_query"]["from"]["id"]
                    cid = update["callback_query"]["id"]
                    resp = self._handle_callback(query=update["callback_query"])

                if type(resp) is not list:
                    resp = [resp]

                for item in resp:
                    try:
                        item.uid = item.uid or uid
                    except AttributeError:
                        pass
                    try:
                        item.cid = item.cid or cid
                    except AttributeError:
                        pass

                    if type(item) is TBot.MessageResponse:
                        self.send_message(item)
                    elif type(item) is TBot.PhotoResponse:
                        self.send_photo(item)
                    elif type(item) is TBot.CallbackResponse:
                        self.answer_callback_query(item)

            except Exception:
                logging.exception("TBot POST response")

    def _handle_message(self, message):
        return None

    def _handle_callback(self, query):
        return None

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
