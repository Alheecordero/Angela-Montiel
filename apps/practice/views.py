import json

from django.http import Http404
from django.views.generic import TemplateView

from apps.core import seo
from apps.core.views import SeoMixin

from .models import PracticeArea, PracticeFigure


class PracticePageView(SeoMixin, TemplateView):
    """Resuelve un slug de primer nivel como área o como figura."""

    def get_template_names(self):
        return ["practice/area.html"] if self.page_type == "area" else ["practice/figure.html"]

    def get_object(self):
        slug = self.kwargs["slug"]
        staff = self.request.user.is_staff
        area = PracticeArea.objects.filter(slug=slug).first()
        if area and (area.is_published or staff):
            self.page_type = "area"
            return area
        figure = PracticeFigure.objects.select_related("area").filter(slug=slug).first()
        if figure and (figure.is_published or staff):
            self.page_type = "figure"
            return figure
        raise Http404()

    def get_page_context(self, context):
        self.object = self.get_object()
        context["page"] = self.object
        context["page_type"] = self.page_type
        context["faqs"] = list(self.object.faqs.all())
        context["breadcrumbs"] = self.object.breadcrumbs()
        if self.page_type == "area":
            area = self.object
            context["area"] = area
            context["figures"] = list(area.figures.published())
            context["map_options"] = list(area.map_options.select_related("figure"))
            context["map_options_json"] = json.dumps([o.as_dict() for o in context["map_options"]], ensure_ascii=False)
            context["comparator_rows"] = list(area.comparator_rows.all())
            context["work_steps"] = list(area.work_steps.all())
            from apps.publications.models import Publication
            from apps.videos.models import Video

            context["related_publications"] = list(Publication.objects.published().filter(areas=area).distinct()[:3])
            context["related_videos"] = list(Video.objects.published().filter(area=area)[:2])
        else:
            figure = self.object
            context["figure"] = figure
            context["area"] = figure.area
            context["tax_points"] = list(figure.tax_points.all())
            context["related_publications"] = list(figure.related_publications())
            context["related_videos"] = list(figure.related_videos())
        return context

    def get_seo(self, context):
        site = context["site"]
        page = context["page"]
        meta = seo.page_meta(site, title=page.meta_title, description=page.meta_description, path=page.get_absolute_url(), noindex=not page.is_published)
        graph = seo.graph(
            seo.breadcrumb_graph(site, context["breadcrumbs"]),
            seo.webpage_graph(site, page.get_absolute_url(), page.meta_title, page.meta_description, page.content_updated_at, page.verified_at),
            seo.faq_graph(context["faqs"]),
        )
        return meta, graph


area_view = PracticePageView.as_view()
figure_view = PracticePageView.as_view()
