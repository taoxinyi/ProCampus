from django.contrib import admin

from chat.models import ChatRoomGroup, ChatHistory


class ChatInline(admin.TabularInline):
    model = ChatHistory


class ChatRoomAdmin(admin.ModelAdmin):
    inlines = [
        ChatInline,
    ]


admin.site.register(ChatRoomGroup, ChatRoomAdmin)
