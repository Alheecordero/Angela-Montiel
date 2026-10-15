from django.conf import settings
from django.http import HttpResponse
from django.views.generic import TemplateView

from apps.blog.content import get_published_content

from .models import AboutSection, SiteSettings


class HomeView(TemplateView):
    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["site_settings"] = SiteSettings.load()
        context["about_section"] = AboutSection.load()
        context["latest_content"] = get_published_content()[:4]
        return context


class AboutView(TemplateView):
    template_name = "core/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["about_section"] = AboutSection.load()
        return context


def robots_txt(request):
    if settings.SITE_INDEXABLE:
        content = "\n".join(
            [
                "User-agent: *",
                "Allow: /",
                "",
                f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}",
            ]
        )
    else:
        content = "\n".join(
            [
                "User-agent: *",
                "Disallow: /",
                "",
                "# Sitio en desarrollo — indexación deshabilitada",
            ]
        )
    response = HttpResponse(content, content_type="text/plain")
    if not settings.SITE_INDEXABLE:
        response["X-Robots-Tag"] = "noindex, nofollow, noarchive"
    return response
