from django.db import models
from django.utils import timezone
from .ex.kinoparser import KinoWebParser


class TbotChatModel(models.Model):
    chat_id = models.CharField(max_length=32, unique=True)
    notif_date = models.DateTimeField(auto_now_add=True)
    tag_mask = models.IntegerField(default=-1)


    @staticmethod
    def is_chat_id(_id):
        return bool(TbotChatModel.objects.filter(chat_id=_id))

    @staticmethod
    def get_tag_mask(user_id):
        r = TbotChatModel.objects.filter(user_id=user_id)
        if r:
            return r[0].tag_mask
        return None

    @staticmethod
    def get_notif_date(user_id):
        r = TbotChatModel.objects.filter(user_id=user_id)
        if r:
            return r[0].notif_date

    @staticmethod
    def notif_user(user_id):
        r = TbotChatModel.objects.filter(chat_id=user_id)
        if r:
            r[0].chat_id = timezone.now()
            r[0].save()

    @staticmethod
    def update_chat_id(chat_id, notif_date=None, tag_mask=-1):
        r = TbotChatModel.objects.filter(chat_id=chat_id)
        if not r:
            TbotChatModel(
                chat_id=chat_id,
                tag_mask=tag_mask
            ).save()
        else:
            if r[0].tag_mask != tag_mask:
                r[0].tag_mask = tag_mask
            if notif_date:
                r[0].notif_date = notif_date
            r[0].save()

    @staticmethod
    def remove_chat_id(_id):
        TbotChatModel.objects.filter(chat_id=_id).delete()

    @staticmethod
    def chat_list():
        for item in TbotChatModel.objects.all():
            yield item

class TbotStoreModel(models.Model):
    up_time = models.DateTimeField(auto_now=True)
    title_en = models.CharField(max_length=256)
    title_ru = models.CharField(max_length=256)
    link = models.CharField(max_length=256)
    year = models.IntegerField(default=0)
    poster = models.CharField(max_length=256)
    tag = models.IntegerField(default=-1)

    class Container:
        def __init__(self, title_ru="", title_en="", year=0, poster="", link="", tag=-1):
            self.title_en = title_en
            self.title_ru = title_ru
            self.year = year
            self.poster = poster
            self.link = link
            self.tag = tag

    @staticmethod
    def update_entry(title_ru="", title_en="", year=0, poster="", link="", tag=-1):
        r = TbotStoreModel.objects.filter(title_ru=title_ru, title_en=title_en)
        if not r:
            TbotStoreModel(
                title_ru=title_ru,
                title_en=title_en,
                year=year,
                poster=poster,
                link=link,
                tag=tag
            ).save()
            return True
        else:
            pass
            '''
            if r[0].title_ru != title_ru and r[0].title_en != title_en:
                r[0].title_ru = title_ru
                r[0].title_en = title_en
                r[0].year = year
                r[0].poster = poster
                r[0].link = link
                r[0].tag = tag
                r[0].save()
            '''
        return False

    @staticmethod
    def _store_entries(items, tag=-1):
        delta = []
        for item in items:
            if TbotStoreModel.update_entry(title_ru=item.title_ru,
                                           title_en=item.title_en,
                                           year=item.year,
                                           poster=item.poster,
                                           link=item.link,
                                           tag=tag):
                delta.append(TbotStoreModel.Container(title_ru=item.title_ru,
                                                      title_en=item.title_en,
                                                      year=item.year,
                                                      poster=item.poster,
                                                      link=item.link,
                                                      tag=tag))

        return delta

    @staticmethod
    def get_last(count=20, not_earlier=None):
        if not_earlier:
            for item in TbotStoreModel.objects.filter(up_time__gt=not_earlier).order_by("-up_time"):
                yield item
        else:
            for item in TbotStoreModel.objects.order_by("-up_time")[:count]:
                yield item

    @staticmethod
    def remove_last(count=200):
        TbotStoreModel.objects.order_by("-up_time")[count:].delete()

    @staticmethod
    def update():
        a = TbotStoreModel._store_entries(KinoWebParser.parse_top(), 1)
        return a
