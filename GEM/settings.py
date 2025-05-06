"""
Configuración base para el proyecto GEM.

Generado por 'django-admin startproject' usando Django 5.2.
Documentación oficial:
- https://docs.djangoproject.com/en/5.2/topics/settings/
- https://docs.djangoproject.com/en/5.2/ref/settings/
"""

import os
from pathlib import Path
##from dotenv import load_dotenv  # Requiere instalar python-dotenv

##load_dotenv()  # Carga las variables desde el archivo .env

# Base directoryS
BASE_DIR = Path(__file__).resolve().parent.parent

# Seguridad
SECRET_KEY = os.getenv('SECRET_KEY', 'clave-insegura-solo-dev')
DEBUG = os.getenv('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# Aplicaciones instaladas
INSTALLED_APPS = [
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Apps locales
    'Core',
    # 'apps.usuarios',
    # 'apps.cursos',

    # Terceros (si usas DRF, crispy-forms, etc.)
    # 'rest_framework',
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# URL principal
ROOT_URLCONF = 'GEM.urls'

# Plantillas
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'Core/templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# WSGI
WSGI_APPLICATION = 'GEM.wsgi.application'


# nuevas base de datos postgres 
DATABASES = {
    'default': {
        'ENGINE':'django.db.backends.postgres',
        'NAME': 'GEM'
        'USER': 'postgres',
        'PASSWORD': 'gem1234',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Base de datos
# DATABASES = {
#     'default': {
#         'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.sqlite3'),
#         'NAME': os.getenv('DB_NAME', BASE_DIR / 'db.sqlite3'),
#         'USER': os.getenv('DB_USER', ''),
#         'PASSWORD': os.getenv('DB_PASSWORD', ''),
#         'HOST': os.getenv('DB_HOST', ''),
#         'PORT': os.getenv('DB_PORT', ''),
#     }
# }

# Validadores de contraseña
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internacionalización
LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True

# Archivos estáticos y media
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'Core/static',
]
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Campo automático por defecto
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Modelo de usuario personalizado
AUTH_USER_MODEL = 'Core.Usuario'

# URLs de autenticación
LOGIN_REDIRECT_URL = 'admin_panel'
LOGOUT_REDIRECT_URL = 'home'
LOGIN_URL = 'accounts/login/'


# Configuración de Bootstrap
BOOTSTRAP5 = {
    'include_jquery': True,
}

# Configuración de DataTables
DATATABLES = {
    'language': {
        'url': '//cdn.datatables.net/plug-ins/1.13.7/i18n/es-ES.json'
    }
}

# Configuración de correo electrónico
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('EMAIL_HOST_USER', '')
