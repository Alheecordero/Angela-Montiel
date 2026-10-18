from django.contrib import admin
from unfold.admin import ModelAdmin, StackedInline, TabularInline
from unfold.decorators import display

from apps.core.models import PublishStatus

from .models import FAQ, ComparatorRow, PracticeArea, PracticeFigure, ReorgMapOption, TaxPoint, WorkStep


class AreaFAQInline(StackedInline):
    model = FAQ
    fk_name = "area"
    extra = 0
    fields = ("order", "question", "answer")
    ordering = ("order",)
    verbose_name_plural = "Preguntas frecuentes"


class FigureFAQInline(StackedInline):
    model = FAQ
    fk_name = "figure"
    extra = 0
    fields = ("order", "question", "answer")
    ordering = ("order",)
    verbose_name_plural = "Preguntas frecuentes"


class WorkStepInline(TabularInline):
    model = WorkStep
    extra = 0
    fields = ("order", "text")
    ordering = ("order",)


class MapOptionInline(StackedInline):
    model = ReorgMapOption
    fk_name = "area"
    extra = 0
    fields = ("order", "question", "figure", "name", "description", "attention_point")
    ordering = ("order",)


class ComparatorRowInline(StackedInline):
    model = ComparatorRow
    extra = 0
    fields = ("order", "criterion", "sa", "spa", "ltda")
    ordering = ("order",)


class TaxPointInline(StackedInline):
    model = TaxPoint
    extra = 0
    fields = ("order", "title", "text")
    ordering = ("order",)
    verbose_name_plural = "Lo tributario (puntos numerados en romanos)"


STATUS_LABELS = {PublishStatus.PUBLISHED: "success", PublishStatus.DRAFT: "warning"}


@admin.register(PracticeArea)
class PracticeAreaAdmin(ModelAdmin):
    list_display = ("name", "slug", "is_primary", "status_badge", "content_updated_at", "verified_at")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [WorkStepInline, AreaFAQInline, MapOptionInline, ComparatorRowInline]
    fieldsets = (
        ("Identidad", {"fields": ("name", "short_name", "slug", "label", "is_primary", "order")}),
        ("Encabezado", {"fields": ("title", "lead", "content_updated_at")}),
        ("Inicio", {"fields": ("home_description", "home_cta")}),
        ("Herramienta interactiva", {"fields": ("tool_label", "tool_title", "tool_intro", "tool_note"), "description": "El mapa o el comparador se editan en las tablas de abajo."}),
        ("Lista de figuras", {"fields": ("figures_label", "figures_title")}),
        ("Y en lo tributario…", {"fields": ("tax_label", "tax_title", "tax_text")}),
        ("La ley, mi criterio y el riesgo", {"fields": ("ley", "criterio", "riesgo")}),
        ("Cómo trabajo", {"fields": ("how_label",), "description": "Los pasos se editan en la tabla de abajo."}),
        ("Fuentes y verificación", {"fields": ("sources", "verified_at")}),
        ("Cierre", {"fields": ("closing_question", "whatsapp_message")}),
        ("Posicionamiento", {"fields": ("meta_title", "meta_description")}),
        ("Publicación", {"fields": ("status", "published_at")}),
    )

    @display(description="Estado", label=STATUS_LABELS)
    def status_badge(self, obj):
        return obj.get_status_display()


@admin.register(PracticeFigure)
class PracticeFigureAdmin(ModelAdmin):
    list_display = ("name", "area", "slug", "status_badge", "content_updated_at", "verified_at")
    list_filter = ("area", "status")
    search_fields = ("name", "title", "definition_lead")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [TaxPointInline, FigureFAQInline]
    fieldsets = (
        ("Identidad", {"fields": ("area", "name", "short_name", "menu_name", "slug", "label", "order", "card_text")}),
        ("Encabezado", {"fields": ("title", "lead", "content_updated_at")}),
        ("Definición", {"fields": ("definition_label", "definition_lead", "definition_body")}),
        ("Lo societario", {"fields": ("sa", "spa", "ltda", "societario_note")}),
        ("La ley, mi criterio y el riesgo", {"fields": ("ley", "criterio", "riesgo")}),
        ("Fuentes y verificación", {"fields": ("sources", "verified_at")}),
        ("Cierre", {"fields": ("closing_question", "whatsapp_message")}),
        ("Posicionamiento", {"fields": ("meta_title", "meta_description")}),
        ("Publicación", {"fields": ("status", "published_at")}),
    )

    @display(description="Estado", label=STATUS_LABELS)
    def status_badge(self, obj):
        return obj.get_status_display()
