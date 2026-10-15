from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.decorators import display

from .models import Subscriber


@admin.action(description="Activar suscriptores")
def activate_subscribers(modeladmin, request, queryset):
    queryset.update(is_active=True)


@admin.action(description="Desactivar suscriptores")
def deactivate_subscribers(modeladmin, request, queryset):
    queryset.update(is_active=False)


@admin.register(Subscriber)
class SubscriberAdmin(ModelAdmin):
    list_display = ("email", "active_badge", "subscribed_at")
    list_filter = ("is_active", "subscribed_at")
    search_fields = ("email",)
    readonly_fields = ("unsubscribe_token", "subscribed_at")
    actions = [activate_subscribers, deactivate_subscribers]

    @display(
        description="Estado",
        label={
            True: "success",
            False: "warning",
        },
    )
    def active_badge(self, obj):
        return "Activo" if obj.is_active else "Inactivo"
