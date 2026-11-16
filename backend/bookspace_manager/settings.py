"""
Django settings for bookspace_manager project.

Proyecto: Raccoon Cafe - Sistema de gestion de salas, cafeteria y libreria
Materia : SOFG1006 - Desarrollo de Aplicaciones Web y Moviles
Taller  : Taller 3 - Django

CONFIGURACION DE PRODUCCION (servidor alwaysdata, base MySQL).
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================================
# VARIABLES DE ENTORNO
# ------------------------------------------------------------
# Ningun secreto vive en el codigo. Los valores se leen del entorno
# o, en desarrollo local, del archivo backend/.env (ver .env.example).
# ============================================================
def _cargar_env(ruta):
    """Carga un archivo .env sencillo (CLAVE=valor) sin dependencias extra.

    Las variables que ya existan en el entorno tienen prioridad, de modo
    que en el hosting basta con definirlas desde su panel.
    """
    if not ruta.exists():
        return
    for linea in ruta.read_text(encoding='utf-8').splitlines():
        linea = linea.strip()
        if not linea or linea.startswith('#') or '=' not in linea:
            continue
        clave, valor = linea.split('=', 1)
        os.environ.setdefault(clave.strip(), valor.strip().strip('"').strip("'"))


def _lista(nombre, por_defecto=''):
    """Convierte una variable 'a,b,c' en lista, ignorando vacios."""
    return [v.strip() for v in os.environ.get(nombre, por_defecto).split(',') if v.strip()]


_cargar_env(BASE_DIR / '.env')


# Clave de firma de sesiones y tokens. En produccion DEBE definirse.
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'clave-solo-para-desarrollo-local')

# Seguro por defecto: DEBUG apagado salvo que se active explicitamente.
DEBUG = os.environ.get('DJANGO_DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = _lista(
    'DJANGO_ALLOWED_HOSTS',
    'dannurda.alwaysdata.net,www.dannurda.alwaysdata.net,localhost,127.0.0.1',
)

CSRF_TRUSTED_ORIGINS = _lista(
    'DJANGO_CSRF_TRUSTED_ORIGINS',
    'https://dannurda.alwaysdata.net,https://www.dannurda.alwaysdata.net',
)

# alwaysdata sirve el sitio detras de un proxy que termina el HTTPS.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# ============================================================
# APLICACIONES
# ============================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',

    # --- Framework de interfaz (Tailwind CSS) ---
    'tailwind',
    'theme',

    # --- Aplicaciones (modulos) del sistema ---
    'cuentas',
    'espacios',
    'clientes',
    'reservas',
    'pagos',
    'cafeteria',
    'libreria',
    'contacto',
    'panel',
    'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # Permite que paginas web de otro dominio consuman la API.
    'corsheaders.middleware.CorsMiddleware',
    # WhiteNoise sirve los archivos estaticos con DEBUG = False.
    # Debe ir inmediatamente despues de SecurityMiddleware.
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bookspace_manager.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'cuentas.context_processors.datos_de_sesion',
            ],
        },
    },
]

WSGI_APPLICATION = 'bookspace_manager.wsgi.application'


# ============================================================
# BASE DE DATOS - MySQL (MariaDB) en alwaysdata
# ============================================================

if os.environ.get('DB_HOST'):
    # Produccion: MySQL. Todos los datos de conexion vienen del entorno.
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ['DB_NAME'],
            'USER': os.environ['DB_USER'],
            'PASSWORD': os.environ['DB_PASSWORD'],
            'HOST': os.environ['DB_HOST'],
            'PORT': os.environ.get('DB_PORT', '3306'),
            'OPTIONS': {
                'charset': 'utf8mb4',
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }
else:
    # Desarrollo local: SQLite, sin necesidad de instalar MySQL.
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# ============================================================
# INTERNACIONALIZACION
# ============================================================

LANGUAGE_CODE = 'es-ec'

TIME_ZONE = 'America/Guayaquil'

USE_I18N = True

USE_TZ = True


# ============================================================
# ARCHIVOS ESTATICOS
# ============================================================

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise comprime los estaticos y les agrega un hash al nombre
# para que el navegador no sirva versiones antiguas del CSS.
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ============================================================
# TAILWIND CSS (framework de interfaz)
# ============================================================
TAILWIND_APP_NAME = 'theme'
TAILWIND_USE_STANDALONE_BINARY = True


# ============================================================
# AUTENTICACION
# ============================================================
LOGIN_URL = 'cuentas:login'
LOGIN_REDIRECT_URL = 'panel:dashboard'
LOGOUT_REDIRECT_URL = 'cuentas:login'


# ============================================================
# PARAMETROS DE NEGOCIO
# ============================================================
HORA_APERTURA = 7      # el local abre a las 07:00
HORA_CIERRE = 22       # el local cierra a las 22:00


REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.AllowAny'],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DATETIME_FORMAT': '%Y-%m-%d %H:%M',
    # Limite de envios del formulario de contacto (por IP) contra spam.
    'DEFAULT_THROTTLE_RATES': {
        'contacto': '5/hour',
    },
}


# ============================================================
# CORS - acceso a la API desde otros dominios
# ============================================================
# La lectura es publica y se permite desde cualquier origen. PATCH y
# DELETE los usa el panel de administracion, pero cada uno exige el
# token de un administrador (ver api/permissions.py).
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_METHODS = ['GET', 'POST', 'PATCH', 'DELETE', 'OPTIONS']
