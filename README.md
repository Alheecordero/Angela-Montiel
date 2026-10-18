# angelamontiel.cl

Sitio profesional de Ángela Montiel. Derecho societario, reorganizaciones empresariales y tributario en Chile.

Dominio canónico `https://angelamontiel.cl` (apex, `www` redirige). URL públicas sin barra final. Idioma `es-CL`.

## Stack

- Django 5.2 con django-unfold (admin) y django-ckeditor-5 (cuerpo de publicaciones)
- SQLite en desarrollo, PostgreSQL en producción
- whitenoise para estáticos, gunicorn tras nginx (ver `deploy/`)
- Frontend propio en `static/css` y `static/js` (sin build). `content.css` y `content.js` son la capa de contenidos; `main.css`, `studio.css`, `main.js` y `studio.js` conservan la línea estética original

## Instalación local

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env            # revisar SECRET_KEY
.venv/bin/python manage.py migrate
.venv/bin/python manage.py importar_prototipo   # carga el contenido aprobado
.venv/bin/python manage.py createsuperuser
.venv/bin/python manage.py runserver
```

Sitio en `http://127.0.0.1:8000` y panel en `http://127.0.0.1:8000/admin/`.

## Comandos propios

| Comando | Qué hace |
|---|---|
| `importar_prototipo [--solo configuracion\|areas\|sobre-mi\|glosario\|legales]` | Carga en la base de datos los textos del prototipo aprobado (`docs/prototipo`), los metadatos (`docs/tecnico/metadatos-por-pagina.csv`) y la configuración del sitio. Idempotente. |
| `revisar_sitio [--estricto]` | Audita reglas de marca (dos puntos, tilde en Ángela, corchetes, Inicia Legal, palabra abogada), metadatos, fuentes, FAQ, H1 único, canónica, datos estructurados, correos visibles y barras finales. |
| `optimizar_imagenes [--forzar] [--sin-avif]` | Genera WebP y AVIF de `static/images` (ancho máximo 1920 px). La etiqueta de plantilla `{% webp %}` usa la versión WebP si existe. |

## Pruebas

```bash
.venv/bin/python manage.py test
```

## Estructura

```
apps/
  core/          SiteSettings, AboutPage, LegalPage, SEO (seo.py), middleware de barra final,
                 inicio, sobre mí, legales, robots, llms.txt, importador, revisar_sitio
  practice/      Áreas de práctica y figuras (mapa de reorganizaciones, comparador, FAQ, fuentes)
  publications/  Publicaciones (nota, columna, guía, boletín) y relación con áreas
  videos/        Videos de YouTube con transcripción y VideoObject
  resources/     Glosario y guías descargables
  newsletter/    Boletín con doble verificación (solo visible si está activo)
config/          settings (base, dev, prod), urls, sitemaps
templates/       Plantillas. components/ contiene hero, Ley · Criterio · Riesgo, FAQ, fuentes, cierre
static/          CSS, JS e imágenes
docs/            prototipo HTML aprobado y paquete técnico (metadatos, datos estructurados)
deploy/          nginx, systemd, deploy.sh, setup_server.sh
```

## Mapa de URL

| Ruta | Contenido |
|---|---|
| `/` | Inicio |
| `/sobre-mi` | Sobre mí |
| `/derecho-societario`, `/reorganizaciones-empresariales`, `/derecho-tributario` | Áreas |
| `/fusion-de-sociedades`, `/division-de-sociedades`, … | Figuras, en primer nivel |
| `/publicaciones`, `/publicaciones/<slug>` | Publicaciones |
| `/videos`, `/videos/<slug>` | Videos |
| `/recursos` | Mapa, comparador, glosario y guías |
| `/politica-de-privacidad`, `/terminos-de-uso` | Legales |
| `/boletin/suscribir`, `/boletin/confirmar/<token>`, `/boletin/baja/<token>` | Boletín (404 si está inactivo) |
| `/robots.txt`, `/sitemap.xml`, `/llms.txt` | Solo con `SITE_INDEXABLE=True` |

Las rutas antiguas (`/blog`, `/blog/videos`, `/contacto`, `/newsletter/baja`) redirigen con 301.

## Reglas de contenido que el sistema hace cumplir

- Sin dos puntos en títulos, bajadas y textos cortos visibles (validadores en modelos y `revisar_sitio`).
- Ángela siempre con tilde. Sin corchetes. Sin menciones a Inicia Legal.
- Contacto único por WhatsApp `https://wa.me/56930882307`. Sin formulario de contacto ni correo visible.
- Aclaración fija en todas las páginas. "Información general. Cada empresa requiere análisis particular. — Ángela"
- Un H1 por página, canónica absoluta sin barra final, JSON-LD (Person, WebSite, BreadcrumbList, WebPage, FAQPage, Article, VideoObject).
- Boletín solo en Publicaciones y únicamente si `Configuración del sitio → Boletín` no está en Inactivo.

## Guía para Ángela

- **Sitio → Configuración del sitio.** WhatsApp, línea del encabezado, redes, boletín, tokens de Search Console y Bing.
- **Sitio → Sobre mí.** Textos, principios, formación, foto.
- **Áreas de práctica.** Cada área y cada figura tiene bajada, definición, bloque Ley · Criterio · Riesgo, preguntas frecuentes, fuentes y metadatos. La fecha de actualización se muestra en la página.
- **Publicaciones.** Título, bajada, cuerpo, formato, áreas relacionadas, fuentes e imagen para redes. Estado Borrador o Publicada.
- **Videos.** URL de YouTube, resumen, transcripción, área. El reproductor se carga solo al pulsar.
- **Recursos.** Términos del glosario y guías descargables.

Ejecutar `python manage.py revisar_sitio` antes de cada publicación importante.

## Despliegue

Variables mínimas en `.env` de producción.

```env
DEBUG=False
DJANGO_SETTINGS_MODULE=config.settings.prod
SECRET_KEY=...
ALLOWED_HOSTS=angelamontiel.cl,www.angelamontiel.cl
CSRF_TRUSTED_ORIGINS=https://angelamontiel.cl,https://www.angelamontiel.cl
DATABASE_URL=postgres://...
SECURE_SSL_REDIRECT=True
SITE_INDEXABLE=False
```

`deploy/deploy.sh` instala dependencias, migra, genera WebP/AVIF, recoge estáticos, ejecuta `revisar_sitio` y reinicia gunicorn.

### Lista de lanzamiento

1. `SITE_INDEXABLE=True` en `.env` y reiniciar gunicorn. Activa robots, sitemap, llms.txt y quita `noindex`.
2. Quitar `add_header X-Robots-Tag` de `deploy/nginx/angelamontiel.conf` y recargar nginx.
3. Cargar el token de Search Console en Configuración del sitio y enviar `https://angelamontiel.cl/sitemap.xml`.
4. `python manage.py revisar_sitio --estricto` sin hallazgos.
