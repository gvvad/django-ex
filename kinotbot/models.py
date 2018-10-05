from django.db import models
from django.db import transaction
# from django.utils import timezone
from .ex.kinoparser import KinoWebParser
from project.modules.model import UserModel


class TbotChatModel(UserModel):
    tag_mask = models.IntegerField(default=-1)

    @classmethod
    def get_tag_mask(cls, user_id):
        r = cls.objects.filter(user_id=user_id)
        if r:
            return r[0].tag_mask
        return None

    @classmethod
    def update_chat_id(cls, user_id, notif_date=None, tag_mask=-1):
        r = TbotChatModel.objects.filter(user_id=user_id)
        if not r:
            cls(
                user_id=user_id,
                tag_mask=tag_mask
            ).save()
        else:
            if r[0].tag_mask != tag_mask:
                r[0].tag_mask = tag_mask
            if notif_date:
                r[0].notif_date = notif_date
            r[0].save()


class TbotStoreModel(models.Model):
    up_time = models.DateTimeField(auto_now=True)
    title_en = models.CharField(max_length=256)
    title_ru = models.CharField(max_length=256)
    link = models.CharField(max_length=256)
    year = models.IntegerField(default=0)
    poster = models.CharField(max_length=256)
    tag = models.IntegerField(default=-1)

    class EntryExistException(Exception):
        pass

    class Container:
        def __init__(self, title_ru="", title_en="", year=0, poster="", link="", tag=-1):
            self.title_en = title_en
            self.title_ru = title_ru
            self.year = year
            self.poster = poster
            self.link = link
            self.tag = tag

    @classmethod
    @transaction.atomic
    def update_entry(cls, title_ru="", title_en="", year=0, poster="", link="", tag=-1):
        if cls.objects.filter(title_ru=title_ru, title_en=title_en).count() == 0:
            cls(
                title_ru=title_ru,
                title_en=title_en,
                year=year,
                poster=poster,
                link=link,
                tag=tag
            ).save()
            if cls.objects.filter(title_ru=title_ru, title_en=title_en).count() != 1:
                raise cls.EntryExistException
            return True
        '''
        else:
            pass
            if r[0].title_ru != title_ru and r[0].title_en != title_en:
                r[0].title_ru = title_ru
                r[0].title_en = title_en
                r[0].year = year
                r[0].poster = poster
                r[0].link = link
                r[0].tag = tag
                r[0].save()
            '''
        raise cls.EntryExistException

    @classmethod
    def _store_entries(cls, items, tag=-1):
        delta = []
        for item in items:
            try:
                cls.update_entry(title_ru=item.title_ru,
                                 title_en=item.title_en,
                                 year=item.year,
                                 poster=item.poster,
                                 link=item.link,
                                 tag=tag)
                delta.append(cls.Container(title_ru=item.title_ru,
                                           title_en=item.title_en,
                                           year=item.year,
                                           poster=item.poster,
                                           link=item.link,
                                           tag=tag))
            except cls.EntryExistException:
                pass

        return delta

    @staticmethod
    def get_not_earlier(date):
        for item in TbotStoreModel.objects.filter(up_time__gt=date).order_by("-up_time"):
            yield item

    @staticmethod
    def get_last(count=20):
        for item in TbotStoreModel.objects.order_by("-up_time")[:count]:
            yield item

    @staticmethod
    def remove_last(count=500):
        tmp = TbotStoreModel.objects.order_by("-up_time").values_list("id", flat=True)[:count]
        TbotStoreModel.objects.exclude(pk__in=list(tmp)).delete()

    @staticmethod
    def update():
        a = TbotStoreModel._store_entries(KinoWebParser.parse_top(), 1)
        return a
