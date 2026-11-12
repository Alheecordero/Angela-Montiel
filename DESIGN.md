# Sistema de diseño · angelamontiel.cl

Una sola fuente de verdad para el estilo del sitio. Documenta la identidad que ya
existe (azul marino, dorado, Playfair Display, Outfit, logo AM, fotos en blanco y
negro) y fija cada decisión una vez, con su uso. Las páginas usan estos nombres,
nunca valores sueltos.

Estado: **aplicado** (noviembre 2026).

Antes había 92 colores fijos, 191 transparencias, 99 tamaños de letra, 23 radios,
38 sombras y 12 cortes de pantalla repartidos en 7.591 líneas de CSS. Ahora:

- `static/css/tokens.css` define todos los valores de este documento. Se carga
  primero. Los nombres antiguos (`--color-blue`, `--gold-deep`, etc.) apuntan a
  estos tokens mientras el CSS heredado los siga usando.
- `static/css/componentes.css` fija una sola versión de cada componente. Se carga
  al final.
- `main.css`, `studio.css`, `content.css` y `retoques.css` son el CSS heredado,
  sin reglas muertas (quedan unas 4.200 líneas en total) y con sus valores
  pasados a tokens.

Regla para cambios nuevos: usar tokens, nunca valores sueltos. Si hace falta un
valor que no existe, se agrega aquí y en `tokens.css`.

---

## 1. Color

Sin modo oscuro: el sitio es claro, con bloques azules para dar peso.

### Marca

| Token | Valor | Uso |
|---|---|---|
| `--ink` | `#172a42` | Azul principal. Menú, pie, bloques oscuros, botón secundario, texto de botones sobre dorado claro. |
| `--ink-deep` | `#101d31` | Final de los degradados azules (menú, pie, cierre). |
| `--ink-soft` | `#27405f` | Hover del botón azul. |
| `--gold` | `#c6a15a` | Acento. Botón principal, líneas finas, íconos, números, texto dorado **sobre azul**. |
| `--gold-hover` | `#d4b36a` | Hover del botón principal. |
| `--gold-text` | `#86672c` | Dorado para **texto sobre fondo claro** (enlaces, etiquetas). 5,3:1 sobre blanco. |
| `--gold-soft` | `#dcc28e` | Texto dorado sobre azul translúcido (tarjeta del mapa). |

Los degradados azules van siempre de `--ink` a `--ink-deep`, en 160°. Nada de
degradados con otros colores.

### Neutros

| Token | Valor | Uso |
|---|---|---|
| `--paper` | `#ffffff` | Fondo de página y de tarjetas. |
| `--cream` | `#f7f2e9` | Superficie cálida. Solo banner de inicio y estados activos suaves. |
| `--line` | `rgba(23, 42, 66, 0.12)` | Bordes y divisores. |
| `--text-strong` | `#16181d` | Títulos. |
| `--text` | `#3f3b36` | Texto corrido. 11,1:1. |
| `--text-muted` | `#6f685e` | Fechas, datos, pies de foto. 5,5:1. |
| `--on-ink` | `#f6f1e8` | Texto sobre azul. |
| `--on-ink-muted` | `rgba(246, 241, 232, 0.78)` | Texto secundario sobre azul. |

Reemplazan a los grises actuales `#4e4a45`, `#4b463f`, `#5e584f`, `#6b655d`,
`#7a7369`, `#8a8176` y a los azules `#1f2e3a`, `#16283f`, `#1d3353`, `#13223a`,
`#0c1a2e`.

### Estados

| Token | Valor | Uso |
|---|---|---|
| `--success` | `#2f6b4f` | Confirmaciones (boletín). |
| `--error` | `#a3392f` | Errores de formulario. |

Excepción de marca externa: el botón flotante de WhatsApp conserva su verde.

---

## 2. Tipografía

Dos familias, las de siempre:

- **Playfair Display** 500 y 500 cursiva: títulos y énfasis en títulos.
- **Outfit** 400, 500 y 600: todo lo demás.

| Token | Tamaño | Interlineado | Familia | Uso |
|---|---|---|---|---|
| `--fs-display` | `clamp(2.6rem, 4.6vw, 4.6rem)` | 1.03 | Playfair | Solo el titular del banner de inicio. |
| `--fs-h1` | `clamp(2.2rem, 4vw, 3.4rem)` | 1.08 | Playfair | Título de cada página. |
| `--fs-h2` | `clamp(1.8rem, 3vw, 2.5rem)` | 1.12 | Playfair | Títulos de sección. |
| `--fs-h3` | `1.35rem` | 1.25 | Playfair | Títulos de tarjeta y subtítulos. |
| `--fs-lead` | `1.125rem` | 1.65 | Outfit | Bajadas bajo un título. |
| `--fs-body` | `1rem` | 1.7 | Outfit | Texto corrido, tarjetas, preguntas. |
| `--fs-small` | `0.875rem` | 1.5 | Outfit | Botones, fechas, datos, filtros. |
| `--fs-label` | `0.72rem` | 1.5 | Outfit 600 | Etiquetas en mayúsculas, espaciado 0.18em. |

Reglas:

- Texto corrido nunca bajo 16 px.
- Líneas de lectura de 65 a 75 letras: ancho máximo `--measure: 38rem`.
- El énfasis en títulos es cursiva dorada (`<em>`), una vez por título.
- Las mayúsculas solo en etiquetas (`--fs-label`), nunca en títulos ni botones.

---

## 3. Espacio

Escala de 4 px. Todo margen, relleno y separación sale de aquí.

| Token | Valor |
|---|---|
| `--space-1` | 4px |
| `--space-2` | 8px |
| `--space-3` | 12px |
| `--space-4` | 16px |
| `--space-5` | 24px |
| `--space-6` | 32px |
| `--space-7` | 48px |
| `--space-8` | 64px |
| `--space-9` | 96px |

| Token | Valor | Uso |
|---|---|---|
| `--section-y` | `clamp(3.5rem, 7vw, 6rem)` | Relleno vertical de cada sección (56 a 96 px). |
| `--section-y-tight` | `clamp(2.5rem, 5vw, 3.5rem)` | Secciones cortas (fuentes, filtros). |
| `--container` | `1180px` | Ancho máximo del contenido. |
| `--gutter` | `24px` escritorio y tablet, `16px` celular | Margen lateral. |
| `--measure` | `38rem` | Ancho máximo de párrafos largos. |

---

## 4. Forma y profundidad

| Token | Valor | Uso |
|---|---|---|
| `--radius-sm` | `4px` | Contorno de foco, etiquetas sobre fotos. |
| `--radius-md` | `14px` | Tarjetas, fotos, bloques azules. |
| `--radius-pill` | `999px` | Botones y filtros. |
| `--shadow-sm` | `0 8px 24px rgba(16, 29, 49, 0.08)` | Hover de tarjetas, botones flotantes. |
| `--shadow-lg` | `0 24px 56px rgba(16, 29, 49, 0.16)` | Lo elevado: tarjeta central del carrusel, tarjeta del mapa, destacada. |

Bordes de 1 px con `--line`. El dorado en bordes solo para marcar lo activo o
destacado.

---

## 5. Pantallas

Tres tamaños, de celular hacia arriba:

| Nombre | Rango | Qué cambia |
|---|---|---|
| Celular | hasta 600px | Una columna, margen 16 px, menú desplegable, carrusel sin flechas. |
| Tablet | 601 a 980px | Dos columnas donde cabe, menú desplegable, foto del banner arriba. |
| Escritorio | desde 981px | Menú completo, columnas finales, foto del banner a la derecha. |

Reemplazan a los cortes anteriores de 380, 480, 520, 640, 768, 900, 1024 y
1050 px.

Excepciones anotadas, porque el componente lo necesita:

- **Menú**: el menú completo no cabe bajo unos 1.080 px, así que se pliega hasta
  1100 px (`max-width: 1100px`). Entre 1101 y 1280 px se compacta (sin la línea
  de especialidades bajo el nombre y con menos espacio entre enlaces).
- **Banner en escritorio angosto** (981 a 1100 px): el titular baja un punto.

---

## 6. Componentes

### Botones

| Tipo | Clase | Aspecto | Uso |
|---|---|---|---|
| Principal | `.firm-pill` | Fondo `--gold`, texto `--ink` (6:1), píldora, alto mínimo 48 px, `--fs-small` 500. Hover `--gold-hover`. | La acción de contacto (WhatsApp). Uno por pantalla. |
| Secundario | `.btn-ink` | Fondo `--ink`, texto `--on-ink`, píldora, 48 px. Hover `--ink-soft`. Sobre azul: versión borde (`--on-ink` al 35 %). | Ir a otra sección: ver publicaciones, ver videos. |
| Enlace | `.firm-text-link` | Texto con subrayado de 1 px. `--gold-text` sobre claro, `--gold` sobre azul. | Leer, ver en detalle, ver el área. |

Estados comunes: hover con transición de 0,25 s; foco con contorno de 2 px
(`--ink` sobre claro, `--gold` sobre azul) separado 3 px; desactivado al 50 %
de opacidad y sin puntero.

Se eliminaron `.btn`, `.btn-primary`, `.btn-outline`, `.btn-blue`, `.type-tab`,
`.hb-btn` (ahora `.btn-ink`) y `.hb-link` (ahora `.firm-text-link`).
El botón del menú (`.firm-pill.nav-cta`) es la versión compacta, de 40 px.

### Filtro

`.filter-chip`: píldora con borde `--line`, `--fs-small`, sin mayúsculas (hoy
van en mayúsculas). Activo: fondo `--ink` y texto `--on-ink`. Área táctil mínima
de 40 px de alto.

### Etiqueta

`.firm-kicker`: `--fs-label` en mayúsculas, línea dorada de 28 px antes.
Color `--gold-text` sobre claro y `--on-ink-muted` sobre azul. Una sola versión.
Si nombra una sección sin otro título, es `<h2>`.

### Números de lista

Los numerales (i., ii., iii.) van en `--gold-text` sobre claro y en `--gold`
sobre azul.

### Tarjeta

Clases que la usan: `.c-tile`, `.c-col`, `.firm-post`, `.c-lcr-card`
(`.c-video-card` es una foto con texto debajo, sin caja):
fondo `--paper`, borde `--line`, radio `--radius-md`, relleno `--space-5`
(`--space-4` en celular). Hover: borde dorado al 35 % y `--shadow-sm`.
Versión azul: degradado de marca, texto `--on-ink`.
Orden interno: foto, etiqueta, título `--fs-h3`, texto `--fs-body`, enlace al pie.

### Sección

`.c-section`: relleno `--section-y`, fondo `--paper`. Dos secciones blancas
seguidas se separan con una línea `--line`. Variante azul `.c-section--ink`
para dar peso (cierre, bloque tributario). La crema solo en el banner.
Cabecera: etiqueta, título `--fs-h2` (máximo 24 letras de ancho), bajada
opcional `--fs-lead` (máximo 40rem).

### Otros

- **Menú**: azul de marca, enlaces `--fs-label`, actual con subrayado dorado.
  En celular, el menú desplegable con filas en Playfair.
- **Pie**: azul de marca con la foto de Ángela que aparece al final.
- **Foco**: siempre visible con teclado, como en los botones.

---

## 7. Imágenes e íconos

- **Fotos siempre en blanco y negro** (`grayscale(1) contrast(1.06)`), incluidas
  las que se suban desde el panel. Ángela en blanco y negro; áreas y figuras con
  fotos sobrias de Santiago, oficinas, documentos o metáforas simples.
- Sin estatuas, columnas ni clichés legales (martillo, balanza).
- Formatos AVIF y WebP en 800 px y 1920 px; siempre con ancho y alto declarados.
- **Íconos**: el set propio de `components/icons.html`, trazo de 1,5 px,
  tamaños 16 y 18 px, color heredado del texto.

## 8. Movimiento

- Aparición al hacer scroll: 0,55 s, desplazamiento de 14 px.
- Banner: cambio cada 7 s, pausa al pasar el mouse.
- Con "reducir movimiento" activado, todo aparece sin animación.
