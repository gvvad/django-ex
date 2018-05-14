from django.db import models
from .ex.tbparser import RustorkaWebParser


class RusTbotChat(models.Model):
    chat_id = models.CharField(max_length=32, unique=True)
    tag_mask = models.IntegerField(default=-1)


    @staticmethod
    def is_chat_id(_id):
        return bool(RusTbotChat.objects.filter(chat_id=_id))

    @staticmethod
    def get_tag_mask(user_id):
        r = RusTbotChat.objects.filter(user_id=user_id)
        if r:
            return r.tag_mask
        return None

    @staticmethod
    def update_chat_id(chat_id, tag_mask=-1):
        r = RusTbotChat.objects.filter(chat_id=chat_id)
        if not r:
            RusTbotChat(
                chat_id=chat_id,
                tag_mask=tag_mask
            ).save()
            return True
        else:
            if r[0].tag_mask != tag_mask:
                r[0].tag_mask = tag_mask
                r[0].save()
                return True
            return False

    @staticmethod
    def remove_chat_id(_id):
        RusTbotChat.objects.filter(chat_id=_id).delete()

    @staticmethod
    def chat_list():
        for item in RusTbotChat.objects.all():
            yield item

class RusTbotStore(models.Model):
    up_time = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=256)
    link = models.CharField(max_length=256)
    author = models.CharField(max_length=256)
    tag = models.IntegerField(default=-1)

    class Container:
        def __init__(self, title="", link="", author="", tag=-1):
            self.title = title
            self.link = link
            self.author = author
            self.tag = tag


    @staticmethod
    def store_entry(_title, _link, _author, _tag=None):
        r = RusTbotStore.objects.filter(link=_link)
        if not r:
            RusTbotStore(
                title=_title,
                link=_link,
                author=_author,
                tag=_tag
            ).save()
            return True
        else:
            if r[0].title != _title:
                r[0].title = _title
                r[0].save()
                return True
            return False

    @staticmethod
    def _store_entries(items, tag=-1):
        delta = []
        for item in items:
            if RusTbotStore.store_entry(item["title"], item["link"], item["author"], _tag=tag):
                delta.append(RusTbotStore.Container(title=item["title"],
                                                    link=item["link"],
                                                    author=item["author"],
                                                    tag=tag
                                                    ))
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
