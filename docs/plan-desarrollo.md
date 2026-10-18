# Plan de desarrollo · angelamontiel.cl

Basado en `Especificaciones sitio angelamontiel.cl.docx` v1.0 (18 oct 2026), el prototipo `sitio/`, los archivos `tecnico/` y las capturas.

**Alcance acordado.** Se conserva el frontend ya aplicado (paleta navy/oro, Playfair + Outfit, logo AM, carrusel 3D, `main.css`, `studio.css`, `main.js`, `studio.js`). El trabajo se concentra en la estructura de datos, el mapa de URL, el gestor de contenidos, los textos verificados, los datos estructurados y el SEO técnico.

**Discrepancia declarada.** La especificación exige la identidad visual 3.1 (§4), ausencia de logotipo (§5.1) y comparación píxel a píxel con las capturas (§13). Al mantener la estética actual, esos tres puntos no se cumplen. Es una decisión de proyecto que Ángela debe aprobar; todo lo demás del documento (textos, URL, campos, comportamientos, SEO, privacidad) se respeta.

---

## 1. Diagnóstico

**Stack:** Django 5.2 · django-unfold · django-ckeditor-5 · whitenoise · gunicorn · SQLite en dev / PostgreSQL en prod · nginx + systemd en `deploy/`.

**Apps:** `core` (SiteSettings, AboutSection) · `blog` (Category, Tag, Post) · `media_content` (VideoPost) · `contact` · `newsletter`. La base de datos está vacía. No hay contenido que migrar.

### Se conserva

| Pieza | Nota |
|---|---|
| CSS, JS, imágenes, componentes visuales, carrusel 3D | Sin cambios de estilo. Las plantillas nuevas reutilizan las clases y componentes existentes (`firm-pill`, tarjetas, `content_card.html`, `article_card.html`, `video_card.html`, `pagination.html`, `icons.html`). |
| Django + Unfold + CKEditor 5 | Cumple el capítulo 8. |
| `PublishStatus` / `PublishedQuerySet` | Se reutiliza en publicaciones, videos, figuras y guías. |
| `VideoPost` (ID de YouTube, `youtube-nocookie`) | Se amplía. |
| `Subscriber` + baja por token | Se amplía. |
| `NoIndexMiddleware`, robots y sitemap dinámicos | Se amplían. |
| `deploy/` | Se ajusta dominio canónico y se retira `noindex` al lanzar. |

### Debe cambiar (reglas no visuales de la especificación)

| Actual | Regla | Acción |
|---|---|---|
| App `contact`, correo y teléfono visibles, botón «Agendar reunión» | §2.1 Contacto único por WhatsApp, sin formularios ni correo | Eliminar `contact`; los CTA existentes pasan a abrir `https://wa.me/56930882307`. Se mantiene el estilo del botón. |
| Etiqueta «Abogada corporativa» bajo el nombre | §2.1 No usar «abogada» fuera de la formulación exacta | Reemplazar por `SOCIETARIO · REORGANIZACIONES · TRIBUTARIO` (editable en configuración). |
| Menú Inicio · Servicios · Sobre mí · Actualidad · Contacto | §5.1 | Inicio · Sobre mí · Áreas de práctica (desplegable con 2 áreas y 9 subpáginas) · Publicaciones · Videos · Recursos · Conversemos. |
| URL con barra final y prefijo `/blog/` | §3 URL definitivas | Nuevo mapa de URL sin barra final y 301 desde las antiguas. |
| `lang="es"` | §10.1 | `es-CL`. |
| Textos con dos puntos, «Angela» sin tilde, datos ficticios de `setup_initial_data` | §2.1 | Reescribir textos de plantillas y admin; validadores; importador del prototipo. |
| Barra global de newsletter en todas las páginas | §8.2 El boletín va en el índice de publicaciones, inactivo hasta decisión | Mover al índice de publicaciones y condicionar a `newsletter_mode`. |
| nginx `www → apex` vs paquete técnico en `www` | §3 | Decidir y alinear (ver §6). |

### No existe y hay que construir

Áreas de práctica y 9 figuras editables · mapa de reorganizaciones · comparador de tipos sociales · publicaciones con los campos del §8.1 · videos con transcripción y VideoObject · glosario buscable y guías · páginas legales · JSON-LD automático · `llms.txt` · metadatos por página desde el CSV.

---

## 2. Arquitectura de datos objetivo

### 2.1 Apps

```
apps/
  core/          Configuración, Sobre mí, páginas legales, inicio, SEO (JSON-LD y metadatos), robots, llms.txt
  practice/      NUEVA · Áreas, figuras, FAQ, mapa de reorganizaciones, comparador
  publications/  Reemplaza blog · Publicaciones, formatos, fuentes, etiquetas de figura
  videos/        Reemplaza media_content · Videos con transcripción
  resources/     NUEVA · Glosario y guías
  newsletter/    Boletín con consentimiento y doble verificación, inactivo por defecto
```

Se elimina `apps/contact`.

### 2.2 Modelos

**core**

- `SiteSettings` (singleton).
  - Agregar `whatsapp_number` (por defecto `56930882307`), `header_line`, `canonical_base_url`, `youtube_url`, `youtube_channel_name`, `tiktok_url`, `search_console_token`, `bing_token`, `newsletter_mode` (`inactivo` · `propio` · `linkedin`), `newsletter_linkedin_url`.
  - Mantener `instagram_url`, `linkedin_url`. Redes vacías no se muestran.
  - Retirar `email`, `address`, `phone`, `hero_*`, `facebook_url`, `footer_text`. Los textos del hero pasan a leerse del primer banner.
- `AboutPage` (singleton, reemplaza `AboutSection`). Campos por sección del prototipo (`SOBRE MÍ`, `CÓMO TRABAJO`, `FORMACIÓN`, `EN BREVE`), fotografía, descripción en tercera persona para `Person`, `knowsAbout`, formación para `alumniOf` y `hasCredential`.
- `LegalPage`. `slug`, `title`, `body`, `is_published`, `updated_at`.

**practice**

- `PracticeArea`. `slug`, `name`, `label`, `title_html`, `lead`, `intro`, inline `TaxPoint`, `ley`, `criterio`, `riesgo`, `how_i_work`, inline `FAQ`, `sources`, `verified_at`, `closing_question`, `whatsapp_message`, `meta_title`, `meta_description`, `order`.
- `PracticeFigure`. Tipo de contenido editable con la plantilla del §7.2 en orden.
  - `area` (FK), `slug`, `short_name`, `label`, `title_html`, `lead`, `updated_at`.
  - `definition_lead`, `definition_body`.
  - `sa`, `spa`, `ltda`, `societario_note`.
  - inline `TaxPoint` (`order`, `title`, `text`), numerados en romanos.
  - `ley`, `criterio`, `riesgo`.
  - inline `FAQ` (`question`, `answer`, `order`) → `FAQPage`.
  - `sources`, `verified_at`, `closing_question`, `whatsapp_message`, `meta_title`, `meta_description`.
- `ReorgMapOption`. `order`, `question`, `figure` (FK), `description`, `attention_point`.
- `ComparatorRow`. `order`, `criterion`, `sa`, `spa`, `ltda`.

**publications**

- `Publication` (reemplaza `Post`). `title`, `slug` editable, `format` (`nota` · `analisis` · `guia` · `consulta` · `cierre`), `areas` (M2M), `figures` (M2M), `lead` (bajada y meta descripción), `summary` (En breve), `body` (CKEditor), `tax_block`, `ley`, `criterio`, `riesgo`, inline `Source` (`text`, `url`), `published_at`, `updated_at` (auto), `verified_at`, `image` (mínimo 1200 × 630), `status`. Propiedades `reading_time` y autora fija.
- Se eliminan `Category` y `Tag`.

**videos**

- `Video` (reemplaza `VideoPost`). Mantener `youtube_url`, `youtube_id`, `thumbnail`. Agregar `area` (FK), `figures` (M2M), `summary`, `transcript` (obligatorio), `duration` (segundos; se expone en ISO 8601 y `m:ss`), `related_publications` (M2M), `published_at`, `updated_at`.

**resources**

- `GlossaryTerm`. `term`, `definition`, `search_key` (normalizado al guardar), `order`.
- `Guide`. `title`, `description`, `file`, `status` (`proximamente` · `publicada` · `oculta`), `figures` (M2M).

**newsletter**

- `Subscriber`. Agregar `consent_at`, `consent_text`, `consent_ip`, `confirmed_at`, `confirm_token`. `is_active` solo tras confirmar.

### 2.3 Mapa de URL (sin barra final)

| URL | Vista |
|---|---|
| `/` | `HomeView` |
| `/sobre-mi` | `AboutView` |
| `/reorganizaciones-empresariales` · `/derecho-societario` | `PracticeAreaView` |
| 9 slugs de figura (`/fusion-de-sociedades` …) | `PracticeFigureView` |
| `/publicaciones` · `/publicaciones/<slug>` | lista y detalle |
| `/videos` · `/videos/<slug>` | lista y detalle |
| `/recursos` | `ResourcesView` |
| `/politica-de-privacidad` · `/terminos-de-uso` | `LegalPageView` |
| `/robots.txt` · `/sitemap.xml` · `/llms.txt` | rastreo |

`APPEND_SLASH = False`, middleware que responde 301 de `/x/` a `/x` (excepto `/admin/`, `/ckeditor5/`, `/static/`, `/media/`). Redirecciones 301 de `/blog/…`, `/sobre-mi/`, `/contacto/`. Resolución de primer nivel: rutas fijas → área → figura → 404.

### 2.4 Plantillas

Se crean plantillas nuevas para las secciones que no existen y se adaptan las actuales, siempre con las clases y componentes del CSS vigente. No se agrega CSS salvo el mínimo para elementos que hoy no tienen equivalente (tabla del comparador con desplazamiento interno, chips de filtro, panel del mapa, `details` de FAQ y transcripción). Ese CSS se agrega a `studio.css` siguiendo sus variables.

- `base.html`. `lang="es-CL"`, bloques para metadatos, canónica, Open Graph y JSON-LD. Se retira la barra global de newsletter.
- `navbar.html` y `footer.html`. Mismo estilo; nuevo contenido según §5. El desplegable Áreas de práctica se construye con el patrón de menú ya existente.
- `core/home.html`. El carrusel 3D actual se alimenta desde datos. Banner 1 fijo con H1, banner 2 con la última Nota jurídica, banner 3 solo si hay video publicado y canal configurado. Secciones Áreas (`#areas`), Publicaciones recientes, Sobre mí, Recursos.
- `practice/area.html`, `practice/figure.html`, `publications/list.html`, `publications/detail.html`, `videos/list.html`, `videos/detail.html`, `resources/index.html`, `core/legal.html`.
- Componentes nuevos de contenido (no de estilo). `bloque_tributario.html`, `bloque_ley_criterio_riesgo.html`, `fuentes.html`, `faq.html`, `relacionados.html`, `cierre_conversemos.html`, `aclaracion.html`, `btn_whatsapp.html`.
- JavaScript. Se agrega a `studio.js` lo que falta y no existe hoy. Filtros por chip, mapa de reorganizaciones (opciones desde JSON renderizado), buscador del glosario con normalización NFD, vista previa liviana de YouTube. El carrusel actual se completa con lo que exige el §6.1 si falta algo (siete segundos, pausa por hover, toque y foco, botón pausar, `prefers-reduced-motion`, banners ocultos sin foco).

### 2.5 SEO y datos estructurados

- `apps/core/seo.py` con generadores de `@graph`. `person`, `website`, `breadcrumb`, `webpage`, `faq`, `article`, `video`.
- Metadatos desde `tecnico/metadatos-por-pagina.csv` cargados al importar. Publicaciones generan `title` y descripción desde `title` y `lead`.
- Sitemap con estáticas, áreas, figuras, publicaciones y videos con `lastmod`. `robots.txt` existente. `llms.txt` servido con la URL base configurada.
- Tokens de verificación de Search Console y Bing desde `SiteSettings`.

### 2.6 Rendimiento (sin tocar el diseño)

- Variantes WebP/AVIF generadas con Pillow al guardar y `<picture>` con `srcset` en las imágenes de contenido. Las imágenes ya presentes en `static/images/` se convierten una vez.
- `preload` del primer banner, `loading="lazy"` bajo la primera pantalla, dimensiones explícitas.
- Vista previa de YouTube con miniatura; el `iframe` se inserta al hacer clic.

### 2.7 Validaciones de marca

- `apps/core/validators.py`. `sin_dos_puntos`, `angela_con_tilde`, `sin_corchetes`, `sin_inicia_legal`. Aplicados a títulos, bajadas, etiquetas, FAQ, glosario y configuración.
- Comando `revisar_sitio`. Renderiza todas las URL públicas y reporta dos puntos en texto visible, «Angela» sin tilde, corchetes, menciones a Inicia Legal, más de un H1, enlaces de WhatsApp distintos, imágenes sin `alt`, redes vacías. Automatiza el checklist §13 salvo el punto visual.

---

## 3. Fases

### Fase 0 · Preparación

1. Resolver las decisiones del §6.
2. Commitear los cambios pendientes de `studio.css` y `studio.js` (son parte de la estética que se conserva). Decidir qué hacer con `imgs/` sin seguimiento (mover a `static/images/` o descartar).
3. Copiar `sitio/img/*` a `static/images/` y guardar `tecnico/` en `docs/tecnico/`.
4. Rama `estructura-contenidos`.

### Fase 1 · Configuración, URL y elementos globales

1. Refactor de `SiteSettings`, nuevo `LegalPage`, eliminación de `contact`.
2. Enrutamiento sin barra final, middleware de redirección, 301 de rutas antiguas.
3. `navbar.html` y `footer.html` con el contenido del §5 y el estilo actual. CTA a WhatsApp.
4. `lang="es-CL"`, retiro de la barra global de newsletter.
5. Validadores y primera versión de `revisar_sitio`.
6. Admin Unfold reorganizado. Publicaciones · Videos · Áreas de práctica · Figuras · Glosario · Guías · Páginas legales · Boletín · Configuración · Sobre mí.

### Fase 2 · Áreas de práctica

1. App `practice`, modelos y migraciones.
2. Comando `importar_prototipo`. Parsea los 11 HTML del prototipo y los JSON de `tecnico/datos-estructurados` para poblar áreas, figuras, puntos tributarios, FAQ, fuentes, mapa, comparador y metadatos. Los textos jurídicos quedan idénticos sin transcripción manual.
3. Plantillas de área y figura con los bloques del §7.2 en orden, usando las tarjetas y componentes existentes.
4. Mapa de reorganizaciones y comparador (tabla HTML real con `scope`, desplazamiento dentro de su recuadro).
5. Relacionados por figura; ocultos si no hay contenido.
6. JSON-LD `BreadcrumbList` + `WebPage` + `FAQPage`.

### Fase 3 · Inicio y Sobre mí

1. Carrusel actual alimentado desde datos, con las condiciones del §6.1 que falten. Banner 3 condicionado.
2. Secciones del inicio en el orden del §6.2.
3. `AboutPage` y plantilla con las secciones del prototipo; importar textos de `sobre-mi.html` y `sobre-mi.json`.
4. JSON-LD `Person` + `WebSite`.

### Fase 4 · Publicaciones

1. App `publications`, `Publication` y `Source`. Se recrea la tabla (está vacía).
2. Admin ordenado como el §8.1, validadores, imagen con validación de tamaño, tiempo de lectura.
3. Índice con destacada, chips por formato con descripciones del prototipo, grilla, filtro sin recarga, boletín condicionado a `newsletter_mode`.
4. Detalle según `plantilla-articulo.html` (encabezado con firma y fechas, En breve, cuerpo, Y en lo tributario…, La ley mi criterio y el riesgo, Fuentes y verificación, Sobre la autora, Sigue leyendo, cierre).
5. JSON-LD `Article` con `citation`.
6. Conexiones automáticas con banner 2, recientes y relacionados.

### Fase 5 · Videos y Recursos

1. App `videos`, `Video`, vista previa liviana, transcripción desplegable, resumen, Para profundizar.
2. Lista con último video, filtro por área, botón de YouTube condicionado.
3. JSON-LD `VideoObject`.
4. App `resources`, importar los 13 términos del glosario desde `recursos.html`, buscador, guías con estado.

### Fase 6 · SEO técnico y rendimiento

1. Metadatos de las 19 páginas desde el CSV, canónicas, Open Graph.
2. Sitemap completo, `llms.txt`, `robots.txt`.
3. Pipeline de imágenes, `preload`, `lazy`, dimensiones.
4. Lighthouse móvil por plantilla. LCP < 2,5 s, INP < 200 ms, CLS < 0,1.
5. Validación de JSON-LD con la prueba de resultados enriquecidos y schema.org.

### Fase 7 · Privacidad, boletín, QA y publicación

1. Boletín con doble verificación y registro de consentimiento. Activo solo con `newsletter_mode = propio` y política publicada. Con `linkedin`, el formulario se reemplaza por enlace.
2. Sin analítica ni terceros por defecto.
3. `revisar_sitio`, checklist §13 (menos el visual) y pruebas Django de URL, redirecciones, H1 único, JSON-LD, sitemap, validadores y visibilidad condicional.
4. nginx al dominio canónico, retiro de `X-Robots-Tag`, `SITE_INDEXABLE=True`, alta en Search Console y Bing con acceso para Ángela.

Fases 4 y 5 pueden ir en paralelo tras la Fase 2.

---

## 4. Reglas permanentes

- Textos jurídicos desde el importador, nunca reescritos. Si algo no cabe, se ajusta la maqueta, no el texto.
- Sin dos puntos en texto visible. Validadores en admin y `revisar_sitio`.
- Ángela siempre con tilde.
- Un solo contacto, `https://wa.me/56930882307`. Parámetro `text` solo con mensajes aprobados.
- Sin mención a Inicia Legal hasta 2027.
- Espacios sin contenido se ocultan. Nunca corchetes visibles.
- Primera persona y tuteo; tercera persona solo en JSON-LD.
- Toda página jurídica cierra con firma, fechas, fuentes y aclaración fija.

---

## 5. Dependencias

- Mantener todas las actuales. Agregar `pillow-avif-plugin` si Pillow no exporta AVIF nativo.
- `tailwindcss` y `package.json` solo se conservan si `main.css` se sigue regenerando desde `input.css`; si no, se retiran.

---

## 6. Decisiones pendientes

| Decisión | Responsable | Propuesta |
|---|---|---|
| Aprobación de mantener la estética actual en lugar de la identidad 3.1 (§4, §5.1, §13). | Ángela | Registrar la aprobación por escrito antes de la Fase 1. |
| Dominio canónico. Paquete en `www`, nginx actual en apex. | Desarrollo | `https://www.angelamontiel.cl` según el paquete; cambiar nginx. Si se elige apex, regenerar `tecnico/`. |
| Página individual por video `/videos/<slug>`. | Ángela | Incluirla; facilita VideoObject, sitemap y compartir. |
| Mantener botones flotantes (WhatsApp, volver arriba) y barra de progreso. | Ángela | Mantener, son parte de la estética que se conserva. El flotante de WhatsApp cumple la regla de contacto único. |
| Línea bajo el nombre, mensajes de WhatsApp, redes, canal de YouTube, boletín, textos legales, fotografías, primeras publicaciones. | Ángela | Provisorias del prototipo y campos previstos en `SiteSettings`, según §12. |

---

## 7. Resultado esperado

- 19 URL del §3 sin barra final, con 301 desde las antiguas.
- 11 páginas jurídicas editables con textos idénticos al prototipo.
- Publicaciones, videos, glosario y guías gestionables sin programar.
- Inicio alimentado automáticamente, con banner 3 condicionado.
- JSON-LD completo y validado, sitemap, robots, `llms.txt`.
- Core Web Vitals en verde en celular.
- Checklist §13 automatizado con `revisar_sitio`, salvo el punto visual, cubierto por la aprobación de Ángela.
