from django.contrib import admin
from django.utils import timezone
from unfold.admin import ModelAdmin
from unfold.decorators import display

from apps.blog.models import PublishStatus

from .models import VideoPost


@admin.action(description="Publicar videos seleccionados")
def publish_videos(modeladmin, request, queryset):
    queryset.update(status=PublishStatus.PUBLISHED, published_at=timezone.now())


@admin.action(description="Marcar como borrador")
def draft_videos(modeladmin, request, queryset):
    queryset.update(status=PublishStatus.DRAFT)


@admin.register(VideoPost)
class VideoPostAdmin(ModelAdmin):
    list_display = ("title", "category", "status_badge", "published_at")
    list_filter = ("status", "category", "published_at")
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}
    actions = [publish_videos, draft_videos]
    readonly_fields = ("youtube_id", "created_at", "updated_at")

    fieldsets = (
        ("Datos básicos", {"fields": ("title", "slug", "category")}),
        ("Video", {"fields": ("youtube_url", "youtube_id", "description", "thumbnail")}),
        ("Publicación", {"fields": ("status", "published_at", "created_at", "updated_at")}),
    )

    @display(
        description="Estado",
        label={
            PublishStatus.PUBLISHED: "success",
            PublishStatus.DRAFT: "warning",
        },
    )
    def status_badge(self, obj):
        return obj.get_status_display()
