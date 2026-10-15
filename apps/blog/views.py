from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import render
from django.views.generic import DetailView, View

from apps.media_content.models import VideoPost

from .content import get_published_content
from .models import Category, Post, Tag


class BlogListView(View):
    template_name = "blog/post_list.html"
    paginate_by = 9

    def get(self, request, category_slug=None, tag_slug=None):
        content_type = request.GET.get("tipo", "todos")
        if content_type not in ("todos", "articulos", "videos"):
            content_type = "todos"

        items = get_published_content(
            content_type=content_type if content_type != "todos" else None,
            category_slug=category_slug,
            tag_slug=tag_slug,
        )

        paginator = Paginator(items, self.paginate_by)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        context = {
            "page_obj": page_obj,
            "content_items": page_obj.object_list,
            "categories": Category.objects.all(),
            "tags": Tag.objects.all(),
            "active_category": category_slug,
            "active_tag": tag_slug,
            "active_type": content_type,
        }
        return render(request, self.template_name, context)


class PostDetailView(DetailView):
    model = Post
    template_name = "blog/post_detail.html"
    context_object_name = "post"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Post.objects.select_related("category").prefetch_related("tags")

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not obj.is_published and not self.request.user.is_staff:
            raise Http404()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object
        related = Post.objects.published().exclude(pk=post.pk)
        if post.category_id:
            related = related.filter(category=post.category)
        context["related_posts"] = related[:3]
        return context


class ContentDetailView(View):
    def get(self, request, slug):
        post = Post.objects.select_related("category").prefetch_related("tags").filter(slug=slug).first()
        if post and (post.is_published or request.user.is_staff):
            related = Post.objects.published().exclude(pk=post.pk)
            if post.category_id:
                related = related.filter(category=post.category)
            return render(
                request,
                "blog/post_detail.html",
                {"post": post, "related_posts": related[:3]},
            )

        video = VideoPost.objects.select_related("category").filter(slug=slug).first()
        if video and (video.is_published or request.user.is_staff):
            related = [
                {"type": "video", "obj": item}
                for item in VideoPost.objects.published().exclude(pk=video.pk)[:3]
            ]
            return render(
                request,
                "blog/video_detail.html",
                {"video": video, "related_items": related},
            )

        raise Http404()
