import json

from django.conf import settings
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from apps.practice.models import PracticeArea
from apps.publications.models import Publication
from apps.videos.models import Video

from . import seo
from .models import AboutPage, LegalPage, SiteSettings


class SeoMixin:
    """Agrega `page_meta` y `jsonld` al contexto desde `get_seo()`.

    Las vistas llenan el contexto en `get_page_context()`; el SEO se calcula
    después, cuando ya existen los objetos de la página.
    """

    def get_seo(self, context):
        return {}, None

    def get_page_context(self, context):
        return context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["site"] = SiteSettings.load()
        context = self.get_page_context(context)
        meta, graph = self.get_seo(context)
        context["page_meta"] = meta
        context["jsonld"] = graph
        return context


class HomeView(SeoMixin, TemplateView):
    template_name = "core/home.html"

    def get_page_context(self, context):
        site = context["site"]
        context["areas"] = PracticeArea.objects.published().prefetch_related("figures")
        map_area = context["areas"].filter(map_options__isnull=False).distinct().first()
        map_options = list(map_area.map_options.select_related("figure")) if map_area else []
        context["map_area"] = map_area
        context["map_options"] = map_options
        context["map_options_json"] = json.dumps([option.as_dict() for option in map_options], ensure_ascii=False)
        context["latest_nota"] = Publication.latest_nota()
        context["recent_publications"] = Publication.objects.published().prefetch_related("areas")[:3]
        context["recent_videos"] = list(Video.objects.published().select_related("area")[:2])
        latest_video = context["recent_videos"][0] if context["recent_videos"] else None
        # El tercer banner solo se publica cuando el canal existe y tiene videos.
        context["latest_video"] = latest_video if (latest_video and site.youtube_url) else None
        return context

    def get_seo(self, context):
        site = context["site"]
        about = AboutPage.load()
        meta = seo.page_meta(site, title=site.meta_title, description=site.meta_description, path="/")
        graph = seo.graph(seo.person_graph(site, about), seo.website_graph(site))
        return meta, graph


class AboutView(SeoMixin, TemplateView):
    template_name = "core/about.html"

    def get_page_context(self, context):
        context["about"] = AboutPage.load()
        context["areas"] = PracticeArea.objects.published()
        return context

    def get_seo(self, context):
        site = context["site"]
        about = context["about"]
        meta = seo.page_meta(site, title=about.meta_title, description=about.meta_description, path="/sobre-mi", og_type="profile")
        crumbs = [{"name": "Inicio", "url": "/"}, {"name": "Sobre mí", "url": "/sobre-mi"}]
        graph = seo.graph(seo.person_graph(site, about), seo.breadcrumb_graph(site, crumbs))
        return meta, graph


class LegalPageView(SeoMixin, TemplateView):
    template_name = "core/legal.html"

    def get_page_context(self, context):
        page = get_object_or_404(LegalPage, slug=self.kwargs["slug"])
        context["page"] = page
        return context

    def get_seo(self, context):
        site = context["site"]
        page = context["page"]
        meta = seo.page_meta(
            site,
            title=f"{page.title.rstrip('.')} | Ángela Montiel",
            description=page.meta_description or f"{page.title.rstrip('.')} del sitio angelamontiel.cl.",
            path=page.get_absolute_url(),
            noindex=not page.is_published,
        )
        crumbs = [{"name": "Inicio", "url": "/"}, {"name": page.title.rstrip("."), "url": page.get_absolute_url()}]
        return meta, seo.graph(seo.breadcrumb_graph(site, crumbs))


def robots_txt(request):
    site = SiteSettings.load()
    if settings.SITE_INDEXABLE:
        content = "\n".join(["User-agent: *", "Allow: /", "Disallow: /admin/", "", f"Sitemap: {site.absolute('/sitemap.xml')}"])
    else:
        content = "\n".join(["User-agent: *", "Disallow: /", "", "# Sitio en desarrollo. Indexación deshabilitada."])
    response = HttpResponse(content, content_type="text/plain; charset=utf-8")
    if not settings.SITE_INDEXABLE:
        response["X-Robots-Tag"] = "noindex, nofollow, noarchive"
    return response


def llms_txt(request):
    """Archivo de orientación para inteligencias artificiales (capítulo 10.3)."""
    if not settings.SITE_INDEXABLE:
        raise Http404()
    site = SiteSettings.load()
    about = AboutPage.load()
    lines = ["# Ángela Montiel", "", f"> {about.person_description or about.in_brief}", "", "## Áreas de práctica", ""]
    for area in PracticeArea.objects.published().prefetch_related("figures"):
        extra = ""
        if area.has_map:
            extra = " con mapa de figuras y su efecto tributario"
        elif area.has_comparator:
            extra = " con comparador de SA, SpA y limitada"
        lines.append(f"- [{area.name}]({site.absolute(area.get_absolute_url())}){extra}")
        for figure in area.figures.published():
            lines.append(f"- [{figure.name}]({site.absolute(figure.get_absolute_url())})")
    lines += [
        "",
        "## Contenido",
        "",
        f"- [Publicaciones]({site.absolute('/publicaciones')}) con notas jurídicas, análisis y guías",
        f"- [Videos]({site.absolute('/videos')}) de la serie Entiende tu empresa, con transcripción",
        f"- [Recursos]({site.absolute('/recursos')}) con glosario societario y tributario",
    ]
    publications = Publication.objects.published()[:20]
    if publications:
        lines += ["", "## Publicaciones recientes", ""]
        for pub in publications:
            lines.append(f"- [{pub.title}]({site.absolute(pub.get_absolute_url())}). {pub.lead}")
    lines += ["", "## Autora", "", f"- [Sobre mí]({site.absolute('/sobre-mi')})", ""]
    return HttpResponse("\n".join(lines), content_type="text/plain; charset=utf-8")
