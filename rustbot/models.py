from django.db import models

# Create your models here.
class RusTbotChat(models.Model):
    chat_id = models.CharField(max_length=32)

    @staticmethod
    def store_chat_id(_id):
        RusTbotChat(chat_id=_id).save()

    @staticmethod
    def remove_chat_id(_id):
        RusTbotChat.objects.filter(chat_id=_id).delete()

    @staticmethod
    def is_chat_id(_id):
        try:
            RusTbotChat.objects.get(chat_id=_id)
            return True
        except models.ObjectDoesNotExist:
            return False

    @staticmethod
    def chat_list():
        for item in RusTbotChat.objects.all():
            yield item.chat_id

class RusTbotStore(models.Model):
    up_time = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=256)
    link = models.CharField(max_length=256)
    author = models.CharField(max_length=256)


    @staticmethod
    def store_entry(_title, _link, _author):
        try:
            r = RusTbotStore.objects.get(link=_link)
            if r.title != _title:
                r.title = _title
                r.author = _author
                r.save()
                return True
            return False
        except models.ObjectDoesNotExist:
            RusTbotStore(
                title=_title,
                link=_link,
                author=_author
            ).save()
            return True

    @staticmethod
    def store_entries(items):
        delta = []
        for item in items:
            if RusTbotStore.store_entry(item["title"], item["link"], item["author"]):
                delta.append(item)
        return delta

    @staticmethod
    def get_last(count=20):
        return [{"title": item.title,
                 "link": item.link,
                 "author": item.author,
                 } for item in RusTbotStore.objects.order_by("-up_time")[:count]]
