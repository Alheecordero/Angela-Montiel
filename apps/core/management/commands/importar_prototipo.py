"""Carga el contenido verificado del prototipo en la base de datos.

Lee los HTML de `docs/prototipo/` y los archivos de `docs/tecnico/` para que
los textos jurídicos queden idénticos a los aprobados, sin transcripción
manual. Es idempotente. Se puede ejecutar de nuevo para restaurar los textos.

    python manage.py importar_prototipo
    python manage.py importar_prototipo --solo areas
"""

import csv
import json
import re
from datetime import date
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.core.models import AboutPage, CredentialCategory, Education, LegalPage, SiteSettings, WorkPrinciple
from apps.practice.models import FAQ, ComparatorRow, PracticeArea, PracticeFigure, ReorgMapOption, TaxPoint, WorkStep
from apps.resources.models import GlossaryTerm

PROTOTIPO = Path(settings.BASE_DIR) / "docs" / "prototipo"
TECNICO = Path(settings.BASE_DIR) / "docs" / "tecnico"

MESES = {m: i + 1 for i, m in enumerate(["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"])}
TAGS_PERMITIDAS = {"strong", "em", "sup", "b", "i"}

AREAS = {
    "reorganizaciones-empresariales": {
        "name": "Reorganizaciones empresariales",
        "short_name": "Reorganizaciones",
        "is_primary": True,
        "order": 0,
        "home_cta": "Usar el mapa de reorganizaciones",
        "figures": [
            ("fusion-de-sociedades", "Fusión de sociedades", "Fusión", "Fusión"),
            ("division-de-sociedades", "División de sociedades", "División", "División"),
            ("transformacion-de-sociedades", "Transformación de sociedades", "Transformación", "Transformación"),
            ("aporte-de-bienes", "Aporte de bienes", "Aporte de bienes", "Aporte de bienes"),
            ("conversion-empresario-individual", "Conversión del empresario individual", "Conversión", "Conversión"),
        ],
    },
    "derecho-societario": {
        "name": "Derecho societario",
        "short_name": "Societario",
        "is_primary": False,
        "order": 1,
        "home_cta": "Comparar SA, SpA y limitada",
        "figures": [
            ("constitucion-de-sociedades", "Constitución de sociedades", "Constitución y tipo social", "Constitución y tipo social"),
            ("entrada-y-salida-de-socios", "Entrada y salida de socios", "Entrada y salida de socios", "Entrada y salida de socios"),
            ("pactos-de-accionistas", "Pactos de accionistas", "Pactos de accionistas y socios", "Pactos de accionistas"),
            ("aumento-y-disminucion-de-capital", "Aumento y disminución de capital", "Aumento y disminución de capital", "Aumento y disminución de capital"),
        ],
    },
}


# ---------------------------------------------------------------- utilidades


def limpiar(texto):
    return re.sub(r"\s+", " ", texto or "").strip()


def txt(el):
    return limpiar(el.get_text(" ", strip=True)) if el else ""


def inline(el):
    """Serializa el contenido conservando solo énfasis (strong, em, sup)."""
    if el is None:
        return ""
    partes = []
    for nodo in el.children:
        if isinstance(nodo, NavigableString):
            partes.append(str(nodo))
        elif nodo.name in TAGS_PERMITIDAS:
            nombre = {"b": "strong", "i": "em"}.get(nodo.name, nodo.name)
            partes.append(f"<{nombre}>{inline(nodo)}</{nombre}>")
        else:
            partes.append(inline(nodo))
    return limpiar("".join(partes))


def sin_em_titulo(el):
    """Los títulos llevan una palabra en itálica por identidad visual; aquí van planos."""
    return txt(el)


def fecha_es(texto):
    m = re.search(r"(\d{1,2}) de ([a-záéíóú]+) de (\d{4})", texto or "", re.IGNORECASE)
    if not m:
        return date.today()
    return date(int(m.group(3)), MESES[m.group(2).lower()], int(m.group(1)))


def leer(nombre):
    ruta = PROTOTIPO / f"{nombre}.html"
    if not ruta.exists():
        raise CommandError(f"No existe {ruta}")
    return BeautifulSoup(ruta.read_text(encoding="utf-8"), "html.parser")


def secciones(soup):
    main = soup.find("main")
    secs = main.find_all("section", recursive=False)
    if not secs:
        wrapper = main.find("div", recursive=False)
        secs = wrapper.find_all("section", recursive=False)
    return secs


def etiqueta(sec):
    el = sec.find("div", style=re.compile(r"letter-spacing: 0\.2[48]em"))
    return txt(el)


def parrafos(sec, excluir=()):
    return [inline(p) for p in sec.find_all("p") if inline(p) and p not in excluir]


def metadatos():
    datos = {}
    with (TECNICO / "metadatos-por-pagina.csv").open(encoding="utf-8-sig") as fh:
        for fila in csv.DictReader(fh):
            datos[fila["Archivo"]] = {"title": fila["Etiqueta title"], "description": fila["Meta descripción"]}
    return datos


# ---------------------------------------------------------------- bloques comunes


def parse_encabezado(sec):
    h1 = sec.find("h1")
    lead = sec.find("p")
    firma = sec.find(string=re.compile("Actualizado el"))
    return {
        "label": etiqueta(sec),
        "title": sin_em_titulo(h1),
        "lead": inline(lead),
        "content_updated_at": fecha_es(str(firma) if firma else ""),
    }


def parse_ley_criterio_riesgo(sec):
    resultado = {"ley": "", "criterio": "", "riesgo": ""}
    claves = {"La ley": "ley", "Mi criterio": "criterio", "El riesgo": "riesgo"}
    for titulo in sec.find_all(string=lambda s: limpiar(s) in claves):
        contenedor = titulo.find_parent(["div", "span"])
        card = contenedor.find_parent("div") if contenedor and contenedor.name == "span" else contenedor.parent
        p = card.find("p") or card.find_all("span")[-1]
        resultado[claves[limpiar(titulo)]] = inline(p)
    return resultado


def parse_faqs(sec):
    faqs = []
    for i, det in enumerate(sec.find_all("details")):
        faqs.append({"order": i, "question": txt(det.find("summary")), "answer": inline(det.find("p"))})
    return faqs


def parse_fuentes(sec):
    ps = sec.find_all("p")
    fuentes = inline(ps[0]) if ps else ""
    verificado = txt(ps[1]) if len(ps) > 1 else ""
    return fuentes, fecha_es(verificado)


def parse_cierre(sec):
    p = sec.find("p")
    return txt(p)


# ---------------------------------------------------------------- figuras


def parse_figura(slug):
    soup = leer(slug)
    secs = secciones(soup)
    datos = parse_encabezado(secs[0])

    definicion = secs[1]
    ps = definicion.find_all("p")
    datos["definition_label"] = etiqueta(definicion)
    datos["definition_lead"] = inline(ps[0])
    datos["definition_body"] = "\n\n".join(inline(p) for p in ps[1:])

    columnas = secs[2]
    cards = columnas.find("div", recursive=False).find_all("div", recursive=False)
    societario, tributario = cards[0], cards[1]
    bloques = {}
    for titulo in societario.find_all("div", style=re.compile("font-style: italic; font-size: 22px")):
        p = titulo.find_next_sibling("p")
        bloques[limpiar(titulo.get_text())] = inline(p)
    datos["sa"] = bloques.get("Sociedad anónima", "")
    datos["spa"] = bloques.get("Sociedad por acciones", "")
    datos["ltda"] = bloques.get("Sociedad de responsabilidad limitada", "")
    nota = societario.find("p", style=re.compile("color: #6B7280"))
    datos["societario_note"] = inline(nota)

    puntos = []
    for i, fila in enumerate(tributario.find_all("div", style=re.compile(r"display: flex; gap: 18px"))):
        p = fila.find("p")
        strong = p.find("strong")
        titulo = limpiar(strong.get_text()).rstrip(".") if strong else f"Punto {i + 1}"
        if strong:
            strong.extract()
        puntos.append({"order": i, "title": titulo, "text": inline(p)})
    datos["tax_points"] = puntos

    datos.update(parse_ley_criterio_riesgo(secs[3]))
    datos["faqs"] = parse_faqs(secs[4])
    datos["sources"], datos["verified_at"] = parse_fuentes(secs[6])
    datos["closing_question"] = parse_cierre(secs[7])
    return datos


# ---------------------------------------------------------------- áreas


def parse_area(slug):
    soup = leer(slug)
    secs = secciones(soup)
    datos = parse_encabezado(secs[0])

    herramienta = secs[1]
    datos["tool_label"] = etiqueta(herramienta)
    datos["tool_title"] = sin_em_titulo(herramienta.find("h2"))
    intro = herramienta.find("p")
    datos["tool_intro"] = inline(intro)
    datos["tool_note"] = ""
    datos["map_options"] = []
    datos["comparator_rows"] = []

    script = soup.find("script", string=re.compile(r"var data = "))
    if script:
        bruto = re.search(r"var data = (\[.*?\]);", script.string, re.S).group(1)
        for i, opt in enumerate(json.loads(bruto)):
            datos["map_options"].append(
                {
                    "order": i,
                    "question": opt["q"],
                    "figure_slug": opt["page"].replace(".html", ""),
                    "name": opt["name"],
                    "description": opt["para"],
                    "attention_point": opt["atencion"],
                }
            )

    tabla = herramienta.find("table")
    if tabla:
        for i, tr in enumerate(tabla.find("tbody").find_all("tr") if tabla.find("tbody") else tabla.find_all("tr")[1:]):
            th = tr.find("th")
            tds = tr.find_all("td")
            if th and len(tds) == 3:
                datos["comparator_rows"].append({"order": i, "criterion": txt(th), "sa": inline(tds[0]), "spa": inline(tds[1]), "ltda": inline(tds[2])})
        notas = [p for p in herramienta.find_all("p") if p is not intro]
        if notas:
            datos["tool_note"] = inline(notas[-1])

    figuras = secs[2]
    datos["figures_label"] = etiqueta(figuras)
    datos["figures_title"] = sin_em_titulo(figuras.find("h2"))
    datos["figure_cards"] = {}
    for a in figuras.find_all("a", href=re.compile(r"\.html$")):
        spans = a.find_all("span")
        if len(spans) >= 3:
            datos["figure_cards"][a["href"].replace(".html", "")] = {"card_title": txt(spans[1]), "card_text": inline(spans[2])}

    tax = secs[3]
    datos["tax_label"] = etiqueta(tax)
    datos["tax_title"] = sin_em_titulo(tax.find("h2"))
    datos["tax_text"] = "\n\n".join(parrafos(tax))

    datos.update(parse_ley_criterio_riesgo(secs[4]))

    como = secs[5]
    datos["how_label"] = etiqueta(como)
    datos["work_steps"] = []
    for i, fila in enumerate(como.find_all("div", style=re.compile(r"display: flex; gap: 24px"))):
        textos = fila.find_all("div", recursive=False)
        datos["work_steps"].append({"order": i, "text": inline(textos[-1])})

    datos["faqs"] = parse_faqs(secs[6])
    datos["sources"], datos["verified_at"] = parse_fuentes(secs[8])
    datos["closing_question"] = parse_cierre(secs[9])
    return datos


def descripcion_inicio(soup_index, slug):
    for a in soup_index.find_all("a", href=f"{slug}.html"):
        card = a.find_parent("div")
        p = card.find("p") if card else None
        if p:
            return inline(p)
    return ""


# ---------------------------------------------------------------- sobre mí


def importar_sobre_mi(stdout):
    soup = leer("sobre-mi")
    secs = secciones(soup)
    about = AboutPage.load()

    enc = secs[0]
    about.label = etiqueta(enc)
    about.title = sin_em_titulo(enc.find("h1"))
    about.lead = inline(enc.find("p"))
    img = enc.find("img")
    if img and img.get("alt"):
        about.photo_alt = img["alt"]

    hago = secs[1]
    about.what_i_do_label = etiqueta(hago)
    about.what_i_do_title = sin_em_titulo(hago.find("h2"))
    about.what_i_do_text = "".join(f"<p>{inline(p)}</p>" for p in hago.find_all("p"))

    como = secs[2]
    about.how_i_work_label = etiqueta(como)
    about.how_i_work_title = sin_em_titulo(como.find("h2"))
    about.principles.all().delete()
    filas = como.find_all("div", style=re.compile(r"display: flex; gap: 24px"))
    for i, fila in enumerate(filas):
        bloques = fila.find_all("div", recursive=False)
        textos = bloques[-1].find_all(["div", "span", "p"])
        titulo = txt(textos[0]) if textos else ""
        cuerpo = inline(textos[1]) if len(textos) > 1 else ""
        WorkPrinciple.objects.create(page=about, order=i, title=titulo, text=cuerpo)

    formacion = secs[3]
    about.education_label = etiqueta(formacion)
    about.education_title = sin_em_titulo(formacion.find("h2"))
    about.education.all().delete()
    filas = formacion.find_all("div", style=re.compile(r"align-items: baseline"))
    orden = 0
    for fila in filas:
        partes = [txt(x) for x in fila.find_all("div", recursive=False) if txt(x)]
        if len(partes) < 3:
            continue
        year, titulo, inst = partes[0], partes[1], partes[2]
        if year.lower().startswith("en curso"):
            cat = CredentialCategory.IN_PROGRESS
        elif titulo.lower().startswith("abogad"):
            cat = CredentialCategory.DEGREE
        else:
            cat = CredentialCategory.CERTIFICATE
        Education.objects.create(page=about, order=orden, year=year, title=titulo, institution=inst, category=cat)
        orden += 1

    breve = secs[4]
    about.in_brief_label = etiqueta(breve)
    about.in_brief = inline(breve.find("p"))

    ruta_json = TECNICO / "datos-estructurados" / "sobre-mi.json"
    if ruta_json.exists():
        datos = json.loads(ruta_json.read_text(encoding="utf-8"))
        for nodo in datos.get("@graph", []):
            if nodo.get("@type") == "Person":
                about.person_description = nodo.get("description", about.person_description)
                if nodo.get("knowsAbout"):
                    about.knows_about = "\n".join(nodo["knowsAbout"])

    meta = metadatos().get("sobre-mi")
    if meta:
        about.meta_title = meta["title"]
        about.meta_description = meta["description"]
    about.full_clean(exclude=["photo"])
    about.save()
    stdout.write(f"  Sobre mí · {about.principles.count()} principios · {about.education.count()} estudios")


# ---------------------------------------------------------------- glosario


def importar_glosario(stdout):
    soup = leer("recursos")
    n = 0
    for i, fila in enumerate(soup.find_all("div", attrs={"data-search": True})):
        bloques = fila.find_all("div", recursive=False)
        termino = txt(bloques[0])
        definicion = inline(bloques[1].find("span")) if len(bloques) > 1 else ""
        if not termino or not definicion:
            continue
        obj, _ = GlossaryTerm.objects.update_or_create(term=termino, defaults={"definition": definicion, "order": i})
        obj.full_clean()
        n += 1
    stdout.write(f"  Glosario · {n} términos")


# ---------------------------------------------------------------- legales


def importar_legales(stdout):
    meta = metadatos()
    for slug, titulo in (("politica-de-privacidad", "Política de privacidad."), ("terminos-de-uso", "Términos de uso.")):
        soup = leer(slug)
        h1 = soup.find("h1")
        LegalPage.objects.update_or_create(
            slug=slug,
            defaults={"title": txt(h1) or titulo, "meta_description": meta.get(slug, {}).get("description", "")},
        )
    stdout.write("  Páginas legales · 2 (texto pendiente de Ángela)")


# ---------------------------------------------------------------- áreas y figuras


def importar_areas(stdout):
    meta = metadatos()
    soup_index = leer("index")
    for slug, cfg in AREAS.items():
        datos = parse_area(slug)
        area, _ = PracticeArea.objects.update_or_create(
            slug=slug,
            defaults={
                "name": cfg["name"],
                "short_name": cfg["short_name"],
                "is_primary": cfg["is_primary"],
                "order": cfg["order"],
                "label": datos["label"],
                "title": datos["title"],
                "lead": datos["lead"],
                "content_updated_at": datos["content_updated_at"],
                "home_description": descripcion_inicio(soup_index, slug),
                "home_cta": cfg["home_cta"],
                "tool_label": datos["tool_label"],
                "tool_title": datos["tool_title"],
                "tool_intro": datos["tool_intro"],
                "tool_note": datos["tool_note"],
                "figures_label": datos["figures_label"],
                "figures_title": datos["figures_title"],
                "tax_label": datos["tax_label"],
                "tax_title": datos["tax_title"],
                "tax_text": datos["tax_text"],
                "ley": datos["ley"],
                "criterio": datos["criterio"],
                "riesgo": datos["riesgo"],
                "how_label": datos["how_label"],
                "sources": datos["sources"],
                "verified_at": datos["verified_at"],
                "closing_question": datos["closing_question"],
                "meta_title": meta[slug]["title"],
                "meta_description": meta[slug]["description"],
            },
        )
        area.full_clean()
        area.work_steps.all().delete()
        for paso in datos["work_steps"]:
            WorkStep.objects.create(area=area, **paso)
        area.faqs.all().delete()
        for faq in datos["faqs"]:
            FAQ.objects.create(area=area, **faq)
        area.comparator_rows.all().delete()
        for fila in datos["comparator_rows"]:
            ComparatorRow.objects.create(area=area, **fila)

        for order, (fslug, name, short_name, menu_name) in enumerate(cfg["figures"]):
            fdatos = parse_figura(fslug)
            card = datos["figure_cards"].get(fslug, {})
            figura, _ = PracticeFigure.objects.update_or_create(
                slug=fslug,
                defaults={
                    "area": area,
                    "order": order,
                    "name": name,
                    "short_name": short_name,
                    "menu_name": menu_name,
                    "card_text": card.get("card_text", fdatos["definition_lead"]),
                    "label": fdatos["label"],
                    "title": fdatos["title"],
                    "lead": fdatos["lead"],
                    "content_updated_at": fdatos["content_updated_at"],
                    "definition_label": fdatos["definition_label"],
                    "definition_lead": fdatos["definition_lead"],
                    "definition_body": fdatos["definition_body"],
                    "sa": fdatos["sa"],
                    "spa": fdatos["spa"],
                    "ltda": fdatos["ltda"],
                    "societario_note": fdatos["societario_note"],
                    "ley": fdatos["ley"],
                    "criterio": fdatos["criterio"],
                    "riesgo": fdatos["riesgo"],
                    "sources": fdatos["sources"],
                    "verified_at": fdatos["verified_at"],
                    "closing_question": fdatos["closing_question"],
                    "meta_title": meta[fslug]["title"],
                    "meta_description": meta[fslug]["description"],
                },
            )
            figura.full_clean()
            figura.tax_points.all().delete()
            for punto in fdatos["tax_points"]:
                TaxPoint.objects.create(figure=figura, **punto)
            figura.faqs.all().delete()
            for faq in fdatos["faqs"]:
                FAQ.objects.create(figure=figura, **faq)
            stdout.write(f"    {figura.name} · {len(fdatos['tax_points'])} puntos tributarios · {len(fdatos['faqs'])} FAQ")

        area.map_options.all().delete()
        for opt in datos["map_options"]:
            figura = PracticeFigure.objects.get(slug=opt.pop("figure_slug"))
            ReorgMapOption.objects.create(area=area, figure=figura, **opt)
        stdout.write(
            f"  {area.name} · {area.figures.count()} figuras · {area.map_options.count()} opciones de mapa · {area.comparator_rows.count()} filas de comparador"
        )


def importar_configuracion(stdout):
    site = SiteSettings.load()
    meta = metadatos().get("index")
    if meta:
        site.meta_title = meta["title"]
        site.meta_description = meta["description"]
    site.full_clean(exclude=["default_og_image"])
    site.save()
    stdout.write("  Configuración · metadatos del inicio")


class Command(BaseCommand):
    help = "Importa el contenido verificado del prototipo (docs/prototipo y docs/tecnico)."

    def add_arguments(self, parser):
        parser.add_argument("--solo", choices=["configuracion", "areas", "sobre-mi", "glosario", "legales"], help="Importa solo una parte.")

    @transaction.atomic
    def handle(self, *args, **options):
        if not PROTOTIPO.exists():
            raise CommandError(f"No existe la carpeta {PROTOTIPO}")
        solo = options.get("solo")
        pasos = [
            ("configuracion", importar_configuracion),
            ("areas", importar_areas),
            ("sobre-mi", importar_sobre_mi),
            ("glosario", importar_glosario),
            ("legales", importar_legales),
        ]
        self.stdout.write("Importando el prototipo…")
        for clave, fn in pasos:
            if solo and clave != solo:
                continue
            fn(self.stdout)
        self.stdout.write(self.style.SUCCESS("Listo."))
