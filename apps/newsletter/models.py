import secrets

from django.db import models
from django.utils import timezone


def generate_token():
    return secrets.token_urlsafe(32)


class Subscriber(models.Model):
    email = models.EmailField("Correo electrónico", unique=True)
    is_active = models.BooleanField("Activo", default=False, help_text="Se activa al confirmar el correo.")
    subscribed_at = models.DateTimeField("Fecha de solicitud", auto_now_add=True)

    consent_at = models.DateTimeField("Fecha del consentimiento", null=True, blank=True)
    consent_text = models.CharField("Texto del consentimiento aceptado", max_length=300, blank=True)
    consent_ip = models.GenericIPAddressField("IP del consentimiento", null=True, blank=True)

    confirm_token = models.CharField("Token de confirmación", max_length=64, unique=True, default=generate_token, editable=False)
    confirmed_at = models.DateTimeField("Fecha de confirmación", null=True, blank=True)
    unsubscribe_token = models.CharField("Token de baja", max_length=64, unique=True, default=generate_token, editable=False)
    unsubscribed_at = models.DateTimeField("Fecha de baja", null=True, blank=True)

    class Meta:
        verbose_name = "Suscriptor"
        verbose_name_plural = "Suscriptores"
        ordering = ["-subscribed_at"]

    def __str__(self):
        return self.email

    @property
    def is_confirmed(self):
        return self.confirmed_at is not None

    def confirm(self):
        self.confirmed_at = timezone.now()
        self.is_active = True
        self.unsubscribed_at = None
        self.save(update_fields=["confirmed_at", "is_active", "unsubscribed_at"])

    def unsubscribe(self):
        self.is_active = False
        self.unsubscribed_at = timezone.now()
        self.save(update_fields=["is_active", "unsubscribed_at"])
