from django.http import Http404
from django.views.generic import TemplateView

from apps.core import seo
from apps.core.views import SeoMixin
from apps.newsletter.forms import NewsletterForm
from apps.practice.models import PracticeArea

from .models import FORMAT_DESCRIPTIONS, Publication, PublicationFormat


class PublicationListView(SeoMixin, TemplateView):
    template_name = "publications/list.html"

    def get_page_context(self, context):
        publications = list(Publication.objects.published().prefetch_related("areas"))
        context["featured"] = publications[0] if publications else None
        context["publications"] = publications
        context["formats"] = [{"key": key, "label": label, "description": FORMAT_DESCRIPTIONS[key]} for key, label in PublicationFormat.choices]
        context["format_descriptions"] = FORMAT_DESCRIPTIONS
        context["newsletter_form"] = NewsletterForm()
        context["areas"] = PracticeArea.objects.published()
        return context

    def get_seo(self, context):
        site = context["site"]
        meta = seo.page_meta(
            site,
            title="Publicaciones, notas jurídicas y análisis | Ángela Montiel",
            description="Notas jurídicas, análisis y guías sobre derecho societario y reorganizaciones empresariales en Chile, con fuentes oficiales verificadas.",
            path="/publicaciones",
        )
        crumbs = [{"name": "Inicio", "url": "/"}, {"name": "Publicaciones", "url": "/publicaciones"}]
        return meta, seo.graph(seo.breadcrumb_graph(site, crumbs))


class PublicationDetailView(SeoMixin, TemplateView):
    template_name = "publications/detail.html"

    def get_object(self):
        pub = Publication.objects.prefetch_related("areas", "figures", "sources").filter(slug=self.kwargs["slug"]).first()
        if not pub or not (pub.is_published or self.request.user.is_staff):
            raise Http404()
        return pub

    def get_page_context(self, context):
        self.object = self.get_object()
        pub = self.object
        context["publication"] = pub
        context["sources"] = list(pub.sources.all())
        context["related_publications"] = pub.related()
        context["related_videos"] = pub.related_videos()
        context["primary_area"] = pub.areas.first()
        context["breadcrumbs"] = [
            {"name": "Inicio", "url": "/"},
            {"name": "Publicaciones", "url": "/publicaciones"},
            {"name": pub.title, "url": pub.get_absolute_url()},
        ]
        return context

    def get_seo(self, context):
        site = context["site"]
        pub = context["publication"]
        image = site.absolute(pub.image.url) if pub.image else seo.default_og_image(site)
        meta = seo.page_meta(site, title=pub.meta_title, description=pub.lead, path=pub.get_absolute_url(), og_type="article", og_image=image, noindex=not pub.is_published)
        graph = seo.graph(seo.breadcrumb_graph(site, context["breadcrumbs"]), seo.article_graph(site, pub, image))
        return meta, graph
