import json
import re

from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


@register.simple_tag
def jsonld(data):
    """Imprime un bloque <script type="application/ld+json"> seguro."""
    if not data:
        return ""
    payload = json.dumps(data, ensure_ascii=False, indent=2).replace("</", "<\\/")
    return mark_safe(f'<script type="application/ld+json">\n{payload}\n</script>')


@register.simple_tag(takes_context=True)
def whatsapp(context, message=""):
    """URL de WhatsApp con mensaje inicial opcional (capítulo 5.3)."""
    site = context.get("site_settings")
    if site is None:
        return "https://wa.me/56930882307"
    return site.whatsapp_link(message)


@register.filter
def fecha_larga(value):
    """18 de octubre de 2026, sin depender de la configuración regional del servidor."""
    if not value:
        return ""
    if hasattr(value, "date"):
        value = value.date() if hasattr(value, "hour") else value
    return f"{value.day} de {MESES[value.month - 1]} de {value.year}"


@register.filter
def fecha_corta(value):
    """18 oct 2026."""
    if not value:
        return ""
    return f"{value.day} {MESES[value.month - 1][:3]} {value.year}"


_INLINE_TAGS = ("strong", "em", "sup", "sub", "br")
_INLINE_RE = re.compile(r"&lt;(/?)(" + "|".join(_INLINE_TAGS) + r")&gt;")


def _inline(texto):
    """Escapa todo salvo las etiquetas de énfasis permitidas en texto corto."""
    return _INLINE_RE.sub(r"<\1\2>", escape(str(texto)))


@register.filter
def enfasis(value):
    """Permite <strong>, <em>, <sup> y <sub> en un campo de una línea."""
    if not value:
        return ""
    return mark_safe(_inline(value))


@register.filter
def parrafos(value):
    """Convierte texto con líneas en blanco en párrafos <p>, conservando énfasis."""
    if not value:
        return ""
    partes = [p.strip() for p in str(value).split("\n\n") if p.strip()]
    return mark_safe("".join(f"<p>{_inline(p)}</p>" for p in partes))


@register.simple_tag
def webp(path):
    """URL estática de la versión WebP si existe; si no, la original.

    Uso. {% webp 'images/museum-hall.jpg' %}
    """
    from pathlib import Path

    from django.conf import settings
    from django.templatetags.static import static

    candidato = str(Path(path).with_suffix(".webp"))
    for base in getattr(settings, "STATICFILES_DIRS", []):
        if (Path(base) / candidato).exists():
            return static(candidato)
    return static(path)


@register.filter
def romano(value):
    from apps.practice.models import romano as _romano

    try:
        return _romano(int(value))
    except (TypeError, ValueError):
        return value
