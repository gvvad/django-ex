from django.db import models
from django.utils import timezone


class UserModel(models.Model):
    user_id = models.CharField(max_length=32, unique=True)
    up_date = models.DateTimeField(auto_now_add=True)

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
    def set_up_date(cls, user_id, date=timezone.now()):
        r = cls.objects.filter(user_id=user_id)
        if r:
            r[0].up_date = date
            r[0].save()

    @classmethod
    def remove_user(cls, user_id):
        cls.objects.filter(user_id=user_id).delete()

    @classmethod
    def user_list(cls):
        for item in cls.objects.all():
            yield item
