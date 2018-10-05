from django.db import models
from .ex.tbparser import RustorkaWebParser
from project.modules.model import UserModel


class RusTbotChat(UserModel):
    tag_mask = models.IntegerField(default=-1)

    @classmethod
    def get_tag_mask(cls, user_id):
        r = cls.objects.filter(user_id=user_id)
        if r:
            return r.tag_mask
        return None

    @classmethod
    def update_user_id(cls, user_id, tag_mask=-1):
        r = cls.objects.filter(user_id=user_id)
        if not r:
            cls(
                user_id=user_id,
                tag_mask=tag_mask
            ).save()
            return True
        else:
            if r[0].tag_mask != tag_mask:
                r[0].tag_mask = tag_mask
                r[0].save()
                return True
            return False


class RusTbotStore(models.Model):
    up_time = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=256)
    link = models.CharField(max_length=256)
    author = models.CharField(max_length=256)
    tag = models.IntegerField(default=-1)
    poster = models.TextField(max_length=256, default="")

    class Container:
        def __init__(self, title="", link="", author="", tag=-1, poster=""):
            self.title = title
            self.link = link
            self.author = author
            self.tag = tag
            self.poster = poster

    @classmethod
    def is_entry_exist(cls, _link) -> bool:
        r = cls.objects.filter(link=_link)
        return bool(r)

    @classmethod
    def store_entry(cls, _title, _link, _author, _tag=None, poster=""):
        r = cls.objects.filter(link=_link)
        if not r:
            cls(
                title=_title,
                link=_link,
                author=_author,
                tag=_tag,
                poster=poster
            ).save()
            return True
        else:
            if r[0].title != _title:
                r[0].title = _title
                r[0].save()
                return True
            return False

    @classmethod
    def _store_entries(cls, items, tag=-1):
        delta = []
        for item in items:
            if not cls.is_entry_exist(item["link"]):
                item["poster"] = RustorkaWebParser.parse_poster(item["link"]) or ""

                if cls.store_entry(item["title"], item["link"], item["author"], _tag=tag, poster=item["poster"]):
                    delta.append(RusTbotStore.Container(title=item["title"],
                                                        link=item["link"],
                                                        author=item["author"],
                                                        tag=tag,
                                                        poster=item["poster"]))
        return delta

    @staticmethod
    def get_last(count=20):
        for item in RusTbotStore.objects.order_by("-up_time")[:count]:
            yield item

    @staticmethod
    def remove_last(count=200):
        tmp = RusTbotStore.objects.order_by("-up_time").values_list("id", flat=True)[:count]
        RusTbotStore.objects.exclude(pk__in=list(tmp)).delete()

    @staticmethod
    def update():
        b = RusTbotStore._store_entries(RustorkaWebParser.get_hot_news()[::-1], 2)
        a = RusTbotStore._store_entries(RustorkaWebParser.get_hot()[::-1], 1)
        return a + b
