from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin

from apps.blog.models import Post, PublishStatus
from apps.contact.models import ContactMessage
from apps.media_content.models import VideoPost
from apps.newsletter.models import Subscriber


admin.site.site_header = "Angela Montiel — Administración"
admin.site.site_title = "Angela Montiel"
admin.site.index_title = "Panel de control"


def dashboard_callback(request, context):
    context.update(
        {
            "stats": [
                {
                    "title": "Artículos publicados",
                    "value": Post.objects.filter(status=PublishStatus.PUBLISHED).count(),
                    "link": "/admin/blog/post/",
                },
                {
                    "title": "Videos publicados",
                    "value": VideoPost.objects.filter(status=PublishStatus.PUBLISHED).count(),
                    "link": "/admin/media_content/videopost/",
                },
                {
                    "title": "Mensajes nuevos",
                    "value": ContactMessage.objects.filter(is_read=False).count(),
                    "link": "/admin/contact/contactmessage/?is_read__exact=0",
                },
                {
                    "title": "Suscriptores activos",
                    "value": Subscriber.objects.filter(is_active=True).count(),
                    "link": "/admin/newsletter/subscriber/?is_active__exact=1",
                },
            ],
        }
    )
    return context
