from django.views.generic import TemplateView

from apps.core import seo
from apps.core.views import SeoMixin
from apps.practice.models import PracticeArea

from .models import GlossaryTerm, Guide, GuideStatus


class ResourcesView(SeoMixin, TemplateView):
    template_name = "resources/index.html"

    def get_page_context(self, context):
        areas = list(PracticeArea.objects.published())
        context["map_area"] = next((a for a in areas if a.has_map), None)
        context["comparator_area"] = next((a for a in areas if a.has_comparator), None)
        context["terms"] = list(GlossaryTerm.objects.all())
        context["guides"] = list(Guide.objects.exclude(status=GuideStatus.HIDDEN))
        return context

    def get_seo(self, context):
        site = context["site"]
        meta = seo.page_meta(
            site,
            title="Recursos, glosario y herramientas | Ángela Montiel",
            description="Mapa de reorganizaciones, comparador de tipos sociales y glosario societario y tributario, verificados en fuentes oficiales.",
            path="/recursos",
        )
        crumbs = [{"name": "Inicio", "url": "/"}, {"name": "Recursos", "url": "/recursos"}]
        return meta, seo.graph(seo.breadcrumb_graph(site, crumbs))
