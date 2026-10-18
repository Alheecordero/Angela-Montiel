from urllib.parse import urlsplit

from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.core.models import LegalPage, SiteSettings
from apps.practice.models import PracticeArea, PracticeFigure
from apps.publications.models import Publication
from apps.videos.models import Video


class CanonicalSitemap(Sitemap):
    """Usa el dominio canónico configurado, no el host de la petición."""

    protocol = "https"

    def get_domain(self, site=None):
        return urlsplit(SiteSettings.load().base_url).netloc

    def get_protocol(self, protocol=None):
        return urlsplit(SiteSettings.load().base_url).scheme or "https"


class StaticViewSitemap(CanonicalSitemap):
    priority = 0.8
    changefreq = "monthly"

    def items(self):
        return ["core:home", "core:about", "publications:list", "videos:list", "resources:index"]

    def location(self, item):
        return reverse(item)


class LegalSitemap(CanonicalSitemap):
    priority = 0.2
    changefreq = "yearly"

    def items(self):
        return LegalPage.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at


class AreaSitemap(CanonicalSitemap):
    priority = 0.9
    changefreq = "monthly"

    def items(self):
        return PracticeArea.objects.published()

    def lastmod(self, obj):
        return obj.content_updated_at


class FigureSitemap(CanonicalSitemap):
    priority = 0.8
    changefreq = "monthly"

    def items(self):
        return PracticeFigure.objects.published()

    def lastmod(self, obj):
        return obj.content_updated_at


class PublicationSitemap(CanonicalSitemap):
    priority = 0.7
    changefreq = "weekly"

    def items(self):
        return Publication.objects.published()

    def lastmod(self, obj):
        return obj.content_updated_at


class VideoSitemap(CanonicalSitemap):
    priority = 0.6
    changefreq = "weekly"

    def items(self):
        return Video.objects.published()

    def lastmod(self, obj):
        return obj.updated_at


SITEMAPS = {
    "paginas": StaticViewSitemap,
    "areas": AreaSitemap,
    "figuras": FigureSitemap,
    "publicaciones": PublicationSitemap,
    "videos": VideoSitemap,
    "legales": LegalSitemap,
}
