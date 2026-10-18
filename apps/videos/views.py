from django.http import Http404
from django.views.generic import TemplateView

from apps.core import seo
from apps.core.views import SeoMixin
from apps.practice.models import PracticeArea

from .models import Video


class VideoListView(SeoMixin, TemplateView):
    """Página de videos. Con `slug` muestra ese video como destacado."""

    template_name = "videos/list.html"

    def get_featured(self, videos):
        slug = self.kwargs.get("slug")
        if slug:
            video = Video.objects.select_related("area").prefetch_related("related_publications", "figures").filter(slug=slug).first()
            if not video or not (video.is_published or self.request.user.is_staff):
                raise Http404()
            return video
        return videos[0] if videos else None

    def get_page_context(self, context):
        videos = list(Video.objects.published().select_related("area"))
        featured = self.get_featured(videos)
        context["featured"] = featured
        context["videos"] = videos
        context["areas"] = PracticeArea.objects.published()
        context["is_detail"] = bool(self.kwargs.get("slug"))
        if featured:
            context["related_publications"] = list(featured.related_publications.all()[:3])
        return context

    def get_seo(self, context):
        site = context["site"]
        featured = context["featured"]
        if context["is_detail"] and featured:
            path = featured.get_absolute_url()
            meta = seo.page_meta(site, title=featured.meta_title, description=featured.summary[:200], path=path, og_type="video.other", og_image=featured.thumbnail_url if featured.thumbnail_url.startswith("http") else None, noindex=not featured.is_published)
            crumbs = [{"name": "Inicio", "url": "/"}, {"name": "Videos", "url": "/videos"}, {"name": featured.title, "url": path}]
            return meta, seo.graph(seo.breadcrumb_graph(site, crumbs), seo.video_graph(site, featured))
        meta = seo.page_meta(
            site,
            title="Videos, Entiende tu empresa | Ángela Montiel",
            description="Videos breves sobre las decisiones societarias que más se preguntan los empresarios, y su efecto tributario.",
            path="/videos",
        )
        crumbs = [{"name": "Inicio", "url": "/"}, {"name": "Videos", "url": "/videos"}]
        items = [seo.breadcrumb_graph(site, crumbs)]
        if featured:
            items.append(seo.video_graph(site, featured))
        return meta, seo.graph(*items)
