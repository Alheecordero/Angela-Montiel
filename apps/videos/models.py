"""Videos (capítulo 9.1 de las especificaciones)."""

import re

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from apps.core.models import PublishStatus, PublishedQuerySet
from apps.core.validators import TEXTO_LARGO, TEXTO_VISIBLE

YOUTUBE_ID_PATTERN = re.compile(r"(?:youtube\.com/(?:watch\?v=|embed/|shorts/|live/)|youtu\.be/)([A-Za-z0-9_-]{11})")


def extract_youtube_id(url):
    if not url:
        return ""
    match = YOUTUBE_ID_PATTERN.search(url.strip())
    return match.group(1) if match else ""


class Video(models.Model):
    title = models.CharField("Título", max_length=200, validators=TEXTO_VISIBLE)
    slug = models.SlugField("URL", unique=True, max_length=220)
    youtube_url = models.URLField("URL de YouTube", help_text="Ejemplo. https://www.youtube.com/watch?v=XXXXXXXXXXX")
    youtube_id = models.CharField("ID de YouTube", max_length=20, blank=True, editable=False)
    thumbnail = models.ImageField("Miniatura personalizada", upload_to="videos/", blank=True, help_text="Si está vacía se usa la miniatura de YouTube.")
    duration_seconds = models.PositiveIntegerField("Duración en segundos", help_text="Se muestra como minutos y segundos y se declara en los datos estructurados.")

    area = models.ForeignKey("practice.PracticeArea", on_delete=models.PROTECT, related_name="videos", verbose_name="Área")
    figures = models.ManyToManyField("practice.PracticeFigure", related_name="videos", blank=True, verbose_name="Etiquetas de figura")

    summary = models.TextField("Resumen escrito", validators=TEXTO_LARGO, help_text="Tres o cuatro líneas con lo esencial, para quien prefiere leer.")
    transcript = models.TextField("Transcripción completa", validators=TEXTO_LARGO, help_text="Obligatoria. Google y las inteligencias artificiales leen texto, no video.")
    related_publications = models.ManyToManyField("publications.Publication", related_name="videos", blank=True, verbose_name="Publicaciones para profundizar")

    status = models.CharField("Estado", max_length=20, choices=PublishStatus.choices, default=PublishStatus.DRAFT)
    published_at = models.DateTimeField("Fecha de publicación", default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PublishedQuerySet.as_manager()

    class Meta:
        verbose_name = "Video"
        verbose_name_plural = "Videos"
        ordering = ["-published_at"]

    def __str__(self):
        return self.title

    def clean(self):
        youtube_id = extract_youtube_id(self.youtube_url)
        if not youtube_id:
            raise ValidationError({"youtube_url": "Ingresa una URL válida de YouTube."})
        self.youtube_id = youtube_id

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:220]
        self.youtube_id = extract_youtube_id(self.youtube_url)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("videos:detail", kwargs={"slug": self.slug})

    @property
    def is_published(self):
        return self.status == PublishStatus.PUBLISHED and self.published_at <= timezone.now()

    @property
    def embed_url(self):
        return f"https://www.youtube-nocookie.com/embed/{self.youtube_id}?autoplay=1&rel=0" if self.youtube_id else ""

    @property
    def watch_url(self):
        return f"https://www.youtube.com/watch?v={self.youtube_id}" if self.youtube_id else self.youtube_url

    @property
    def thumbnail_url(self):
        if self.thumbnail:
            return self.thumbnail.url
        return f"https://i.ytimg.com/vi/{self.youtube_id}/hqdefault.jpg" if self.youtube_id else ""

    @property
    def duration_display(self):
        """Sin dos puntos, por la regla de marca. Ejemplo. 4 min 32 s."""
        minutes, seconds = divmod(self.duration_seconds or 0, 60)
        if minutes and seconds:
            return f"{minutes} min {seconds} s"
        if minutes:
            return f"{minutes} min"
        return f"{seconds} s"

    @property
    def duration_iso(self):
        minutes, seconds = divmod(self.duration_seconds or 0, 60)
        hours, minutes = divmod(minutes, 60)
        parts = "PT"
        if hours:
            parts += f"{hours}H"
        if minutes:
            parts += f"{minutes}M"
        parts += f"{seconds}S"
        return parts

    @property
    def meta_title(self):
        return f"{self.title} | Ángela Montiel"
