"""Revisión automática de las reglas del sitio antes de publicar.

Recorre los contenidos de la base de datos y las páginas renderizadas y
reporta incumplimientos de las reglas de marca (capítulo 2) y de la capa
técnica (capítulos 3 y 10).

    python manage.py revisar_sitio
    python manage.py revisar_sitio --estricto   # termina con error si hay hallazgos
"""

import re

from django.core.management.base import BaseCommand
from django.test import Client, override_settings
from django.utils.html import strip_tags

from apps.core.models import AboutPage, LegalPage, SiteSettings
from apps.core.validators import PATRON_ANGELA_SIN_TILDE, PATRON_CORCHETES, PATRON_INICIA_LEGAL
from apps.practice.models import PracticeArea, PracticeFigure
from apps.publications.models import Publication
from apps.resources.models import GlossaryTerm
from apps.videos.models import Video

CAMPOS_VISIBLES = {
    PracticeArea: ["title", "lead", "label", "tool_title", "tool_intro", "figures_title", "tax_title", "closing_question", "home_description", "meta_description"],
    PracticeFigure: ["title", "lead", "label", "card_text", "definition_lead", "closing_question", "meta_description"],
    Publication: ["title", "lead", "summary", "highlight", "image_alt"],
    Video: ["title", "summary"],
    GlossaryTerm: ["term", "definition"],
}
PATRON_ABOGADA = re.compile(r"\babogad[ao]\b", re.IGNORECASE)
FORMULA_ABOGADA = "abogada titulada en la Universidad del Zulia"
PATRON_CORREO = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")


class Command(BaseCommand):
    help = "Revisa reglas de marca, SEO y estructura del sitio."

    def add_arguments(self, parser):
        parser.add_argument("--estricto", action="store_true", help="Devuelve código de salida 1 si hay hallazgos.")

    def handle(self, *args, **options):
        self.hallazgos = []
        self.revisar_contenidos()
        self.revisar_paginas()
        if self.hallazgos:
            self.stdout.write(self.style.WARNING(f"\n{len(self.hallazgos)} hallazgos."))
            for h in self.hallazgos:
                self.stdout.write(f"  - {h}")
            if options["estricto"]:
                raise SystemExit(1)
        else:
            self.stdout.write(self.style.SUCCESS("Sin hallazgos. El sitio cumple las reglas revisadas."))

    def anotar(self, texto):
        self.hallazgos.append(texto)

    # ------------------------------------------------------------ contenidos

    def revisar_texto(self, origen, campo, valor, visible=True):
        if not valor:
            return
        plano = strip_tags(str(valor))
        if visible and ":" in plano:
            self.anotar(f"{origen} · {campo} usa dos puntos.")
        if PATRON_ANGELA_SIN_TILDE.search(plano):
            self.anotar(f"{origen} · {campo} escribe Angela sin tilde.")
        if PATRON_CORCHETES.search(plano):
            self.anotar(f"{origen} · {campo} conserva texto entre corchetes del prototipo.")
        if PATRON_INICIA_LEGAL.search(plano):
            self.anotar(f"{origen} · {campo} menciona Inicia Legal.")
        if PATRON_ABOGADA.search(plano) and FORMULA_ABOGADA not in plano and "Abogada" not in plano:
            self.anotar(f"{origen} · {campo} usa la palabra abogada fuera de la formulación aprobada.")

    def revisar_contenidos(self):
        self.stdout.write("Revisando contenidos…")
        for modelo, campos in CAMPOS_VISIBLES.items():
            for obj in modelo.objects.all():
                origen = f"{modelo._meta.verbose_name} «{obj}»"
                for campo in campos:
                    self.revisar_texto(origen, campo, getattr(obj, campo, ""))
                for campo in ("meta_title", "meta_description"):
                    valor = getattr(obj, campo, "")
                    if campo == "meta_description" and valor and not 110 <= len(valor) <= 160:
                        self.anotar(f"{origen} · meta descripción de {len(valor)} caracteres (ideal 110 a 160).")
                    if campo == "meta_title" and valor and len(valor) > 80:
                        self.anotar(f"{origen} · title de {len(valor)} caracteres (sugerido hasta 80).")
                if hasattr(obj, "sources") and isinstance(getattr(obj, "sources"), str) and not obj.sources.strip():
                    self.anotar(f"{origen} · sin fuentes.")

        for figura in PracticeFigure.objects.all():
            if not figura.faqs.exists():
                self.anotar(f"Figura «{figura}» sin preguntas frecuentes.")
            if not figura.tax_points.exists():
                self.anotar(f"Figura «{figura}» sin puntos tributarios.")
            if not figura.has_ley_criterio_riesgo:
                self.anotar(f"Figura «{figura}» sin bloque Ley · Criterio · Riesgo.")

        for pub in Publication.objects.published():
            if not pub.sources.exists():
                self.anotar(f"Publicación «{pub}» publicada sin fuentes.")
            if not pub.image:
                self.anotar(f"Publicación «{pub}» sin imagen para redes.")
            if not pub.areas.exists():
                self.anotar(f"Publicación «{pub}» sin área.")

        for video in Video.objects.published():
            if not video.transcript.strip():
                self.anotar(f"Video «{video}» sin transcripción.")

        about = AboutPage.load()
        self.revisar_texto("Sobre mí", "title", about.title)
        self.revisar_texto("Sobre mí", "lead", about.lead)
        if not about.person_description.startswith("Ángela Montiel es"):
            self.anotar("Sobre mí · la descripción para datos estructurados debe ir en tercera persona.")

        for legal in LegalPage.objects.all():
            if legal.is_published and not strip_tags(legal.body).strip():
                self.anotar(f"Página legal «{legal.title}» publicada sin texto.")

        site = SiteSettings.load()
        if site.whatsapp_number != "56930882307":
            self.anotar("Configuración · el número de WhatsApp difiere del aprobado.")
        if site.canonical_base_url.endswith("/"):
            self.anotar("Configuración · la URL base canónica no debe terminar en barra.")
        if not site.search_console_token:
            self.anotar("Configuración · falta el token de Search Console (necesario para el lanzamiento).")

    # --------------------------------------------------------------- páginas

    @override_settings(ALLOWED_HOSTS=["*"])
    def revisar_paginas(self):
        self.stdout.write("Revisando páginas renderizadas…")
        client = Client()
        urls = ["/", "/sobre-mi", "/publicaciones", "/videos", "/recursos", "/politica-de-privacidad", "/terminos-de-uso"]
        urls += [a.get_absolute_url() for a in PracticeArea.objects.published()]
        urls += [f.get_absolute_url() for f in PracticeFigure.objects.published()]
        urls += [p.get_absolute_url() for p in Publication.objects.published()]
        urls += [v.get_absolute_url() for v in Video.objects.published()]
        for url in urls:
            r = client.get(url, secure=True)
            if r.status_code != 200:
                self.anotar(f"{url} responde {r.status_code}.")
                continue
            html = r.content.decode()
            if html.count("<h1") != 1:
                self.anotar(f"{url} tiene {html.count('<h1')} H1.")
            if 'lang="es-CL"' not in html:
                self.anotar(f"{url} sin lang es-CL.")
            if '<link rel="canonical"' not in html:
                self.anotar(f"{url} sin canónica.")
            if 'application/ld+json' not in html:
                self.anotar(f"{url} sin datos estructurados.")
            if "mailto:" in html or PATRON_CORREO.search(strip_tags(html)):
                self.anotar(f"{url} muestra un correo electrónico.")
            if "<form" in html and "boletin" not in html:
                self.anotar(f"{url} contiene un formulario distinto del boletín.")
            if PATRON_INICIA_LEGAL.search(html):
                self.anotar(f"{url} menciona Inicia Legal.")
            if "Información general. Cada empresa requiere análisis particular." not in html:
                self.anotar(f"{url} sin la aclaración fija.")
            if re.search(r'href="https://angelamontiel\.cl/[^"]+/"', html):
                self.anotar(f"{url} enlaza una URL interna con barra final.")
        self.stdout.write(f"  {len(urls)} páginas revisadas.")
