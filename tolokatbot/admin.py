from django.contrib import admin
from .models import TbotChatModel
from .models import TbotStoreModel
#import logging
from .views import tbot


class ChatAdmin(admin.ModelAdmin):
    list_display = ("user_id", "up_date")


def cus_action(self, request, queryset):
    posts = list(queryset)
    for user in TbotChatModel.objects.all():
        for post in posts:
            tbot.send_post(user.user_id, post)


cus_action.short_description = "Delivery to users"


class StoreAdmin(admin.ModelAdmin):
    list_display = ("add_time", "title_a", "title_b", "year")
    list_filter = ("year", "add_time")
    actions = [cus_action]


admin.site.register(TbotChatModel, ChatAdmin)
admin.site.register(TbotStoreModel, StoreAdmin)
