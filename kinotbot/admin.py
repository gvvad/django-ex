from django.contrib import admin
from .models import TbotChatModel
from .models import TbotStoreModel


class ChatAdmin(admin.ModelAdmin):
    list_display = ("chat_id", "notif_date")


class StoreAdmin(admin.ModelAdmin):
    list_display = ("up_time", "title_en", "title_ru", "year")
    list_filter = ("year", "up_time")


admin.site.register(TbotChatModel, ChatAdmin)
admin.site.register(TbotStoreModel, StoreAdmin)
