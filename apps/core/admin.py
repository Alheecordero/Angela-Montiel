from django import forms
from django.contrib import admin
from django_ckeditor_5.widgets import CKEditor5Widget
from unfold.admin import ModelAdmin, TabularInline

from .models import AboutPage, Education, LegalPage, SiteSettings, WorkPrinciple


class SingletonAdmin(ModelAdmin):
    def has_add_permission(self, request):
        return not self.model.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        from django.shortcuts import redirect

        obj = self.model.load()
        return redirect(f"/admin/{self.model._meta.app_label}/{self.model._meta.model_name}/{obj.pk}/change/")


@admin.register(SiteSettings)
class SiteSettingsAdmin(SingletonAdmin):
    fieldsets = (
        ("Identidad", {"fields": ("site_name", "header_line", "short_presentation", "signature_phrase", "disclaimer")}),
        ("Contacto único", {"fields": ("whatsapp_number", "whatsapp_display"), "description": "El único medio de contacto del sitio es WhatsApp."}),
        ("Redes sociales", {"fields": ("instagram_url", "instagram_handle", "linkedin_url", "youtube_url", "youtube_channel_name", "tiktok_url"), "description": "Las redes sin enlace se ocultan."}),
        ("Posicionamiento", {"fields": ("canonical_base_url", "meta_title", "meta_description", "default_og_image", "search_console_token", "bing_token")}),
        ("Boletín", {"fields": ("newsletter_mode", "newsletter_linkedin_url")}),
    )


class WorkPrincipleInline(TabularInline):
    model = WorkPrinciple
    extra = 0
    fields = ("order", "title", "text")
    ordering = ("order",)


class EducationInline(TabularInline):
    model = Education
    extra = 0
    fields = ("order", "year", "title", "institution", "category")
    ordering = ("order",)


class AboutPageForm(forms.ModelForm):
    class Meta:
        model = AboutPage
        fields = "__all__"
        widgets = {
            "what_i_do_text": CKEditor5Widget(config_name="default"),
            "in_brief": forms.Textarea(attrs={"rows": 5}),
            "person_description": forms.Textarea(attrs={"rows": 5}),
        }


@admin.register(AboutPage)
class AboutPageAdmin(SingletonAdmin):
    form = AboutPageForm
    inlines = [WorkPrincipleInline, EducationInline]
    fieldsets = (
        ("Encabezado", {"fields": ("label", "title", "lead", "photo", "photo_alt", "since_year", "since_label")}),
        ("Lo que hago", {"fields": ("what_i_do_label", "what_i_do_title", "what_i_do_text")}),
        ("Cómo trabajo", {"fields": ("how_i_work_label", "how_i_work_title"), "description": "Los principios se editan en la tabla de abajo."}),
        ("Formación", {"fields": ("education_label", "education_title"), "description": "Los estudios se editan en la tabla de abajo."}),
        ("En breve", {"fields": ("in_brief_label", "in_brief")}),
        ("Datos estructurados", {"fields": ("person_description", "knows_about"), "classes": ("collapse",)}),
        ("Posicionamiento", {"fields": ("meta_title", "meta_description"), "classes": ("collapse",)}),
    )


class LegalPageForm(forms.ModelForm):
    class Meta:
        model = LegalPage
        fields = "__all__"
        widgets = {"body": CKEditor5Widget(config_name="default")}


@admin.register(LegalPage)
class LegalPageAdmin(ModelAdmin):
    form = LegalPageForm
    list_display = ("title", "slug", "is_published", "updated_at")
    readonly_fields = ("updated_at",)
    fields = ("slug", "title", "body", "is_published", "meta_description", "updated_at")

    def has_add_permission(self, request):
        return LegalPage.objects.count() < 2
