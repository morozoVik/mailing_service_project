from django.contrib import admin

from .models import Client, Mailing, MailingAttempt, Message


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("email", "full_name", "owner", "comment")
    list_filter = ("owner",)
    search_fields = ("email", "full_name")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("subject", "owner", "body_preview")
    list_filter = ("owner",)
    search_fields = ("subject", "body")

    def body_preview(self, obj):
        return obj.body[:50] + "..." if len(obj.body) > 50 else obj.body

    body_preview.short_description = "Превью тела"


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "status",
        "start_time",
        "end_time",
        "owner",
        "message_subject",
    )
    list_filter = ("status", "owner", "start_time")
    filter_horizontal = ("clients",)

    def message_subject(self, obj):
        return obj.message.subject

    message_subject.short_description = "Тема сообщения"


@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    list_display = ("mailing", "attempt_time", "status", "server_response_preview")
    list_filter = ("status", "attempt_time")
    readonly_fields = ("attempt_time",)

    def server_response_preview(self, obj):
        return (
            obj.server_response[:50] + "..."
            if len(obj.server_response) > 50
            else obj.server_response
        )

    server_response_preview.short_description = "Ответ сервера"
