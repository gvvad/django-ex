from django.db import models
from django.utils import timezone

from .ex.parser import TolokaWebParser
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
    def update_user(cls, user_id, up_date=None, tag_mask=-1):
        r = cls.objects.filter(user_id=user_id)
        if not r:
            cls(
                user_id=user_id,
                tag_mask=tag_mask
            ).save()
        else:
            if r[0].tag_mask != tag_mask:
                r[0].tag_mask = tag_mask
            if up_date:
                r[0].up_date = up_date
            r[0].save()

    @classmethod
    def get_notification_list(cls):
        query = cls.objects.raw("SELECT * "
                              "FROM tolokatbot_tbotchatmodel LEFT JOIN tolokatbot_tbotstoremodel "
                              "ON add_time > up_date")
        res = dict()
        for item in query:
            res.setdefault(item.user_id, []).append(item)
        return res


class TbotStoreModel(models.Model):
    add_time = models.DateTimeField(auto_now_add=True)
    title_a = models.CharField(max_length=256)
    title_b = models.CharField(max_length=256)
    link = models.CharField(max_length=256)
    year = models.IntegerField(default=0)
    poster = models.CharField(max_length=256)
    tag = models.IntegerField(default=-1)

    class Container:
        def __init__(self, title_a="", title_b="", year=0, poster="", link="", tag=-1):
            self.title_a = title_a
            self.title_b = title_b
            self.year = year
            self.poster = poster
            self.link = link
            self.tag = tag

    @staticmethod
    def append_entry(title_a, title_b, link=None, year=None, poster=None, tag=None):
        r = TbotStoreModel.objects.filter(title_a=title_a, title_b=title_b)
        if not r:
            new = TbotStoreModel(
                title_a=title_a or "",
                title_b=title_b or "",
                year=year or 0,
                poster=poster or TolokaWebParser.parse_poster(link),
                link=link or "",
                tag=tag or 0
            )
            new.save()
            return new
        return r[0]

    @staticmethod
    def update_entry(title_a, title_b, link=None, year=None, poster=None, tag=None):
        r = TbotStoreModel.objects.filter(
                title_a=title_a,
                title_b=title_b
        )

        if r:
            if link != None:
                r.link = link
            if year != None:
                r.year = year
            if poster != None:
                r.poster = poster
            if tag != None:
                r.tag = tag
            r.save()

        return r

    @staticmethod
    def _store_posts(items):
        delta = []
        for item in items:
            r = TbotStoreModel.append_entry(title_a=item.title_a,
                                            title_b=item.title_b,
                                            link=item.link,
                                            year=item.year,
                                            tag=item.tag)
            if r:
                delta.append(r)

        return delta

    @staticmethod
    def get_not_earlier(date):
        for item in TbotStoreModel.objects.filter(add_time__gt=date).order_by("-add_time"):
            yield item

    @staticmethod
    def get_last(count=20):
        for item in TbotStoreModel.objects.order_by("-add_time")[:count]:
            yield item

    @staticmethod
    def remove_last(count=200):
        tmp = TbotStoreModel.objects.order_by("-add_time").values_list("id", flat=True)[:count]
        TbotStoreModel.objects.exclude(pk__in=list(tmp)).delete()

    @staticmethod
    def update_posts():
        delta = []
        delta += TbotStoreModel._store_posts(TolokaWebParser.parse_top_hd("2018"))
        delta += TbotStoreModel._store_posts(TolokaWebParser.parse_top_hd("2017"))
        delta += TbotStoreModel._store_posts(TolokaWebParser.parse_top_hd("2016"))

        return delta
