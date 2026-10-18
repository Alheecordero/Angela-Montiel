from urllib.parse import quote

from django.db import models
from django.urls import reverse
from django.utils import timezone

from .validators import TEXTO_LARGO, TEXTO_VISIBLE


class PublishStatus(models.TextChoices):
    DRAFT = "draft", "Borrador"
    PUBLISHED = "published", "Publicado"


class PublishedQuerySet(models.QuerySet):
    def published(self):
        return self.filter(status=PublishStatus.PUBLISHED, published_at__lte=timezone.now())


class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class NewsletterMode(models.TextChoices):
    INACTIVE = "inactivo", "Inactivo (el formulario no se muestra)"
    OWN = "propio", "Boletín propio (formulario con doble verificación)"
    LINKEDIN = "linkedin", "Boletín en LinkedIn (enlace, sin recoger correos)"


class SiteSettings(SingletonModel):
    site_name = models.CharField("Nombre del sitio", max_length=120, default="Ángela Montiel", validators=TEXTO_VISIBLE)
    header_line = models.CharField(
        "Línea bajo el nombre",
        max_length=120,
        default="SOCIETARIO · REORGANIZACIONES · TRIBUTARIO",
        help_text="Provisoria hasta la aprobación de Ángela.",
        validators=TEXTO_VISIBLE,
    )
    short_presentation = models.CharField(
        "Presentación breve",
        max_length=120,
        default="ÁNGELA MONTIEL · DERECHO SOCIETARIO",
        validators=TEXTO_VISIBLE,
    )
    signature_phrase = models.CharField(
        "Frase firma",
        max_length=200,
        default="Entender tu empresa es la primera forma de protegerla.",
        validators=TEXTO_VISIBLE,
    )
    disclaimer = models.CharField(
        "Aclaración fija",
        max_length=200,
        default="Información general. Cada empresa requiere análisis particular. — Ángela",
        validators=TEXTO_VISIBLE,
    )

    whatsapp_number = models.CharField(
        "Número de WhatsApp",
        max_length=20,
        default="56930882307",
        help_text="Solo dígitos con código de país. Es el único medio de contacto del sitio.",
    )
    whatsapp_display = models.CharField("WhatsApp como se muestra", max_length=30, default="+56 9 3088 2307")

    canonical_base_url = models.URLField(
        "URL base canónica",
        default="https://angelamontiel.cl",
        help_text="Sin barra final. Se usa en canónicas, Open Graph, sitemap y datos estructurados.",
    )

    instagram_url = models.URLField("Instagram", blank=True, default="https://www.instagram.com/abogada_angelamontiel/")
    instagram_handle = models.CharField("Usuario de Instagram", max_length=60, blank=True, default="@abogada_angelamontiel")
    linkedin_url = models.URLField("LinkedIn", blank=True, help_text="Pendiente. Vacío se oculta.")
    youtube_url = models.URLField("Canal de YouTube", blank=True, help_text="Pendiente. Vacío se oculta y no se publica el tercer banner.")
    youtube_channel_name = models.CharField("Nombre del canal de YouTube", max_length=120, blank=True)
    tiktok_url = models.URLField("TikTok", blank=True, help_text="Pendiente. Vacío se oculta.")

    meta_title = models.CharField(
        "Etiqueta title del inicio",
        max_length=120,
        default="Ángela Montiel | Reorganizaciones empresariales y derecho societario con enfoque tributario",
    )
    meta_description = models.CharField(
        "Meta descripción del inicio",
        max_length=200,
        default="Derecho societario y reorganizaciones empresariales en Chile, explicados junto con su efecto tributario, para que decidas con claridad.",
    )
    default_og_image = models.ImageField(
        "Imagen por defecto para redes",
        upload_to="site/",
        blank=True,
        help_text="Mínimo 1200 por 630 px. Si está vacía se usa la fotografía del primer banner.",
    )

    search_console_token = models.CharField("Verificación de Google Search Console", max_length=120, blank=True)
    bing_token = models.CharField("Verificación de Bing Webmaster", max_length=120, blank=True)

    newsletter_mode = models.CharField(
        "Boletín",
        max_length=20,
        choices=NewsletterMode.choices,
        default=NewsletterMode.INACTIVE,
        help_text="Solo activar el boletín propio cuando la política de privacidad esté publicada.",
    )
    newsletter_linkedin_url = models.URLField("Enlace al boletín en LinkedIn", blank=True)

    class Meta:
        verbose_name = "Configuración del sitio"
        verbose_name_plural = "Configuración del sitio"

    def __str__(self):
        return self.site_name

    @property
    def whatsapp_url(self):
        return f"https://wa.me/{self.whatsapp_number}"

    def whatsapp_link(self, message=""):
        if message:
            return f"{self.whatsapp_url}?text={quote(message)}"
        return self.whatsapp_url

    @property
    def base_url(self):
        return self.canonical_base_url.rstrip("/")

    def absolute(self, path):
        if not path.startswith("/"):
            path = f"/{path}"
        return f"{self.base_url}{path}"

    @property
    def social_links(self):
        links = []
        if self.instagram_url:
            label = f"Instagram · {self.instagram_handle}" if self.instagram_handle else "Instagram"
            links.append({"name": "Instagram", "label": label, "url": self.instagram_url, "icon": "instagram"})
        if self.linkedin_url:
            links.append({"name": "LinkedIn", "label": "LinkedIn", "url": self.linkedin_url, "icon": "linkedin"})
        if self.youtube_url:
            label = f"YouTube · {self.youtube_channel_name}" if self.youtube_channel_name else "YouTube"
            links.append({"name": "YouTube", "label": label, "url": self.youtube_url, "icon": "play"})
        if self.tiktok_url:
            links.append({"name": "TikTok", "label": "TikTok", "url": self.tiktok_url, "icon": "arrow-right"})
        return links

    @property
    def same_as(self):
        return [link["url"] for link in self.social_links]

    @property
    def newsletter_enabled(self):
        return self.newsletter_mode == NewsletterMode.OWN

    @property
    def newsletter_linkedin(self):
        return self.newsletter_mode == NewsletterMode.LINKEDIN and bool(self.newsletter_linkedin_url)


class AboutPage(SingletonModel):
    label = models.CharField("Etiqueta superior", max_length=60, default="SOBRE MÍ", validators=TEXTO_VISIBLE)
    title = models.CharField("Título H1", max_length=200, default="Soy Ángela Montiel. Te ayudo a entender tu empresa.", validators=TEXTO_VISIBLE)
    lead = models.TextField(
        "Bajada",
        default="Asesoro a empresas de todo Chile desde 2019 en derecho societario y reorganizaciones empresariales, con enfoque tributario.",
        validators=TEXTO_VISIBLE,
    )
    photo = models.ImageField("Fotografía", upload_to="about/", blank=True)
    photo_alt = models.CharField("Texto alternativo de la fotografía", max_length=200, default="Ángela Montiel", validators=TEXTO_VISIBLE)
    since_year = models.CharField("Desde", max_length=10, default="2019")
    since_label = models.CharField("Texto bajo el año", max_length=80, default="ASESORANDO EMPRESAS EN CHILE", validators=TEXTO_VISIBLE)

    what_i_do_label = models.CharField("Etiqueta Lo que hago", max_length=60, default="LO QUE HAGO", validators=TEXTO_VISIBLE)
    what_i_do_title = models.CharField("Título Lo que hago", max_length=200, default="Ordenar la estructura de tu empresa, con su efecto tributario.", validators=TEXTO_VISIBLE)
    what_i_do_text = models.TextField("Texto Lo que hago", blank=True, validators=TEXTO_LARGO)

    how_i_work_label = models.CharField("Etiqueta Cómo trabajo", max_length=60, default="CÓMO TRABAJO", validators=TEXTO_VISIBLE)
    how_i_work_title = models.CharField("Título Cómo trabajo", max_length=200, default="Lo que puedes esperar de mí.", validators=TEXTO_VISIBLE)

    education_label = models.CharField("Etiqueta Formación", max_length=60, default="FORMACIÓN", validators=TEXTO_VISIBLE)
    education_title = models.CharField("Título Formación", max_length=200, default="Estudiar también es parte del rigor.", validators=TEXTO_VISIBLE)

    in_brief_label = models.CharField("Etiqueta En breve", max_length=60, default="EN BREVE", validators=TEXTO_VISIBLE)
    in_brief = models.TextField(
        "En breve",
        blank=True,
        help_text="Es la única formulación autorizada del título profesional.",
        validators=TEXTO_LARGO,
    )

    person_description = models.TextField(
        "Descripción en tercera persona",
        blank=True,
        help_text="Solo para datos estructurados. Debe usar la formulación exacta del título profesional.",
        validators=TEXTO_LARGO,
    )
    knows_about = models.TextField(
        "Materias (knowsAbout)",
        blank=True,
        help_text="Una por línea.",
        default="Derecho societario\nReorganizaciones empresariales\nFusión de sociedades\nDivisión de sociedades\nTransformación de sociedades\nAporte de bienes\nConversión de empresario individual\nTributación corporativa",
    )

    meta_title = models.CharField("Etiqueta title", max_length=120, default="Sobre mí | Ángela Montiel")
    meta_description = models.CharField(
        "Meta descripción",
        max_length=200,
        default="Asesoro a empresas de todo Chile desde 2019 en derecho societario y reorganizaciones empresariales, con enfoque tributario. Formación y forma de trabajo.",
    )

    class Meta:
        verbose_name = "Sobre mí"
        verbose_name_plural = "Sobre mí"

    def __str__(self):
        return "Sobre mí"

    def get_absolute_url(self):
        return reverse("core:about")

    @property
    def knows_about_list(self):
        return [line.strip() for line in self.knows_about.splitlines() if line.strip()]

    @property
    def photo_url(self):
        if self.photo:
            return self.photo.url
        from django.templatetags.static import static

        return static("images/angela-escritorio.jpg")


class WorkPrinciple(models.Model):
    page = models.ForeignKey(AboutPage, on_delete=models.CASCADE, related_name="principles")
    order = models.PositiveSmallIntegerField("Orden", default=0)
    title = models.CharField("Título", max_length=200, validators=TEXTO_VISIBLE)
    text = models.TextField("Texto", validators=TEXTO_VISIBLE)

    class Meta:
        verbose_name = "Principio de trabajo"
        verbose_name_plural = "Cómo trabajo"
        ordering = ["order", "id"]

    def __str__(self):
        return self.title


class CredentialCategory(models.TextChoices):
    DEGREE = "degree", "Título"
    CERTIFICATE = "certificate", "Diplomado o certificado"
    IN_PROGRESS = "in_progress", "En curso"


class Education(models.Model):
    page = models.ForeignKey(AboutPage, on_delete=models.CASCADE, related_name="education")
    order = models.PositiveSmallIntegerField("Orden", default=0)
    year = models.CharField("Año o estado", max_length=20, validators=TEXTO_VISIBLE)
    title = models.CharField("Título", max_length=200, validators=TEXTO_VISIBLE)
    institution = models.CharField("Institución", max_length=200, validators=TEXTO_VISIBLE)
    category = models.CharField("Tipo", max_length=20, choices=CredentialCategory.choices, default=CredentialCategory.CERTIFICATE)

    class Meta:
        verbose_name = "Formación"
        verbose_name_plural = "Formación"
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.title} · {self.institution}"


class LegalSlug(models.TextChoices):
    PRIVACY = "politica-de-privacidad", "Política de privacidad"
    TERMS = "terminos-de-uso", "Términos de uso"


class LegalPage(models.Model):
    slug = models.CharField("URL", max_length=40, choices=LegalSlug.choices, unique=True)
    title = models.CharField("Título H1", max_length=120, validators=TEXTO_VISIBLE)
    body = models.TextField("Texto", blank=True, help_text="Lo redacta Ángela. Mientras esté vacío, la página muestra solo el título.", validators=TEXTO_LARGO)
    is_published = models.BooleanField("Publicada", default=False)
    updated_at = models.DateTimeField("Actualizada", auto_now=True)
    meta_description = models.CharField("Meta descripción", max_length=200, blank=True)

    class Meta:
        verbose_name = "Página legal"
        verbose_name_plural = "Páginas legales"
        ordering = ["slug"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return f"/{self.slug}"
