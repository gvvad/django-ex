# import telegram
import json
import logging
import re
import io
import time
from telegram import *
from telegram.error import *
from .webparser import WebParser
from threading import Thread, Event


class TBot:
    token = None
    bot = None

    class MessageResponse:
        def __init__(self, text, uid=None, reply_markup: [ReplyKeyboardMarkup, InlineKeyboardMarkup, None]=None, parse_mode=ParseMode.HTML, no_notif=False):
            self.reply_markup = reply_markup
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
        def __init__(self, caption, photo, uid=None, reply_markup: [ReplyKeyboardMarkup, InlineKeyboardMarkup, None]=None, parse_mode=ParseMode.HTML, no_notif=False):
            self.uid = uid
            self.reply_markup = reply_markup
            self.caption = caption
            self.photo = photo
            self.no_notif = no_notif
            self.parse_mode = parse_mode

        def is_photo_url(self):
            return isinstance(self.photo, str) and re.search("^https?:", self.photo)

    def __init__(self, token):
        if not token:
            raise InvalidToken
        self.token = token
        self.bot = Bot(token=token)

    def send(self,
             resp: [CallbackResponse, PhotoResponse, MessageResponse],
             uid: [int, None]=None,
             cid: [int, None]=None,
             attempt=3
             ) -> [Message, bool]:
        """
        Send message to user|chat
        :param resp: Response object
        :param uid: Default uid
        :param cid: Default cid
        """
        while attempt > 0:
            try:
                if isinstance(resp, self.MessageResponse):
                    resp.uid = resp.uid or uid
                    return self.send_message(resp)
                elif isinstance(resp, self.PhotoResponse):
                    resp.uid = resp.uid or uid
                    return self.send_photo(resp)
                elif isinstance(resp, self.CallbackResponse):
                    resp.cid = resp.cid or cid
                    return self.answer_callback_query(resp)
            except TimedOut as e:
                logging.debug("send Timed Out attempt:{}".format(attempt))
                attempt -= 1
                if attempt == 0:
                    raise e

        return False

    def send_message(self, resp: MessageResponse) -> Message:
        """
        Send message
        :param resp: MessageResponse
        :return:
        """
        return self.bot.send_message(
            chat_id=resp.uid,
            text=resp.text,
            parse_mode=resp.parse_mode,
            reply_markup=resp.reply_markup,
            disable_notification=resp.no_notif
        )

    def send_photo(self, resp: PhotoResponse) -> Message:
        """
        Send photo
        :param resp: PhotoResponse
        :return:
        """
        try:
            return self.bot.send_photo(
                chat_id=resp.uid,
                photo=resp.photo,
                caption=resp.caption,
                parse_mode=resp.parse_mode,
                disable_notification=resp.no_notif,
                timeout=50)
        except BadRequest as e:
            if resp.is_photo_url():
                content = WebParser.sync_request(resp.photo)
                if not content:
                    raise e
                with io.BytesIO(content) as file:
                    return self.bot.send_photo(
                        chat_id=resp.uid,
                        photo=file,
                        caption=resp.caption,
                        parse_mode=resp.parse_mode,
                        disable_notification=resp.no_notif,
                        timeout=50)
            else:
                raise e

    def answer_callback_query(self, resp: CallbackResponse) -> bool:
        """
        Answer to callback
        :param resp:
        :return:
        """
        return self.bot.answer_callback_query(
            callback_query_id=resp.cid,
            text=resp.text,
            show_alert=resp.alert,
            url=resp.url)

    def _handle_request(self, request):
        """
        Helper for handle_request
        """
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

                if not resp:
                    return

                if not isinstance(resp, list):
                    resp = [resp]
                for item in resp:
                    self.send(item, uid=uid, cid=cid)

            except Exception as e:
                logging.exception("TBot POST response", e)

    def handle_request(self, request, is_async=True):
        """
        Handle http request
        :param request: http request
        :param is_async: run in thread
        """
        if is_async:
            Thread(target=self._handle_request, args=(request,)).start()
        else:
            self._handle_request(request)

    def _handle_message(self, message) -> [CallbackResponse, MessageResponse, PhotoResponse, None]:
        return None

    def _handle_callback(self, query) -> [CallbackResponse, MessageResponse, PhotoResponse, None]:
        return None

    def set_webhook_url(self, url, cert_file_path=None, attempt: int=1):
        """
        Set web hook url
        :param url: url in url format
        :param cert_file_path:
        :param attempt: count of attempts
        :return:
        """
        while attempt > 0:
            try:
                try:
                    if not cert_file_path:
                        raise FileNotFoundError
                    with open(cert_file_path, "rb") as cert_file:
                        return self.bot.setWebhook(url, cert_file)
                except FileNotFoundError:
                    return self.bot.setWebhook(url)
            except RetryAfter as e:
                time.sleep(round(e.retry_after))
            except (TimedOut, NetworkError):
                attempt -= 1
                logging.info("set webhook time out, attempts left:{}".format(attempt))
                if attempt > 0:
                    time.sleep(5)

        raise TimedOut()

    def delete_webhook_url(self):
        """
        Remove web hook
        """
        self.bot.deleteWebhook()
