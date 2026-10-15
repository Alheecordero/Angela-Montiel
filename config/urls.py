from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponseNotFound
from django.urls import include, path
from django.views.generic import RedirectView

from apps.core.views import robots_txt
from config.sitemaps import PostSitemap, StaticViewSitemap, VideoSitemap

sitemaps = {
    "static": StaticViewSitemap,
    "posts": PostSitemap,
    "videos": VideoSitemap,
}


def conditional_sitemap(request, **kwargs):
    if not settings.SITE_INDEXABLE:
        return HttpResponseNotFound("Sitemap no disponible en entorno de desarrollo.")
    return sitemap(request, sitemaps=sitemaps, **kwargs)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("ckeditor5/", include("django_ckeditor_5.urls")),
    path("", include("apps.core.urls")),
    path("blog/videos/", RedirectView.as_view(url="/blog/?tipo=videos", permanent=True)),
    path(
        "blog/videos/<slug:slug>/",
        RedirectView.as_view(pattern_name="blog:post_detail", permanent=True),
    ),
    path("blog/", include("apps.blog.urls")),
    path("contacto/", include("apps.contact.urls")),
    path("newsletter/", include("apps.newsletter.urls")),
    path("robots.txt", robots_txt),
    path("sitemap.xml", conditional_sitemap, name="django.contrib.sitemaps.views.sitemap"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
