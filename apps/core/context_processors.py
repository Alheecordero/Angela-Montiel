from django.conf import settings

from apps.practice.models import PracticeArea

from .models import AboutPage, SiteSettings


def site_context(request):
    site_settings = SiteSettings.load()
    areas = PracticeArea.objects.published().prefetch_related("figures")
    nav_areas = [
        {"area": area, "figures": [f for f in area.figures.all() if f.is_published]}
        for area in areas
    ]
    return {
        "site_settings": site_settings,
        "about_page": AboutPage.load(),
        "nav_areas": nav_areas,
        "SITE_INDEXABLE": settings.SITE_INDEXABLE,
        "canonical_url": site_settings.absolute(request.path),
    }
