from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.blog.models import Post
from apps.media_content.models import VideoPost


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "monthly"

    def items(self):
        return ["core:home", "core:about", "blog:post_list", "contact:contact"]

    def location(self, item):
        return reverse(item)


class PostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Post.objects.published()

    def lastmod(self, obj):
        return obj.updated_at


class VideoSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return VideoPost.objects.published()

    def lastmod(self, obj):
        return obj.updated_at
