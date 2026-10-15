import secrets

from django.db import models


def generate_unsubscribe_token():
    return secrets.token_urlsafe(32)


class Subscriber(models.Model):
    email = models.EmailField("Correo electrónico", unique=True)
    is_active = models.BooleanField("Activo", default=True)
    subscribed_at = models.DateTimeField("Fecha de suscripción", auto_now_add=True)
    unsubscribe_token = models.CharField(
        "Token de baja",
        max_length=64,
        unique=True,
        default=generate_unsubscribe_token,
        editable=False,
    )

    class Meta:
        verbose_name = "Suscriptor"
        verbose_name_plural = "Suscriptores"
        ordering = ["-subscribed_at"]

    def __str__(self):
        return self.email
