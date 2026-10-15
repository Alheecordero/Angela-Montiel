from django.db import models


class ContactMessage(models.Model):
    name = models.CharField("Nombre", max_length=120)
    email = models.EmailField("Correo electrónico")
    phone = models.CharField("Teléfono", max_length=30, blank=True)
    subject = models.CharField("Asunto", max_length=200)
    message = models.TextField("Mensaje")
    is_read = models.BooleanField("Leído", default=False)
    ip_address = models.GenericIPAddressField("Dirección IP", null=True, blank=True)
    created_at = models.DateTimeField("Recibido", auto_now_add=True)

    class Meta:
        verbose_name = "Mensaje de contacto"
        verbose_name_plural = "Mensajes de contacto"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} — {self.subject}"
