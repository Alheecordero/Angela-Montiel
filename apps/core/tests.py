"""Pruebas de estructura del sitio. Cargan el prototipo una vez por clase."""

import json
import re
from io import StringIO

from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import Client, TestCase, override_settings
from django.utils import timezone

from apps.core.models import LegalPage, SiteSettings
from apps.core.validators import angela_con_tilde, sin_corchetes, sin_dos_puntos, sin_inicia_legal
from apps.practice.models import PracticeArea, PracticeFigure
from apps.publications.models import Publication, PublicationFormat, PublishStatus
from apps.videos.models import Video

URLS_FIJAS = ["/", "/sobre-mi", "/publicaciones", "/videos", "/recursos", "/politica-de-privacidad", "/terminos-de-uso"]


def jsonld_de(html):
    bloques = re.findall(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', html, re.S)
    return [json.loads(b) for b in bloques]


class ImportadorMixin:
    @classmethod
    def setUpTestData(cls):
        call_command("importar_prototipo", stdout=StringIO())
        cls.area = PracticeArea.objects.get(slug="reorganizaciones-empresariales")
        cls.figure = PracticeFigure.objects.get(slug="fusion-de-sociedades")


@override_settings(ALLOWED_HOSTS=["*"])
class ImportadorTests(ImportadorMixin, TestCase):
    def test_carga_areas_figuras_y_glosario(self):
        from apps.resources.models import GlossaryTerm

        self.assertEqual(PracticeArea.objects.count(), 2)
        self.assertEqual(PracticeFigure.objects.count(), 9)
        self.assertEqual(self.area.map_options.count(), 5)
        self.assertEqual(PracticeArea.objects.get(slug="derecho-societario").comparator_rows.count(), 6)
        self.assertEqual(GlossaryTerm.objects.count(), 13)
        self.assertEqual(LegalPage.objects.count(), 2)

    def test_textos_sin_corchetes_ni_dos_puntos(self):
        for figura in PracticeFigure.objects.all():
            for campo in ("title", "lead", "closing_question", "card_text"):
                valor = getattr(figura, campo)
                self.assertNotIn(":", valor, f"{figura.slug}.{campo}")
                self.assertNotIn("[", valor, f"{figura.slug}.{campo}")

    def test_es_idempotente(self):
        call_command("importar_prototipo", stdout=StringIO())
        self.assertEqual(PracticeFigure.objects.count(), 9)
        self.assertEqual(self.figure.tax_points.count(), 7)


@override_settings(ALLOWED_HOSTS=["*"])
class RutasTests(ImportadorMixin, TestCase):
    def setUp(self):
        self.client = Client()

    def test_paginas_responden_con_un_solo_h1_y_jsonld(self):
        urls = URLS_FIJAS + [a.get_absolute_url() for a in PracticeArea.objects.all()] + [f.get_absolute_url() for f in PracticeFigure.objects.all()]
        for url in urls:
            with self.subTest(url=url):
                r = self.client.get(url)
                self.assertEqual(r.status_code, 200)
                html = r.content.decode()
                self.assertEqual(html.count("<h1"), 1)
                self.assertIn('lang="es-CL"', html)
                self.assertIn('<link rel="canonical" href="https://angelamontiel.cl' + ("" if url == "/" else url) + '"', html.replace('href="https://angelamontiel.cl/"', 'href="https://angelamontiel.cl"') if url == "/" else html)
                self.assertTrue(jsonld_de(html))

    def test_canonica_del_inicio(self):
        html = self.client.get("/").content.decode()
        self.assertIn('<link rel="canonical" href="https://angelamontiel.cl/"', html)

    def test_barra_final_redirige_301(self):
        r = self.client.get("/sobre-mi/")
        self.assertEqual(r.status_code, 301)
        self.assertEqual(r["Location"], "/sobre-mi")
        r = self.client.get("/fusion-de-sociedades/?x=1")
        self.assertEqual(r["Location"], "/fusion-de-sociedades?x=1")

    def test_redirecciones_heredadas(self):
        casos = {
            "/blog/": "/publicaciones",
            "/blog": "/publicaciones",
            "/blog/mi-post/": "/publicaciones/mi-post",
            "/blog/videos/": "/videos",
            "/blog/videos/clip": "/videos/clip",
            "/contacto/": "/#conversemos",
        }
        for origen, destino in casos.items():
            with self.subTest(origen=origen):
                r = self.client.get(origen)
                self.assertEqual(r.status_code, 301)
                self.assertEqual(r["Location"], destino)

    def test_404_en_slug_desconocido(self):
        self.assertEqual(self.client.get("/no-existe").status_code, 404)
        self.assertEqual(self.client.get("/publicaciones/no-existe").status_code, 404)

    def test_sin_correo_ni_formulario_de_contacto(self):
        html = self.client.get("/").content.decode()
        self.assertNotIn("mailto:", html)
        self.assertNotIn("Abogada corporativa", html)
        self.assertIn("https://wa.me/56930882307", html)
        self.assertIn("Información general. Cada empresa requiere análisis particular. — Ángela", html)

    def test_area_incluye_faq_en_jsonld(self):
        html = self.client.get(self.area.get_absolute_url()).content.decode()
        tipos = [n["@type"] for n in jsonld_de(html)[0]["@graph"]]
        self.assertIn("FAQPage", tipos)
        self.assertIn("BreadcrumbList", tipos)
        self.assertIn("WebPage", tipos)

    def test_inicio_incluye_person_y_website(self):
        html = self.client.get("/").content.decode()
        grafo = jsonld_de(html)[0]["@graph"]
        persona = next(n for n in grafo if n["@type"] == "Person")
        self.assertEqual(persona["name"], "Ángela Montiel")
        self.assertTrue(persona["description"].startswith("Ángela Montiel es"))
        self.assertIn("WebSite", [n["@type"] for n in grafo])

    @override_settings(SITE_INDEXABLE=False)
    def test_sin_indexar_en_desarrollo(self):
        r = self.client.get("/")
        self.assertEqual(r["X-Robots-Tag"], "noindex, nofollow, noarchive")
        self.assertEqual(self.client.get("/sitemap.xml").status_code, 404)
        self.assertEqual(self.client.get("/llms.txt").status_code, 404)
        self.assertIn("Disallow: /", self.client.get("/robots.txt").content.decode())

    @override_settings(SITE_INDEXABLE=True)
    def test_sitemap_y_llms_cuando_es_indexable(self):
        xml = self.client.get("/sitemap.xml").content.decode()
        self.assertIn("https://angelamontiel.cl/fusion-de-sociedades</loc>", xml)
        self.assertNotIn("/fusion-de-sociedades/</loc>", xml)
        self.assertIn("https://angelamontiel.cl/</loc>", xml)
        llms = self.client.get("/llms.txt").content.decode()
        self.assertIn("# Ángela Montiel", llms)
        self.assertIn("/reorganizaciones-empresariales)", llms)
        self.assertIn("Sitemap: https://angelamontiel.cl/sitemap.xml", self.client.get("/robots.txt").content.decode())


@override_settings(ALLOWED_HOSTS=["*"])
class ContenidoTests(ImportadorMixin, TestCase):
    def crear_publicacion(self, **extra):
        datos = dict(
            title="Nueva circular del SII sobre fusiones",
            format=PublicationFormat.NOTA,
            lead="Qué cambia para tu empresa con la nueva circular.",
            summary="La circular precisa el tratamiento de las pérdidas en una fusión.",
            body="<h2>El contexto</h2><p>Texto del cuerpo.</p>",
            image_alt="Portada de la nota",
            status=PublishStatus.PUBLISHED,
            published_at=timezone.now(),
        )
        datos.update(extra)
        pub = Publication.objects.create(**datos)
        pub.areas.add(self.area)
        pub.figures.add(self.figure)
        return pub

    def test_publicacion_publicada_y_borrador(self):
        pub = self.crear_publicacion()
        r = self.client.get(pub.get_absolute_url())
        self.assertEqual(r.status_code, 200)
        html = r.content.decode()
        self.assertEqual(html.count("<h1"), 1)
        self.assertIn("Article", [n["@type"] for n in jsonld_de(html)[0]["@graph"]])
        self.assertIn('og:type" content="article"', html)
        borrador = self.crear_publicacion(title="Borrador", slug="borrador", status=PublishStatus.DRAFT)
        self.assertEqual(self.client.get(borrador.get_absolute_url()).status_code, 404)

    def test_inicio_muestra_ultima_nota_y_figura_enlaza_relacionadas(self):
        pub = self.crear_publicacion()
        html = self.client.get("/").content.decode()
        self.assertIn(pub.title, html)
        html = self.client.get(self.figure.get_absolute_url()).content.decode()
        self.assertIn("Para seguir leyendo", html)
        self.assertIn(pub.get_absolute_url(), html)
        html = self.client.get("/publicaciones").content.decode()
        self.assertIn('data-key="nota"', html)

    def test_video_detalle_con_videoobject(self):
        video = Video.objects.create(
            title="Fusión de sociedades en cuatro minutos",
            youtube_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            duration_seconds=272,
            area=self.area,
            summary="Lo esencial de la fusión.",
            transcript="Hola, soy Ángela Montiel. Hoy te explico la fusión.",
            status=PublishStatus.PUBLISHED,
        )
        self.assertEqual(video.youtube_id, "dQw4w9WgXcQ")
        self.assertEqual(video.duration_display, "4 min 32 s")
        self.assertEqual(video.duration_iso, "PT4M32S")
        html = self.client.get(video.get_absolute_url()).content.decode()
        self.assertEqual(html.count("<h1"), 1)
        grafo = jsonld_de(html)[0]["@graph"]
        obj = next(n for n in grafo if n["@type"] == "VideoObject")
        self.assertIn("youtube-nocookie.com/embed/dQw4w9WgXcQ", obj["embedUrl"])
        self.assertIn("Ver transcripción completa", html)
        # Sin canal configurado, el tercer banner del inicio no aparece.
        self.assertNotIn('data-banner-dot="2"', self.client.get("/").content.decode())
        site = SiteSettings.load()
        site.youtube_url = "https://www.youtube.com/@angelamontiel"
        site.save()
        self.assertIn('data-banner-dot="2"', self.client.get("/").content.decode())

    def test_boletin_inactivo_por_defecto(self):
        html = self.client.get("/publicaciones").content.decode()
        self.assertNotIn('id="boletin"', html)
        self.assertEqual(self.client.post("/boletin/suscribir", {"email": "a@b.cl", "consent": "on"}).status_code, 404)

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_boletin_doble_verificacion(self):
        from django.core import mail

        from apps.newsletter.models import Subscriber

        site = SiteSettings.load()
        site.newsletter_mode = "propio"
        site.save()
        html = self.client.get("/publicaciones").content.decode()
        self.assertIn('id="boletin"', html)
        self.assertIn("política de privacidad", html)
        r = self.client.post("/boletin/suscribir", {"email": "Socio@Empresa.cl", "consent": "on", "next": "/publicaciones"})
        self.assertEqual(r.status_code, 302)
        sub = Subscriber.objects.get(email="socio@empresa.cl")
        self.assertFalse(sub.is_active)
        self.assertIsNotNone(sub.consent_at)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(f"/boletin/confirmar/{sub.confirm_token}", mail.outbox[0].body)
        self.assertEqual(self.client.get(f"/boletin/confirmar/{sub.confirm_token}").status_code, 200)
        sub.refresh_from_db()
        self.assertTrue(sub.is_active)
        self.assertEqual(self.client.get(f"/boletin/baja/{sub.unsubscribe_token}").status_code, 200)
        sub.refresh_from_db()
        self.assertFalse(sub.is_active)
        # Sin consentimiento no se registra.
        self.client.post("/boletin/suscribir", {"email": "otro@empresa.cl"})
        self.assertFalse(Subscriber.objects.filter(email="otro@empresa.cl").exists())


class ValidadoresTests(TestCase):
    def test_reglas_de_marca(self):
        with self.assertRaises(ValidationError):
            sin_dos_puntos("Fusión: lo esencial")
        with self.assertRaises(ValidationError):
            angela_con_tilde("Soy Angela Montiel")
        with self.assertRaises(ValidationError):
            sin_corchetes("[Título de la guía]")
        with self.assertRaises(ValidationError):
            sin_inicia_legal("Antes trabajé en Inicia Legal")
        sin_dos_puntos("Fusión de sociedades, lo esencial")
        angela_con_tilde("Ángela Montiel")

    def test_modelo_rechaza_dos_puntos_en_titulo(self):
        call_command("importar_prototipo", "--solo", "areas", stdout=StringIO())
        figura = PracticeFigure.objects.first()
        figura.title = "Fusión: todo lo que debes saber"
        with self.assertRaises(ValidationError):
            figura.full_clean()
