import json
import re
from functools import lru_cache

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


@register.simple_tag
def imagen_por_slug(prefijo, slug, respaldo):
    """Ruta de la foto propia de un área o figura, o la de respaldo si no tiene.

    Las fotos viven en static/images/<prefijo>-<slug>.jpg. Si se crea una figura
    nueva sin foto, se usa la imagen de respaldo y la página no se rompe.

    Uso. {% imagen_por_slug 'figura' figure.slug 'images/study-desk.jpg' as foto %}
    """
    from pathlib import Path

    from django.conf import settings

    ruta = f"images/{prefijo}-{slug}.jpg"
    for base in getattr(settings, "STATICFILES_DIRS", []):
        if (Path(base) / ruta).exists():
            return ruta
    return respaldo


def _archivo_estatico(relativa):
    """Ruta en disco de un archivo de static/, o None si no existe."""
    from pathlib import Path

    from django.conf import settings

    for base in getattr(settings, "STATICFILES_DIRS", []):
        candidato = Path(base) / relativa
        if candidato.exists():
            return candidato
    return None


def _ancho_imagen(ruta):
    """Ancho en píxeles leyendo solo la cabecera del archivo (con caché por fecha)."""
    try:
        return _ancho_en_cache(str(ruta), ruta.stat().st_mtime)
    except OSError:
        return None


@lru_cache(maxsize=512)
def _ancho_en_cache(ruta, _mtime):
    from PIL import Image

    try:
        with Image.open(ruta) as img:
            return img.width
    except Exception:
        return None


@register.simple_tag
def foto(path, alt="", sizes="100vw", clase="", carga="lazy", ancho="", alto="", prioridad=""):
    """<picture> con AVIF y WebP en dos tamaños (800 px y hasta 1920 px).

    El navegador elige el formato y el tamaño según la pantalla. Usa las versiones
    que genera `optimizar_imagenes`; si faltan, cae a la imagen original.

    Uso. {% foto 'images/museum-hall.jpg' sizes='(max-width: 768px) 90vw, 380px' %}
    """
    from pathlib import Path

    from django.templatetags.static import static
    from django.utils.html import format_html

    original = Path(path)
    chica = original.with_name(f"{original.stem}-800{original.suffix}")

    def candidatos(ext):
        partes = []
        for variante in (chica, original):
            relativa = str(variante.with_suffix(ext))
            disco = _archivo_estatico(relativa)
            if disco:
                ancho_real = _ancho_imagen(disco)
                if ancho_real:
                    partes.append(f"{static(relativa)} {ancho_real}w")
        return ", ".join(partes)

    avif = candidatos(".avif")
    webp_srcset = candidatos(".webp")
    src = webp(path)
    fuente = format_html('<source type="image/avif" srcset="{}" sizes="{}">', avif, sizes) if avif else ""
    atributos = format_html(
        ' alt="{}"{}{}{}{}{}',
        alt,
        format_html(' class="{}"', clase) if clase else "",
        format_html(' width="{}" height="{}"', ancho, alto) if ancho and alto else "",
        format_html(' loading="{}" decoding="async"', carga) if carga else "",
        format_html(' fetchpriority="{}"', prioridad) if prioridad else "",
        format_html(' srcset="{}" sizes="{}"', webp_srcset, sizes) if webp_srcset else "",
    )
    return format_html('<picture class="foto">{}<img src="{}"{}></picture>', fuente, src, atributos)


@register.filter
def miniatura(campo, ancho=900):
    """URL de una copia WebP reducida de una imagen subida desde el panel.

    La copia se crea la primera vez que se pide, junto al archivo original
    (por ejemplo publicaciones/foto-900.webp), y se reutiliza después. Si algo
    falla, devuelve la imagen original para que la página nunca quede sin foto.

    Uso. {{ pub.image|miniatura:900 }}
    """
    from pathlib import Path

    if not campo:
        return ""
    try:
        ancho = int(ancho)
        origen = Path(campo.path)
        destino = origen.with_name(f"{origen.stem}-{ancho}.webp")
        if not destino.exists() or destino.stat().st_mtime < origen.stat().st_mtime:
            from PIL import Image

            with Image.open(origen) as img:
                img = img.convert("RGB")
                if img.width > ancho:
                    img = img.resize((ancho, round(img.height * ancho / img.width)), Image.LANCZOS)
                img.save(destino, "WEBP", quality=78, method=6)
        return campo.storage.url(str(Path(campo.name).with_name(destino.name)))
    except Exception:
        try:
            return campo.url
        except Exception:
            return ""


@register.filter
def romano(value):
    from apps.practice.models import romano as _romano

    try:
        return _romano(int(value))
    except (TypeError, ValueError):
        return value
