# Web profesional — Angela Montiel

Sitio web profesional para la abogada Angela Montiel (Chile). Incluye landing page, blog de artículos legales, sección de videos de YouTube, formulario de contacto y newsletter.

## Stack

- **Backend:** Django 5.x
- **Admin:** django-unfold (panel visual moderno)
- **Editor:** django-ckeditor-5 (artículos del blog)
- **Frontend:** Plantillas Django + CSS personalizado (diseño sobrio y profesional)
- **Base de datos:** SQLite (desarrollo) / PostgreSQL (producción)

## Requisitos

- Python 3.10+
- pip

## Instalación local

```bash
# Clonar o entrar al proyecto
cd AngelaMontiel

# Instalar dependencias
pip install -r requirements.txt

# Configurar entorno
cp .env.example .env
# Editar .env con SECRET_KEY y ALLOWED_HOSTS

# Migraciones y datos iniciales
python manage.py migrate
python manage.py setup_initial_data

# Crear usuario administrador
python manage.py createsuperuser

# Iniciar servidor
python manage.py runserver
```

- **Sitio público:** http://127.0.0.1:8000/
- **Panel admin:** http://127.0.0.1:8000/admin/

## Guía para Angela — Gestión de contenido

### Acceder al panel

1. Ir a `/admin/`
2. Iniciar sesión con su usuario y contraseña

### Configurar el sitio

- **Configuración del sitio:** teléfono, email, dirección, redes sociales, textos de la página de inicio.
- **Sobre mí:** biografía, foto profesional, credenciales y especialidades.

### Publicar un artículo

1. Ir a **Contenido → Artículos → Añadir artículo**
2. Completar título, extracto y contenido
3. Opcional: imagen de portada, categoría y etiquetas
4. En **Publicación**, cambiar estado a **Publicado**
5. Guardar

### Publicar un video de YouTube

1. Ir a **Contenido → Videos → Añadir video**
2. Pegar la URL de YouTube (ej: `https://www.youtube.com/watch?v=XXXXXXXXXXX`)
3. Agregar título y descripción
4. Cambiar estado a **Publicado** y guardar

> No es necesario pegar código iframe. El sistema genera el reproductor automáticamente.

### Revisar mensajes de contacto

- **Comunicación → Mensajes:** consultas enviadas desde el formulario de contacto
- Los mensajes nuevos aparecen marcados como **Nuevo**
- Seleccionar mensajes y usar la acción **Marcar como leídos**

### Newsletter

- **Comunicación → Newsletter:** lista de suscriptores activos
- Cada suscriptor tiene un enlace de baja automático (`/newsletter/baja/<token>/`)

## Estructura del proyecto

```
apps/
  core/           Landing, sobre mí, configuración
  blog/           Artículos legales
  media_content/  Videos de YouTube
  contact/        Formulario de contacto
  newsletter/     Suscriptores
config/           Settings, URLs, admin dashboard
templates/        Plantillas HTML
static/           CSS y JavaScript
```

## Despliegue en producción

1. Configurar variables de entorno:

```env
DEBUG=False
SECRET_KEY=generar-clave-segura-larga
ALLOWED_HOSTS=tudominio.cl,www.tudominio.cl
DATABASE_URL=postgres://usuario:password@host:5432/nombre_db
SECURE_SSL_REDIRECT=True
```

2. Ejecutar:

```bash
export DJANGO_SETTINGS_MODULE=config.settings.prod
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py setup_initial_data
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

3. Servir archivos media con nginx o almacenamiento en la nube (S3, etc.)

## Rutas principales

| Ruta | Descripción |
|------|-------------|
| `/` | Página de inicio |
| `/sobre-mi/` | Biografía profesional |
| `/blog/` | Listado de artículos |
| `/blog/videos/` | Listado de videos |
| `/contacto/` | Formulario de contacto |
| `/admin/` | Panel de administración |
| `/sitemap.xml` | Mapa del sitio (SEO) |

## Credenciales de desarrollo

Tras la instalación inicial se crea un superusuario de prueba:

- **Usuario:** `angela`
- **Contraseña:** `admin123`

> Cambiar esta contraseña antes de desplegar en producción.
