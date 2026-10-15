from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.decorators import display

from .models import ContactMessage


@admin.action(description="Marcar como leídos")
def mark_as_read(modeladmin, request, queryset):
    queryset.update(is_read=True)


@admin.action(description="Marcar como no leídos")
def mark_as_unread(modeladmin, request, queryset):
    queryset.update(is_read=False)


@admin.register(ContactMessage)
class ContactMessageAdmin(ModelAdmin):
    list_display = ("name", "email", "subject", "read_badge", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("name", "email", "subject", "message")
    readonly_fields = ("name", "email", "phone", "subject", "message", "ip_address", "created_at")
    actions = [mark_as_read, mark_as_unread]

    fieldsets = (
        ("Remitente", {"fields": ("name", "email", "phone", "ip_address")}),
        ("Mensaje", {"fields": ("subject", "message", "is_read", "created_at")}),
    )

    @display(
        description="Estado",
        label={
            True: "success",
            False: "warning",
        },
    )
    def read_badge(self, obj):
        return "Leído" if obj.is_read else "Nuevo"

    def has_add_permission(self, request):
        return False
