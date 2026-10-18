"""Publicaciones (capítulo 8 de las especificaciones)."""

import math
import re

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.text import slugify

from apps.core.models import PublishStatus, PublishedQuerySet
from apps.core.validators import TEXTO_LARGO, TEXTO_VISIBLE

PALABRAS_POR_MINUTO = 200
IMAGEN_MIN_ANCHO = 1200
IMAGEN_MIN_ALTO = 630


class PublicationFormat(models.TextChoices):
    NOTA = "nota", "Nota jurídica"
    ANALISIS = "analisis", "Análisis"
    GUIA = "guia", "Guía empresarial"
    CONSULTA = "consulta", "Consulta de la semana"
    CIERRE = "cierre", "Cierre del año"


FORMAT_DESCRIPTIONS = {
    "todas": "Todo lo publicado, del más reciente al más antiguo.",
    PublicationFormat.NOTA: "Reacción breve, en 24 a 48 horas, a una ley, una circular del SII o un fallo, con el hecho y su efecto para tu empresa.",
    PublicationFormat.ANALISIS: "Una pieza de mayor profundidad con mi postura sobre un tema.",
    PublicationFormat.GUIA: "Contenido de consulta para guardar y revisar con tu asesor.",
    PublicationFormat.CONSULTA: "La respuesta a una pregunta real, anonimizada.",
    PublicationFormat.CIERRE: "Cada diciembre, las decisiones societarias que conviene revisar antes del cierre.",
}


def validar_imagen_social(image):
    if not image:
        return
    width = getattr(image, "width", None)
    height = getattr(image, "height", None)
    if width and height and (width < IMAGEN_MIN_ANCHO or height < IMAGEN_MIN_ALTO):
        raise ValidationError(
            f"La imagen debe medir al menos {IMAGEN_MIN_ANCHO} por {IMAGEN_MIN_ALTO} px. La actual mide {width} por {height}."
        )


class Publication(models.Model):
    title = models.CharField("Título", max_length=200, validators=TEXTO_VISIBLE, help_text="Es el H1 y la etiqueta title. Sin dos puntos.")
    slug = models.SlugField("URL", unique=True, max_length=220, help_text="Se completa desde el título. Puedes editarla antes de publicar.")
    format = models.CharField("Formato", max_length=20, choices=PublicationFormat.choices)
    areas = models.ManyToManyField("practice.PracticeArea", related_name="publications", verbose_name="Área")
    figures = models.ManyToManyField(
        "practice.PracticeFigure",
        related_name="publications",
        blank=True,
        verbose_name="Etiquetas de figura",
        help_text="La publicación aparece en el bloque de relacionadas de cada figura marcada.",
    )

    lead = models.CharField("Bajada", max_length=240, validators=TEXTO_VISIBLE, help_text="Dos líneas bajo el título. Es también la meta descripción.")
    summary = models.TextField("En breve", validators=TEXTO_LARGO, help_text="Respuesta directa al inicio, de tres o cuatro líneas.")
    body = models.TextField("Cuerpo", validators=TEXTO_LARGO, help_text="Con títulos H2, citas numeradas y frase destacada opcional.")
    highlight = models.CharField("Frase destacada", max_length=240, blank=True, validators=TEXTO_VISIBLE, help_text="Se muestra en la tarjeta destacada del índice.")

    tax_block = models.TextField("Y en lo tributario…", blank=True, validators=TEXTO_LARGO, help_text="Bloque fijo cuando el tema tiene efecto tributario.")
    ley = models.TextField("La ley", blank=True, validators=TEXTO_LARGO)
    criterio = models.TextField("Mi criterio", blank=True, validators=TEXTO_LARGO)
    riesgo = models.TextField("El riesgo", blank=True, validators=TEXTO_LARGO)

    image = models.ImageField("Imagen", upload_to="publicaciones/", validators=[validar_imagen_social], help_text="Para redes y datos estructurados. Mínimo 1200 por 630 px.")
    image_alt = models.CharField("Texto alternativo de la imagen", max_length=200, validators=TEXTO_VISIBLE)

    status = models.CharField("Estado", max_length=20, choices=PublishStatus.choices, default=PublishStatus.DRAFT)
    published_at = models.DateTimeField("Fecha de publicación", default=timezone.now)
    content_updated_at = models.DateField("Fecha de actualización", default=timezone.localdate, help_text="Cámbiala cada vez que edites el contenido.")
    verified_at = models.DateField("Fecha de verificación", default=timezone.localdate)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PublishedQuerySet.as_manager()

    class Meta:
        verbose_name = "Publicación"
        verbose_name_plural = "Publicaciones"
        ordering = ["-published_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:220]
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("publications:detail", kwargs={"slug": self.slug})

    @property
    def is_published(self):
        return self.status == PublishStatus.PUBLISHED and self.published_at <= timezone.now()

    @property
    def format_label(self):
        return self.get_format_display()

    @property
    def meta_title(self):
        return f"{self.title} | Ángela Montiel"

    @property
    def reading_time(self):
        text = " ".join(strip_tags(part or "") for part in (self.summary, self.body, self.tax_block, self.ley, self.criterio, self.riesgo))
        words = len(re.findall(r"\w+", text))
        return max(1, math.ceil(words / PALABRAS_POR_MINUTO))

    @property
    def has_ley_criterio_riesgo(self):
        return bool(self.ley or self.criterio or self.riesgo)

    @property
    def area_names(self):
        return " y ".join(area.name for area in self.areas.all())

    @property
    def area_short_names(self):
        return " · ".join(area.short_name for area in self.areas.all())

    def related(self, limit=3):
        qs = Publication.objects.published().exclude(pk=self.pk)
        figure_ids = list(self.figures.values_list("id", flat=True))
        if figure_ids:
            by_figure = list(qs.filter(figures__in=figure_ids).distinct()[:limit])
            if len(by_figure) >= limit:
                return by_figure
            rest = qs.exclude(pk__in=[p.pk for p in by_figure]).filter(areas__in=self.areas.all()).distinct()[: limit - len(by_figure)]
            return by_figure + list(rest)
        return list(qs.filter(areas__in=self.areas.all()).distinct()[:limit])

    def related_videos(self, limit=2):
        from apps.videos.models import Video

        qs = Video.objects.published()
        figure_ids = list(self.figures.values_list("id", flat=True))
        if figure_ids:
            return list(qs.filter(figures__in=figure_ids).distinct()[:limit])
        return list(qs.filter(area__in=self.areas.all())[:limit])

    @classmethod
    def latest_nota(cls):
        return cls.objects.published().filter(format=PublicationFormat.NOTA).first()


class Source(models.Model):
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE, related_name="sources")
    order = models.PositiveSmallIntegerField("Orden", default=0)
    text = models.CharField("Fuente", max_length=300, validators=TEXTO_LARGO, help_text="Norma, artículo y versión vigente, o circular, oficio o fallo con su número y fecha.")
    url = models.URLField("Enlace oficial", help_text="LeyChile, SII, Poder Judicial u otra fuente oficial.")

    class Meta:
        verbose_name = "Fuente"
        verbose_name_plural = "Fuentes"
        ordering = ["order", "id"]

    def __str__(self):
        return self.text
