from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


class PublishStatus(models.TextChoices):
    DRAFT = "draft", "Borrador"
    PUBLISHED = "published", "Publicado"


class PublishedQuerySet(models.QuerySet):
    def published(self):
        now = timezone.now()
        return self.filter(status=PublishStatus.PUBLISHED, published_at__lte=now)


class Category(models.Model):
    name = models.CharField("Nombre", max_length=100)
    slug = models.SlugField("Slug", unique=True, max_length=120)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Tag(models.Model):
    name = models.CharField("Nombre", max_length=60)
    slug = models.SlugField("Slug", unique=True, max_length=80)

    class Meta:
        verbose_name = "Etiqueta"
        verbose_name_plural = "Etiquetas"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Post(models.Model):
    title = models.CharField("Título", max_length=200)
    slug = models.SlugField("Slug", unique=True, max_length=220)
    excerpt = models.TextField("Extracto", max_length=400, blank=True)
    content = models.TextField("Contenido")
    cover_image = models.ImageField("Imagen de portada", upload_to="blog/covers/", blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posts",
        verbose_name="Categoría",
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="posts", verbose_name="Etiquetas")
    status = models.CharField(
        "Estado",
        max_length=20,
        choices=PublishStatus.choices,
        default=PublishStatus.DRAFT,
    )
    published_at = models.DateTimeField("Fecha de publicación", default=timezone.now)
    created_at = models.DateTimeField("Creado", auto_now_add=True)
    updated_at = models.DateTimeField("Actualizado", auto_now=True)
    meta_title = models.CharField("Meta título (SEO)", max_length=70, blank=True)
    meta_description = models.CharField("Meta descripción (SEO)", max_length=160, blank=True)

    objects = PublishedQuerySet.as_manager()

    class Meta:
        verbose_name = "Artículo"
        verbose_name_plural = "Artículos"
        ordering = ["-published_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.status == PublishStatus.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog:post_detail", kwargs={"slug": self.slug})

    @property
    def is_published(self):
        return self.status == PublishStatus.PUBLISHED and self.published_at <= timezone.now()

    @property
    def seo_title(self):
        return self.meta_title or self.title

    @property
    def seo_description(self):
        return self.meta_description or self.excerpt
