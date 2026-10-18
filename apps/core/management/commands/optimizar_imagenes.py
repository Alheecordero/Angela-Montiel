"""Genera versiones WebP y AVIF de las imágenes estáticas.

Las imágenes decorativas del sitio pesan varios megas en PNG. Este comando
crea junto a cada original una versión redimensionada (ancho máximo 1920 px)
en WebP y AVIF. El filtro `webp` de las plantillas usa la versión WebP cuando
existe. Es idempotente y solo regenera lo que falta o está desactualizado.

    python manage.py optimizar_imagenes
    python manage.py optimizar_imagenes --forzar
"""

from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from PIL import Image, features

ORIGENES = (".png", ".jpg", ".jpeg")
ANCHO_MAX = 1920
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
            destinos = [ruta.with_suffix(".webp")] + ([ruta.with_suffix(".avif")] if avif else [])
            pendientes = [d for d in destinos if options["forzar"] or not d.exists() or d.stat().st_mtime < ruta.stat().st_mtime]
            if not pendientes:
                continue
            with Image.open(ruta) as img:
                img = img.convert("RGBA") if img.mode in ("P", "LA") else img
                if img.width > ANCHO_MAX:
                    img = img.resize((ANCHO_MAX, round(img.height * ANCHO_MAX / img.width)), Image.LANCZOS)
                for destino in pendientes:
                    if destino.suffix == ".webp":
                        img.save(destino, "WEBP", quality=CALIDAD_WEBP, method=6)
                    else:
                        img.convert("RGB").save(destino, "AVIF", quality=CALIDAD_AVIF)
                    generadas += 1
                    self.stdout.write(f"  {destino.name} · {destino.stat().st_size // 1024} KB (original {ruta.stat().st_size // 1024} KB)")
        self.stdout.write(self.style.SUCCESS(f"Listo. {generadas} archivos generados."))
