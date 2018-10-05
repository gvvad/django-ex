from django.contrib import admin
from .models import RusTbotChat
from .models import RusTbotStore


class ChatAdmin(admin.ModelAdmin):
    list_display = ("user_id", )


class StoreAdmin(admin.ModelAdmin):
    list_display = ("up_time", "title", "author")
    list_filter = ("up_time", )


admin.site.register(RusTbotChat, ChatAdmin)
admin.site.register(RusTbotStore, StoreAdmin)
