"""Generadores de datos estructurados (capítulo 10.2 de las especificaciones).

Cada función devuelve un diccionario listo para serializar como JSON-LD.
Las vistas arman el `@graph` de su página y la plantilla base lo imprime.
La descripción de la persona va en tercera persona, como pide el documento.
"""

from django.templatetags.static import static

PERSON_ID = "#angela-montiel"
WEBSITE_ID = "#website"


def _d(value):
    return value.isoformat() if hasattr(value, "isoformat") else value


def person_id(site):
    return site.absolute(f"/{PERSON_ID}")


def person_graph(site, about):
    credentials = []
    alumni = []
    for edu in about.education.all():
        if edu.institution and edu.institution not in alumni:
            alumni.append(edu.institution)
        if edu.category == "in_progress":
            continue
        credentials.append(
            {
                "@type": "EducationalOccupationalCredential",
                "credentialCategory": "degree" if edu.category == "degree" else "certificate",
                "name": edu.title,
                "recognizedBy": {"@type": "CollegeOrUniversity", "name": edu.institution.split(",")[0].strip()},
            }
        )
    data = {
        "@type": "Person",
        "@id": person_id(site),
        "name": "Ángela Montiel",
        "url": site.absolute("/sobre-mi"),
        "image": site.absolute(about.photo_url) if about.photo_url.startswith("/") else about.photo_url,
        "description": about.person_description or about.in_brief,
        "knowsAbout": about.knows_about_list,
        "address": {"@type": "PostalAddress", "addressCountry": "CL"},
    }
    if alumni:
        data["alumniOf"] = [{"@type": "CollegeOrUniversity", "name": name.split(",")[0].strip()} for name in alumni]
    if credentials:
        data["hasCredential"] = credentials
    if site.same_as:
        data["sameAs"] = site.same_as
    return data


def website_graph(site):
    return {
        "@type": "WebSite",
        "@id": site.absolute(f"/{WEBSITE_ID}"),
        "url": site.absolute("/"),
        "name": site.site_name,
        "inLanguage": "es-CL",
        "publisher": {"@id": person_id(site)},
    }


def breadcrumb_graph(site, items):
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": index + 1,
                "name": item["name"],
                "item": site.absolute(item["url"]) if item["url"].startswith("/") else item["url"],
            }
            for index, item in enumerate(items)
        ],
    }


def webpage_graph(site, path, name, description, date_modified, last_reviewed):
    url = site.absolute(path)
    return {
        "@type": "WebPage",
        "@id": f"{url}#pagina",
        "url": url,
        "name": name,
        "description": description,
        "inLanguage": "es-CL",
        "dateModified": _d(date_modified),
        "author": {"@id": person_id(site)},
        "reviewedBy": {"@id": person_id(site)},
        "lastReviewed": _d(last_reviewed),
    }


def faq_graph(faqs):
    faqs = list(faqs)
    if not faqs:
        return None
    return {
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": faq.question,
                "acceptedAnswer": {"@type": "Answer", "text": faq.answer},
            }
            for faq in faqs
        ],
    }


def article_graph(site, publication, image_url):
    data = {
        "@type": "Article",
        "headline": publication.title,
        "description": publication.lead,
        "datePublished": _d(publication.published_at.date()),
        "dateModified": _d(publication.content_updated_at),
        "inLanguage": "es-CL",
        "author": {"@id": person_id(site)},
        "publisher": {"@id": person_id(site)},
        "image": image_url,
        "mainEntityOfPage": site.absolute(publication.get_absolute_url()),
        "articleSection": publication.get_format_display(),
    }
    citations = [source.url for source in publication.sources.all() if source.url]
    if citations:
        data["citation"] = citations
    return data


def video_graph(site, video):
    thumb = video.thumbnail_url
    if thumb.startswith("/"):
        thumb = site.absolute(thumb)
    return {
        "@type": "VideoObject",
        "name": video.title,
        "description": video.summary,
        "thumbnailUrl": [thumb] if thumb else [],
        "uploadDate": _d(video.published_at.date()),
        "duration": video.duration_iso,
        "embedUrl": f"https://www.youtube-nocookie.com/embed/{video.youtube_id}",
        "contentUrl": video.watch_url,
        "transcript": video.transcript,
        "inLanguage": "es-CL",
        "author": {"@id": person_id(site)},
        "publisher": {"@id": person_id(site)},
        "mainEntityOfPage": site.absolute(video.get_absolute_url()),
    }


def graph(*items):
    return {"@context": "https://schema.org", "@graph": [item for item in items if item]}


def default_og_image(site):
    if site.default_og_image:
        return site.absolute(site.default_og_image.url)
    return site.absolute(static("images/angela-banner1.jpg"))


def page_meta(site, *, title, description, path, og_type="website", og_image=None, noindex=False):
    return {
        "title": title,
        "description": description,
        "canonical": site.absolute(path),
        "og_type": og_type,
        "og_image": og_image or default_og_image(site),
        "noindex": noindex,
    }
