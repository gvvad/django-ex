from django.contrib import admin
from .models import TbotChatModel
from .models import TbotStoreModel


class ChatAdmin(admin.ModelAdmin):
    list_display = ("user_id", "up_date")


class StoreAdmin(admin.ModelAdmin):
    list_display = ("add_time", "title_a", "title_b", "year")
    list_filter = ("year", "add_time")


admin.site.register(TbotChatModel, ChatAdmin)
admin.site.register(TbotStoreModel, StoreAdmin)
