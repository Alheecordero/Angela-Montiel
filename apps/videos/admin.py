from django import forms
from django.contrib import admin
from django.utils import timezone
from unfold.admin import ModelAdmin
from unfold.decorators import display

from apps.core.models import PublishStatus

from .models import Video


class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = "__all__"
        widgets = {
            "summary": forms.Textarea(attrs={"rows": 4}),
            "transcript": forms.Textarea(attrs={"rows": 18}),
        }


@admin.action(description="Publicar los seleccionados")
def publish(modeladmin, request, queryset):
    queryset.update(status=PublishStatus.PUBLISHED, published_at=timezone.now())


@admin.register(Video)
class VideoAdmin(ModelAdmin):
    form = VideoForm
    list_display = ("title", "area", "duration_display", "status_badge", "published_at")
    list_filter = ("status", "area", "figures")
    search_fields = ("title", "summary", "transcript")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("figures", "related_publications")
    actions = [publish]
    readonly_fields = ("youtube_id", "updated_at")
    fieldsets = (
        ("Video", {"fields": ("title", "slug", "youtube_url", "youtube_id", "thumbnail", "duration_seconds")}),
        ("Clasificación", {"fields": ("area", "figures", "related_publications")}),
        ("Texto", {"fields": ("summary", "transcript"), "description": "La transcripción es obligatoria. Es lo que leen Google y las inteligencias artificiales."}),
        ("Publicación", {"fields": ("status", "published_at", "updated_at")}),
    )

    @display(description="Estado", label={PublishStatus.PUBLISHED: "success", PublishStatus.DRAFT: "warning"})
    def status_badge(self, obj):
        return obj.get_status_display()
