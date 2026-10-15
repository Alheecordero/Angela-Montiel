from django.conf import settings

from .models import AboutSection, SiteSettings


def site_context(request):
    return {
        "site_settings": SiteSettings.load(),
        "about_section": AboutSection.load(),
        "SITE_INDEXABLE": settings.SITE_INDEXABLE,
    }
