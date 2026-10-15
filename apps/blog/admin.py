from django.contrib import admin
from django.utils import timezone
from unfold.admin import ModelAdmin
from unfold.decorators import display

from .forms import PostAdminForm
from .models import Category, Post, PublishStatus, Tag


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.action(description="Publicar artículos seleccionados")
def publish_posts(modeladmin, request, queryset):
    queryset.update(status=PublishStatus.PUBLISHED, published_at=timezone.now())


@admin.action(description="Marcar como borrador")
def draft_posts(modeladmin, request, queryset):
    queryset.update(status=PublishStatus.DRAFT)


@admin.register(Post)
class PostAdmin(ModelAdmin):
    form = PostAdminForm
    list_display = ("title", "category", "status_badge", "published_at", "updated_at")
    list_filter = ("status", "category", "tags", "published_at")
    search_fields = ("title", "excerpt", "content")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("tags",)
    actions = [publish_posts, draft_posts]
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Datos básicos", {"fields": ("title", "slug", "category", "tags")}),
        ("Contenido", {"fields": ("excerpt", "content", "cover_image")}),
        ("SEO", {"fields": ("meta_title", "meta_description"), "classes": ("collapse",)}),
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
