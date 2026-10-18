from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.decorators import display

from .models import Subscriber


@admin.action(description="Dar de baja")
def deactivate(modeladmin, request, queryset):
    for subscriber in queryset:
        subscriber.unsubscribe()


@admin.register(Subscriber)
class SubscriberAdmin(ModelAdmin):
    list_display = ("email", "state_badge", "subscribed_at", "confirmed_at", "consent_at")
    list_filter = ("is_active", "subscribed_at")
    search_fields = ("email",)
    readonly_fields = ("subscribed_at", "consent_at", "consent_text", "consent_ip", "confirmed_at", "unsubscribed_at", "confirm_token", "unsubscribe_token")
    actions = [deactivate]
    fieldsets = (
        ("Suscriptor", {"fields": ("email", "is_active", "subscribed_at")}),
        ("Consentimiento", {"fields": ("consent_at", "consent_text", "consent_ip", "confirmed_at", "unsubscribed_at")}),
        ("Tokens", {"fields": ("confirm_token", "unsubscribe_token"), "classes": ("collapse",)}),
    )

    def has_add_permission(self, request):
        return False

    @display(description="Estado", label={"Confirmado": "success", "Pendiente": "warning", "Baja": "danger"})
    def state_badge(self, obj):
        if obj.is_active:
            return "Confirmado"
        if obj.unsubscribed_at:
            return "Baja"
        return "Pendiente"
