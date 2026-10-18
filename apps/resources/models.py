"""Recursos (capítulo 9.2 de las especificaciones). Glosario y guías."""

import unicodedata

from django.db import models

from apps.core.validators import TEXTO_LARGO, TEXTO_VISIBLE


def normalizar(texto):
    """Minúsculas y sin tildes, para el buscador del glosario."""
    nfd = unicodedata.normalize("NFD", texto or "")
    return "".join(ch for ch in nfd if unicodedata.category(ch) != "Mn").lower().strip()


class GlossaryTerm(models.Model):
    term = models.CharField("Término", max_length=120, unique=True, validators=TEXTO_VISIBLE)
    definition = models.TextField("Definición", validators=TEXTO_LARGO)
    search_key = models.CharField("Clave de búsqueda", max_length=1200, editable=False, blank=True)
    order = models.PositiveSmallIntegerField("Orden", default=0)

    class Meta:
        verbose_name = "Término del glosario"
        verbose_name_plural = "Glosario"
        ordering = ["term"]

    def __str__(self):
        return self.term

    def save(self, *args, **kwargs):
        self.search_key = normalizar(f"{self.term} {self.definition}")[:1200]
        super().save(*args, **kwargs)


class GuideStatus(models.TextChoices):
    SOON = "proximamente", "Próximamente (se muestra sin descarga)"
    PUBLISHED = "publicada", "Publicada"
    HIDDEN = "oculta", "Oculta"


class Guide(models.Model):
    title = models.CharField("Título", max_length=160, validators=TEXTO_VISIBLE)
    description = models.TextField("Descripción", validators=TEXTO_VISIBLE)
    file = models.FileField("Archivo PDF", upload_to="guias/", blank=True)
    status = models.CharField("Estado", max_length=20, choices=GuideStatus.choices, default=GuideStatus.SOON)
    figures = models.ManyToManyField("practice.PracticeFigure", related_name="guides", blank=True, verbose_name="Figuras relacionadas")
    order = models.PositiveSmallIntegerField("Orden", default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Guía descargable"
        verbose_name_plural = "Guías descargables"
        ordering = ["order", "title"]

    def __str__(self):
        return self.title

    @property
    def is_downloadable(self):
        return self.status == GuideStatus.PUBLISHED and bool(self.file)
