from django.db import models


class SiteSettings(models.Model):
    site_name = models.CharField("Nombre del sitio", max_length=120, default="Angela Montiel")
    tagline = models.CharField("Subtítulo / eslogan", max_length=200, blank=True)
    hero_title = models.CharField("Título principal (hero)", max_length=200, default="Asesoría legal profesional")
    hero_subtitle = models.TextField("Subtítulo del hero", blank=True)
    hero_cta_text = models.CharField("Texto del botón principal", max_length=80, default="Agendar consulta")
    hero_cta_url = models.CharField("URL del botón principal", max_length=200, default="/contacto/")
    phone = models.CharField("Teléfono", max_length=30, blank=True)
    email = models.EmailField("Correo electrónico", blank=True)
    address = models.CharField("Dirección", max_length=255, blank=True)
    city = models.CharField("Ciudad", max_length=100, default="Santiago, Chile")
    linkedin_url = models.URLField("LinkedIn", blank=True)
    instagram_url = models.URLField("Instagram", blank=True)
    facebook_url = models.URLField("Facebook", blank=True)
    footer_text = models.TextField("Texto del pie de página", blank=True)
    meta_description = models.TextField("Descripción SEO (inicio)", blank=True)

    class Meta:
        verbose_name = "Configuración del sitio"
        verbose_name_plural = "Configuración del sitio"

    def __str__(self):
        return self.site_name

    @property
    def phone_digits(self):
        return "".join(ch for ch in (self.phone or "") if ch.isdigit())

    @property
    def phone_href(self):
        digits = self.phone_digits
        return f"tel:+{digits}" if digits else ""

    @property
    def whatsapp_url(self):
        digits = self.phone_digits
        if not digits:
            return ""
        if digits.startswith("0"):
            digits = digits.lstrip("0")
        if not digits.startswith("56"):
            digits = f"56{digits}"
        return f"https://wa.me/{digits}"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class AboutSection(models.Model):
    headline = models.CharField("Titular", max_length=200, default="Sobre mí")
    bio = models.TextField("Biografía")
    photo = models.ImageField("Foto profesional", upload_to="about/", blank=True)
    university = models.CharField("Universidad", max_length=200, blank=True)
    bar_association = models.CharField("Colegio de abogados", max_length=200, blank=True)
    specialties = models.CharField(
        "Especialidades",
        max_length=300,
        blank=True,
        help_text="Separadas por comas, ej: Derecho civil, Familia",
    )
    years_experience = models.PositiveIntegerField("Años de experiencia", default=0)
    credentials = models.TextField("Credenciales adicionales", blank=True)

    class Meta:
        verbose_name = "Sobre mí"
        verbose_name_plural = "Sobre mí"

    def __str__(self):
        return self.headline

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(
            pk=1,
            defaults={
                "bio": "Abogada con experiencia en asesoría legal en Chile.",
            },
        )
        return obj

    @property
    def specialty_list(self):
        if not self.specialties:
            return []
        return [s.strip() for s in self.specialties.split(",") if s.strip()]
