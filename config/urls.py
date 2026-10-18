from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponseNotFound
from django.urls import include, path, re_path
from django.views.generic import RedirectView

from apps.core.views import llms_txt, robots_txt
from config.sitemaps import SITEMAPS


def conditional_sitemap(request, **kwargs):
    if not settings.SITE_INDEXABLE:
        return HttpResponseNotFound("Sitemap no disponible en entorno de desarrollo.")
    return sitemap(request, sitemaps=SITEMAPS, **kwargs)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("ckeditor5/", include("django_ckeditor_5.urls")),
    path("robots.txt", robots_txt, name="robots"),
    path("llms.txt", llms_txt, name="llms"),
    path("sitemap.xml", conditional_sitemap, name="django.contrib.sitemaps.views.sitemap"),
    # Redirecciones desde las rutas de la versión anterior del sitio.
    re_path(r"^blog/videos/?$", RedirectView.as_view(url="/videos", permanent=True)),
    re_path(r"^blog/videos/(?P<slug>[-\w]+)/?$", RedirectView.as_view(url="/videos/%(slug)s", permanent=True)),
    re_path(r"^blog/?$", RedirectView.as_view(url="/publicaciones", permanent=True)),
    re_path(r"^blog/(?P<slug>[-\w]+)/?$", RedirectView.as_view(url="/publicaciones/%(slug)s", permanent=True)),
    re_path(r"^contacto/?$", RedirectView.as_view(url="/#conversemos", permanent=True)),
    re_path(r"^newsletter/baja/(?P<token>[-\w]+)/?$", RedirectView.as_view(url="/boletin/baja/%(token)s", permanent=True)),
    # Secciones con prefijo propio. Cada app declara sus rutas completas sin barra final.
    path("", include("apps.publications.urls")),
    path("", include("apps.videos.urls")),
    path("", include("apps.resources.urls")),
    path("", include("apps.newsletter.urls")),
    # Inicio, Sobre mí y páginas legales.
    path("", include("apps.core.urls")),
    # Áreas de práctica y figuras ocupan el primer nivel; van al final.
    path("", include("apps.practice.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
