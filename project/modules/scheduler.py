import logging
from threading import Thread, Event
import threading
import os


class Scheduler:
    """
    Loop-call function in new thread
    """
    thread = None
    sleep_time = None
    handler = None
    event = None

    def __init__(self, handler, sleep_time=60, start=False, is_daemon=False):
        """
        Scheduler constructor
        :param handler: Function
        :param sleep_time: Delay time in seconds
        :param start: Start automatically
        :param is_daemon: Is daemon
        """
        self.handler = handler
        self.sleep_time = sleep_time
        self.thread = Thread(target=self._worker, daemon=is_daemon, name="Some scheduler daemon")
        self.event = Event()

        if start:
            self.thread.start()

    def set_time(self, new_time=None):
        if new_time:
            self.sleep_time = new_time

    def set_mtime(self, new_mtime):
        self.set_time(new_mtime * 60)

    def _worker(self):
        while True:
            try:
                self.handler()
            except Exception:
                logging.exception("Scheduler")
            if self.event.wait(timeout=self.sleep_time):
                break

    def start(self):
        if self.thread:
            self.thread.start()

    def stop(self):
        if self.thread:
            self.event.set()
