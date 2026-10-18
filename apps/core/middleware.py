from django.conf import settings
from django.http import HttpResponsePermanentRedirect

# Rutas que conservan la barra (convención de Django) o que ya tienen una
# redirección propia hacia la estructura nueva (rutas heredadas del sitio anterior).
PREFIJOS_CON_BARRA = ("/admin/", "/ckeditor5/", "/static/", "/media/", "/blog/", "/contacto/", "/newsletter/")


class NoIndexMiddleware:
    """Evita indexación mientras el sitio está en desarrollo."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if not settings.SITE_INDEXABLE:
            response["X-Robots-Tag"] = "noindex, nofollow, noarchive"
        return response


class TrailingSlashRedirectMiddleware:
    """Las URL definitivas no llevan barra final (capítulo 3).

    Responde 301 de /ruta/ a /ruta, salvo en el admin, el editor y los
    archivos estáticos, que conservan la convención de Django.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        if len(path) > 1 and path.endswith("/") and not path.startswith(PREFIJOS_CON_BARRA) and request.method in ("GET", "HEAD"):
            new_path = path.rstrip("/")
            query = request.META.get("QUERY_STRING", "")
            return HttpResponsePermanentRedirect(f"{new_path}?{query}" if query else new_path)
        return self.get_response(request)
