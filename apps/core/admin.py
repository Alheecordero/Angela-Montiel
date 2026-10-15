from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import AboutSection, SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(ModelAdmin):
    fieldsets = (
        ("Identidad", {"fields": ("site_name", "tagline", "meta_description")}),
        (
            "Página de inicio (Hero)",
            {"fields": ("hero_title", "hero_subtitle", "hero_cta_text", "hero_cta_url")},
        ),
        ("Contacto", {"fields": ("phone", "email", "address", "city")}),
        ("Redes sociales", {"fields": ("linkedin_url", "instagram_url", "facebook_url")}),
        ("Pie de página", {"fields": ("footer_text",)}),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(AboutSection)
class AboutSectionAdmin(ModelAdmin):
    fieldsets = (
        ("Presentación", {"fields": ("headline", "photo")}),
        ("Biografía", {"fields": ("bio",)}),
        (
            "Credenciales",
            {"fields": ("university", "bar_association", "specialties", "years_experience", "credentials")},
        ),
    )

    def has_add_permission(self, request):
        return not AboutSection.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
