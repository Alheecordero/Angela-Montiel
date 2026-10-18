"""Áreas de práctica y figuras (capítulo 7 de las especificaciones).

Cada subpágina de figura es un tipo de contenido editable que replica, en
orden, los bloques de la plantilla del prototipo. Los textos jurídicos se
cargan con `importar_prototipo` y no deben reescribirse sin aprobación.
"""

from django.db import models
from django.urls import reverse
from django.utils import timezone

from apps.core.models import PublishStatus, PublishedQuerySet
from apps.core.validators import TEXTO_LARGO, TEXTO_VISIBLE

ROMANOS = ["i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x", "xi", "xii"]


def romano(index):
    return ROMANOS[index] if index < len(ROMANOS) else str(index + 1)


class LegalPageMixin(models.Model):
    """Campos comunes a áreas y figuras."""

    title = models.CharField("Título H1", max_length=220, validators=TEXTO_VISIBLE)
    lead = models.TextField("Bajada", validators=TEXTO_VISIBLE)
    content_updated_at = models.DateField("Fecha de actualización", default=timezone.localdate)

    ley = models.TextField("La ley", blank=True, validators=TEXTO_LARGO)
    criterio = models.TextField("Mi criterio", blank=True, validators=TEXTO_LARGO)
    riesgo = models.TextField("El riesgo", blank=True, validators=TEXTO_LARGO)

    sources = models.TextField("Fuentes", help_text="Normas consultadas, en un párrafo.", validators=TEXTO_LARGO)
    verified_at = models.DateField("Fecha de verificación", default=timezone.localdate)

    closing_question = models.CharField("Pregunta de cierre", max_length=240, validators=TEXTO_VISIBLE)
    whatsapp_message = models.CharField(
        "Mensaje inicial de WhatsApp",
        max_length=200,
        blank=True,
        help_text="Vacío mientras Ángela no apruebe los mensajes. Ejemplo. Hola Ángela, vengo de la página de fusión de sociedades.",
        validators=TEXTO_VISIBLE,
    )

    meta_title = models.CharField("Etiqueta title", max_length=140, validators=[])
    meta_description = models.CharField("Meta descripción", max_length=200)

    status = models.CharField("Estado", max_length=20, choices=PublishStatus.choices, default=PublishStatus.PUBLISHED)
    published_at = models.DateTimeField("Publicada desde", default=timezone.now)
    updated_at = models.DateTimeField("Guardado", auto_now=True)

    objects = PublishedQuerySet.as_manager()

    class Meta:
        abstract = True

    @property
    def has_ley_criterio_riesgo(self):
        return bool(self.ley or self.criterio or self.riesgo)

    @property
    def is_published(self):
        return self.status == PublishStatus.PUBLISHED and self.published_at <= timezone.now()


class PracticeArea(LegalPageMixin):
    slug = models.SlugField("URL", unique=True, max_length=80)
    name = models.CharField("Nombre", max_length=80, validators=TEXTO_VISIBLE)
    short_name = models.CharField("Nombre corto", max_length=40, validators=TEXTO_VISIBLE, help_text="Para filtros y etiquetas, por ejemplo Reorganizaciones.")
    label = models.CharField("Etiqueta superior", max_length=60, validators=TEXTO_VISIBLE, help_text="SERVICIO PRINCIPAL o ÁREA DE PRÁCTICA.")
    is_primary = models.BooleanField("Servicio principal", default=False)
    order = models.PositiveSmallIntegerField("Orden", default=0)

    home_description = models.TextField("Descripción en el inicio", validators=TEXTO_VISIBLE)
    home_cta = models.CharField("Enlace en el inicio", max_length=80, validators=TEXTO_VISIBLE, help_text="Ejemplo. Usar el mapa de reorganizaciones")

    tool_label = models.CharField("Etiqueta de la herramienta", max_length=60, validators=TEXTO_VISIBLE)
    tool_title = models.CharField("Título de la herramienta", max_length=160, validators=TEXTO_VISIBLE)
    tool_intro = models.TextField("Introducción de la herramienta", validators=TEXTO_VISIBLE)
    tool_note = models.TextField("Nota al pie de la herramienta", blank=True, validators=TEXTO_LARGO)

    figures_label = models.CharField("Etiqueta de la lista de figuras", max_length=60, validators=TEXTO_VISIBLE)
    figures_title = models.CharField("Título de la lista de figuras", max_length=160, validators=TEXTO_VISIBLE)

    tax_label = models.CharField("Etiqueta tributaria", max_length=60, default="Y EN LO TRIBUTARIO…", validators=TEXTO_VISIBLE)
    tax_title = models.CharField("Título tributario", max_length=160, validators=TEXTO_VISIBLE)
    tax_text = models.TextField("Texto tributario", help_text="Párrafos separados por una línea en blanco.", validators=TEXTO_LARGO)

    how_label = models.CharField("Etiqueta Cómo trabajo", max_length=60, validators=TEXTO_VISIBLE)

    class Meta:
        verbose_name = "Área de práctica"
        verbose_name_plural = "Áreas de práctica"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("practice:area", kwargs={"slug": self.slug})

    @property
    def tax_paragraphs(self):
        return [p.strip() for p in self.tax_text.split("\n\n") if p.strip()]

    @property
    def published_figures(self):
        return self.figures.published()

    @property
    def has_map(self):
        return self.map_options.exists()

    @property
    def has_comparator(self):
        return self.comparator_rows.exists()

    def breadcrumbs(self):
        return [
            {"name": "Inicio", "url": "/"},
            {"name": "Áreas de práctica", "url": "/#areas"},
            {"name": self.name, "url": self.get_absolute_url()},
        ]


class PracticeFigure(LegalPageMixin):
    area = models.ForeignKey(PracticeArea, on_delete=models.PROTECT, related_name="figures", verbose_name="Área")
    slug = models.SlugField("URL", unique=True, max_length=80)
    name = models.CharField("Nombre", max_length=120, validators=TEXTO_VISIBLE, help_text="Nombre completo, por ejemplo Fusión de sociedades.")
    short_name = models.CharField("Nombre corto", max_length=60, validators=TEXTO_VISIBLE, help_text="Para la ruta de navegación, por ejemplo Fusión.")
    menu_name = models.CharField("Nombre en el menú", max_length=60, validators=TEXTO_VISIBLE)
    card_text = models.TextField("Resumen para tarjetas", validators=TEXTO_VISIBLE, help_text="Se usa en la lista de figuras del área.")
    label = models.CharField("Etiqueta superior", max_length=80, validators=TEXTO_VISIBLE, help_text="Ejemplo. REORGANIZACIONES · FUSIÓN")
    order = models.PositiveSmallIntegerField("Orden", default=0)

    definition_label = models.CharField("Etiqueta de la definición", max_length=80, validators=TEXTO_VISIBLE)
    definition_lead = models.TextField("Definición", help_text="Lo más cercana posible al texto legal.", validators=TEXTO_LARGO)
    definition_body = models.TextField("Desarrollo de la definición", blank=True, help_text="Párrafos separados por una línea en blanco.", validators=TEXTO_LARGO)

    sa = models.TextField("Sociedad anónima", validators=TEXTO_LARGO)
    spa = models.TextField("Sociedad por acciones", validators=TEXTO_LARGO)
    ltda = models.TextField("Sociedad de responsabilidad limitada", validators=TEXTO_LARGO)
    societario_note = models.TextField("Nota societaria", blank=True, validators=TEXTO_LARGO)

    class Meta:
        verbose_name = "Figura"
        verbose_name_plural = "Figuras (subpáginas)"
        ordering = ["area__order", "order", "name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("practice:figure", kwargs={"slug": self.slug})

    @property
    def definition_paragraphs(self):
        return [p.strip() for p in self.definition_body.split("\n\n") if p.strip()]

    def breadcrumbs(self):
        return self.area.breadcrumbs() + [{"name": self.short_name, "url": self.get_absolute_url()}]

    def related_publications(self, limit=3):
        from apps.publications.models import Publication

        return Publication.objects.published().filter(figures=self).distinct()[:limit]

    def related_videos(self, limit=3):
        from apps.videos.models import Video

        return Video.objects.published().filter(figures=self).distinct()[:limit]


class TaxPoint(models.Model):
    figure = models.ForeignKey(PracticeFigure, on_delete=models.CASCADE, related_name="tax_points")
    order = models.PositiveSmallIntegerField("Orden", default=0)
    title = models.CharField("Título", max_length=120, validators=TEXTO_VISIBLE, help_text="Ejemplo. Término de giro.")
    text = models.TextField("Texto", validators=TEXTO_LARGO)

    class Meta:
        verbose_name = "Punto tributario"
        verbose_name_plural = "Lo tributario"
        ordering = ["order", "id"]

    def __str__(self):
        return self.title

    @property
    def numeral(self):
        return romano(self.order)


class FAQ(models.Model):
    area = models.ForeignKey(PracticeArea, on_delete=models.CASCADE, related_name="faqs", null=True, blank=True)
    figure = models.ForeignKey(PracticeFigure, on_delete=models.CASCADE, related_name="faqs", null=True, blank=True)
    order = models.PositiveSmallIntegerField("Orden", default=0)
    question = models.CharField("Pregunta", max_length=240, validators=TEXTO_VISIBLE)
    answer = models.TextField("Respuesta", validators=TEXTO_LARGO)

    class Meta:
        verbose_name = "Pregunta frecuente"
        verbose_name_plural = "Preguntas frecuentes"
        ordering = ["order", "id"]

    def __str__(self):
        return self.question


class WorkStep(models.Model):
    area = models.ForeignKey(PracticeArea, on_delete=models.CASCADE, related_name="work_steps")
    order = models.PositiveSmallIntegerField("Orden", default=0)
    text = models.TextField("Paso", validators=TEXTO_VISIBLE)

    class Meta:
        verbose_name = "Paso de trabajo"
        verbose_name_plural = "Cómo trabajo"
        ordering = ["order", "id"]

    def __str__(self):
        return self.text[:60]

    @property
    def numeral(self):
        return romano(self.order)


class ReorgMapOption(models.Model):
    area = models.ForeignKey(PracticeArea, on_delete=models.CASCADE, related_name="map_options")
    order = models.PositiveSmallIntegerField("Orden", default=0)
    question = models.CharField("Objetivo del empresario", max_length=160, validators=TEXTO_VISIBLE)
    figure = models.ForeignKey(PracticeFigure, on_delete=models.PROTECT, related_name="map_options", verbose_name="Figura")
    name = models.CharField("Nombre a mostrar", max_length=60, validators=TEXTO_VISIBLE)
    description = models.TextField("Descripción", validators=TEXTO_VISIBLE)
    attention_point = models.TextField("Punto de atención", validators=TEXTO_LARGO)

    class Meta:
        verbose_name = "Opción del mapa"
        verbose_name_plural = "Mapa de reorganizaciones"
        ordering = ["order", "id"]

    def __str__(self):
        return self.question

    def as_dict(self):
        return {
            "q": self.question,
            "name": self.name,
            "para": self.description,
            "atencion": self.attention_point,
            "page": self.figure.get_absolute_url(),
        }


class ComparatorRow(models.Model):
    area = models.ForeignKey(PracticeArea, on_delete=models.CASCADE, related_name="comparator_rows")
    order = models.PositiveSmallIntegerField("Orden", default=0)
    criterion = models.CharField("Criterio", max_length=80, validators=TEXTO_VISIBLE)
    sa = models.TextField("Sociedad anónima", validators=TEXTO_LARGO)
    spa = models.TextField("Sociedad por acciones", validators=TEXTO_LARGO)
    ltda = models.TextField("Responsabilidad limitada", validators=TEXTO_LARGO)

    class Meta:
        verbose_name = "Fila del comparador"
        verbose_name_plural = "Comparador de tipos sociales"
        ordering = ["order", "id"]

    def __str__(self):
        return self.criterion
