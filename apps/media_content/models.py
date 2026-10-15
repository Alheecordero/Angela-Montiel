import re

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from apps.blog.models import Category, PublishStatus, PublishedQuerySet


YOUTUBE_ID_PATTERN = re.compile(
    r"(?:youtube\.com/(?:watch\?v=|embed/|shorts/)|youtu\.be/)([A-Za-z0-9_-]{11})"
)


def extract_youtube_id(url):
    if not url:
        return ""
    match = YOUTUBE_ID_PATTERN.search(url.strip())
    return match.group(1) if match else ""


class VideoPost(models.Model):
    title = models.CharField("Título", max_length=200)
    slug = models.SlugField("Slug", unique=True, max_length=220)
    description = models.TextField("Descripción", blank=True)
    youtube_url = models.URLField("URL de YouTube", help_text="Ej: https://www.youtube.com/watch?v=...")
    youtube_id = models.CharField("ID de YouTube", max_length=20, blank=True, editable=False)
    thumbnail = models.ImageField("Miniatura personalizada", upload_to="videos/thumbs/", blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="videos",
        verbose_name="Categoría",
    )
    status = models.CharField(
        "Estado",
        max_length=20,
        choices=PublishStatus.choices,
        default=PublishStatus.DRAFT,
    )
    published_at = models.DateTimeField("Fecha de publicación", default=timezone.now)
    created_at = models.DateTimeField("Creado", auto_now_add=True)
    updated_at = models.DateTimeField("Actualizado", auto_now=True)

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
            raise ValidationError({"youtube_url": "Ingrese una URL válida de YouTube."})
        self.youtube_id = youtube_id

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        self.youtube_id = extract_youtube_id(self.youtube_url)
        if self.status == PublishStatus.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog:post_detail", kwargs={"slug": self.slug})

    @property
    def is_published(self):
        return self.status == PublishStatus.PUBLISHED and self.published_at <= timezone.now()

    @property
    def embed_url(self):
        if self.youtube_id:
            return f"https://www.youtube-nocookie.com/embed/{self.youtube_id}"
        return ""

    @property
    def thumbnail_url(self):
        if self.thumbnail:
            return self.thumbnail.url
        if self.youtube_id:
            return f"https://img.youtube.com/vi/{self.youtube_id}/hqdefault.jpg"
        return ""
