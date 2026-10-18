from django.contrib import admin

from apps.core.models import PublishStatus
from apps.newsletter.models import Subscriber
from apps.practice.models import PracticeFigure
from apps.publications.models import Publication
from apps.videos.models import Video

admin.site.site_header = "Ángela Montiel · Administración"
admin.site.site_title = "Ángela Montiel"
admin.site.index_title = "Panel de control"


def dashboard_callback(request, context):
    context.update(
        {
            "stats": [
                {
                    "title": "Publicaciones publicadas",
                    "value": Publication.objects.filter(status=PublishStatus.PUBLISHED).count(),
                    "link": "/admin/publications/publication/",
                },
                {
                    "title": "Videos publicados",
                    "value": Video.objects.filter(status=PublishStatus.PUBLISHED).count(),
                    "link": "/admin/videos/video/",
                },
                {
                    "title": "Figuras publicadas",
                    "value": PracticeFigure.objects.filter(status=PublishStatus.PUBLISHED).count(),
                    "link": "/admin/practice/practicefigure/",
                },
                {
                    "title": "Suscriptores confirmados",
                    "value": Subscriber.objects.filter(is_active=True).count(),
                    "link": "/admin/newsletter/subscriber/?is_active__exact=1",
                },
            ],
        }
    )
    return context
