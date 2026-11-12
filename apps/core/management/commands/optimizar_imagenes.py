"""Genera versiones WebP y AVIF de las imágenes estáticas.

Las imágenes decorativas del sitio pesan varios megas en PNG. Este comando
crea junto a cada original una versión redimensionada (ancho máximo 1920 px)
en WebP y AVIF, y otra de 800 px (nombre-800.webp y nombre-800.avif) para
tarjetas y pantallas chicas. La etiqueta `webp` de las plantillas usa la versión
WebP cuando existe y `foto` arma el <picture> con ambos tamaños. Es idempotente
y solo regenera lo que falta o está desactualizado.

    python manage.py optimizar_imagenes
    python manage.py optimizar_imagenes --forzar
"""

from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from PIL import Image, features

ORIGENES = (".png", ".jpg", ".jpeg")
ANCHO_MAX = 1920
ANCHO_CHICO = 800
CALIDAD_WEBP = 78
CALIDAD_AVIF = 55


class Command(BaseCommand):
    help = "Crea versiones WebP y AVIF de static/images."

    def add_arguments(self, parser):
        parser.add_argument("--forzar", action="store_true", help="Regenera aunque ya existan.")
        parser.add_argument("--sin-avif", action="store_true", help="Omite AVIF.")

    def handle(self, *args, **options):
        carpeta = Path(settings.BASE_DIR) / "static" / "images"
        avif = not options["sin_avif"] and features.check("avif")
        generadas = 0
        for ruta in sorted(carpeta.iterdir()):
            if ruta.suffix.lower() not in ORIGENES or ruta.name.startswith("logo"):
                continue
            chica = ruta.with_name(f"{ruta.stem}-{ANCHO_CHICO}{ruta.suffix}")
            destinos = [(ruta.with_suffix(ext), ANCHO_MAX) for ext in (".webp", ".avif") if ext == ".webp" or avif]
            destinos += [(chica.with_suffix(ext), ANCHO_CHICO) for ext in (".webp", ".avif") if ext == ".webp" or avif]
            pendientes = [(d, a) for d, a in destinos if options["forzar"] or not d.exists() or d.stat().st_mtime < ruta.stat().st_mtime]
            if not pendientes:
                continue
            with Image.open(ruta) as original:
                original = original.convert("RGBA") if original.mode in ("P", "LA") else original
                for destino, ancho in pendientes:
                    if ancho == ANCHO_CHICO and original.width <= ANCHO_CHICO:
                        continue
                    img = original
                    if img.width > ancho:
                        img = img.resize((ancho, round(img.height * ancho / img.width)), Image.LANCZOS)
                    if destino.suffix == ".webp":
                        img.save(destino, "WEBP", quality=CALIDAD_WEBP, method=6)
                    else:
                        img.convert("RGB").save(destino, "AVIF", quality=CALIDAD_AVIF)
                    generadas += 1
                    self.stdout.write(f"  {destino.name} · {destino.stat().st_size // 1024} KB (original {ruta.stat().st_size // 1024} KB)")
        self.stdout.write(self.style.SUCCESS(f"Listo. {generadas} archivos generados."))
