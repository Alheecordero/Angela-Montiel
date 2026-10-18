from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import GlossaryTerm, Guide


@admin.register(GlossaryTerm)
class GlossaryTermAdmin(ModelAdmin):
    list_display = ("term", "order")
    search_fields = ("term", "definition")
    fields = ("term", "definition", "order")


@admin.register(Guide)
class GuideAdmin(ModelAdmin):
    list_display = ("title", "status", "order", "updated_at")
    list_filter = ("status",)
    filter_horizontal = ("figures",)
    fields = ("title", "description", "file", "status", "figures", "order")
