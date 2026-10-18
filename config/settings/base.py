from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
    SITE_INDEXABLE=(bool, False),
)

environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY", default="django-insecure-dev-key-change-in-production")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])
SITE_INDEXABLE = env.bool("SITE_INDEXABLE", default=False)

INSTALLED_APPS = [
    "config.apps.ConfigConfig",
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "django.contrib.humanize",
    "django_ckeditor_5",
    "apps.core",
    "apps.practice",
    "apps.publications",
    "apps.videos",
    "apps.resources",
    "apps.newsletter",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "apps.core.middleware.NoIndexMiddleware",
    "apps.core.middleware.TrailingSlashRedirectMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
APPEND_SLASH = False

# Correo del boletín (doble verificación). En producción se configura el proveedor en .env.
EMAIL_BACKEND = env("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = env("EMAIL_HOST", default="")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="Ángela Montiel <boletin@angelamontiel.cl>")

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.core.context_processors.site_context",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "es-cl"
TIME_ZONE = "America/Santiago"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CKEDITOR_5_CONFIGS = {
    "default": {
        "language": "es",
        "toolbar": [
            "heading",
            "|",
            "bold",
            "italic",
            "superscript",
            "link",
            "bulletedList",
            "numberedList",
            "blockQuote",
            "|",
            "undo",
            "redo",
        ],
        "heading": {
            "options": [
                {"model": "paragraph", "title": "Párrafo", "class": "ck-heading_paragraph"},
                {"model": "heading2", "view": "h2", "title": "Título H2", "class": "ck-heading_heading2"},
                {"model": "heading3", "view": "h3", "title": "Título H3", "class": "ck-heading_heading3"},
            ]
        },
    },
}

CKEDITOR_5_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"

UNFOLD = {
    "DASHBOARD_CALLBACK": "config.admin.dashboard_callback",
    "SITE_TITLE": "Ángela Montiel",
    "SITE_HEADER": "Panel de administración",
    "SITE_SUBHEADER": "Gestión de contenido",
    "SITE_SYMBOL": "gavel",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": "Panel",
                "items": [
                    {"title": "Inicio", "icon": "dashboard", "link": "/admin/"},
                ],
            },
            {
                "title": "Contenido",
                "items": [
                    {"title": "Publicaciones", "icon": "article", "link": "/admin/publications/publication/"},
                    {"title": "Videos", "icon": "play_circle", "link": "/admin/videos/video/"},
                    {"title": "Glosario", "icon": "menu_book", "link": "/admin/resources/glossaryterm/"},
                    {"title": "Guías descargables", "icon": "download", "link": "/admin/resources/guide/"},
                ],
            },
            {
                "title": "Áreas de práctica",
                "items": [
                    {"title": "Áreas", "icon": "account_tree", "link": "/admin/practice/practicearea/"},
                    {"title": "Figuras (subpáginas)", "icon": "description", "link": "/admin/practice/practicefigure/"},
                ],
            },
            {
                "title": "Sitio",
                "items": [
                    {"title": "Configuración", "icon": "settings", "link": "/admin/core/sitesettings/1/change/"},
                    {"title": "Sobre mí", "icon": "person", "link": "/admin/core/aboutpage/1/change/"},
                    {"title": "Páginas legales", "icon": "gavel", "link": "/admin/core/legalpage/"},
                ],
            },
            {
                "title": "Boletín",
                "items": [
                    {"title": "Suscriptores", "icon": "campaign", "link": "/admin/newsletter/subscriber/"},
                ],
            },
        ],
    },
}
