from django.db import models
from django.utils import timezone
import logging


class UserModel(models.Model):
    user_id = models.CharField(max_length=32, unique=True)
    up_date = models.DateTimeField(auto_now_add=True)
    awaiting = models.TextField(default="")

    class Meta:
        abstract = True

    @classmethod
    def is_user(cls, user_id):
        return bool(cls.objects.filter(user_id=user_id))

    @classmethod
    def get_up_date(cls, user_id):
        r = cls.objects.filter(user_id=user_id)
        if r:
            return r[0].up_date

    @classmethod
    def set_awaiting(cls, user_id, data):
        r = cls.objects.filter(user_id=user_id)
        if r:
            r[0].awaiting = data
            r[0].save()

    @classmethod
    def handle_awaiting(cls, user_id):
        r = cls.objects.filter(user_id=user_id)
        if r:
            res = r[0].awaiting
            r[0].awaiting = ""
            r[0].save()
            return res

        return None

    @classmethod
    def set_up_date(cls, user_id, date=timezone.now()):
        r = cls.objects.filter(user_id=user_id)
        if r:
            logging.debug("set up_date {}".format(date.strftime("%Y-%m-%d %H:%M")))
            r[0].up_date = date
            r[0].save()

    @classmethod
    def remove_user(cls, user_id):
        cls.objects.filter(user_id=user_id).delete()

    @classmethod
    def user_list(cls):
        for item in cls.objects.all():
            yield item
