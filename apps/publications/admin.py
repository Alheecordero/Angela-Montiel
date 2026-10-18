from django import forms
from django.contrib import admin
from django.utils import timezone
from django_ckeditor_5.widgets import CKEditor5Widget
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display

from apps.core.models import PublishStatus

from .models import Publication, Source


class SourceInline(TabularInline):
    model = Source
    extra = 1
    fields = ("order", "text", "url")
    ordering = ("order",)


class PublicationForm(forms.ModelForm):
    class Meta:
        model = Publication
        fields = "__all__"
        widgets = {
            "body": CKEditor5Widget(config_name="default"),
            "summary": forms.Textarea(attrs={"rows": 4}),
            "tax_block": forms.Textarea(attrs={"rows": 5}),
            "ley": forms.Textarea(attrs={"rows": 3}),
            "criterio": forms.Textarea(attrs={"rows": 3}),
            "riesgo": forms.Textarea(attrs={"rows": 3}),
        }


@admin.action(description="Publicar las seleccionadas")
def publish(modeladmin, request, queryset):
    queryset.update(status=PublishStatus.PUBLISHED, published_at=timezone.now())


@admin.action(description="Pasar a borrador")
def draft(modeladmin, request, queryset):
    queryset.update(status=PublishStatus.DRAFT)


@admin.register(Publication)
class PublicationAdmin(ModelAdmin):
    form = PublicationForm
    list_display = ("title", "format", "status_badge", "published_at", "content_updated_at", "reading_time_display")
    list_filter = ("status", "format", "areas", "figures")
    search_fields = ("title", "lead", "summary", "body")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("areas", "figures")
    inlines = [SourceInline]
    actions = [publish, draft]
    readonly_fields = ("created_at", "updated_at", "reading_time_display")
    date_hierarchy = "published_at"
    fieldsets = (
        ("Título y clasificación", {"fields": ("title", "slug", "format", "areas", "figures")}),
        ("Texto", {"fields": ("lead", "summary", "body", "highlight")}),
        ("Bloques opcionales", {"fields": ("tax_block", "ley", "criterio", "riesgo"), "classes": ("collapse",)}),
        ("Imagen", {"fields": ("image", "image_alt")}),
        ("Fechas", {"fields": ("published_at", "content_updated_at", "verified_at", "reading_time_display")}),
        ("Publicación", {"fields": ("status", "created_at", "updated_at")}),
    )

    @display(description="Estado", label={PublishStatus.PUBLISHED: "success", PublishStatus.DRAFT: "warning"})
    def status_badge(self, obj):
        return obj.get_status_display()

    @display(description="Lectura")
    def reading_time_display(self, obj):
        return f"{obj.reading_time} min" if obj.pk else "—"
