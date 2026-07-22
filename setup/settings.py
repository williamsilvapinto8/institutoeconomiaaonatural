"""
Django settings for setup project — Instituto Economia ao Natural
"""

import environ
from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# django-environ
env = environ.Env(
    DEBUG=(bool, False)
)
environ.Env.read_env(BASE_DIR / '.env')

# SECURITY
SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')

from django.core.exceptions import ImproperlyConfigured
if not DEBUG and 'insecure' in SECRET_KEY.lower():
    raise ImproperlyConfigured("A SECRET_KEY configurada para producao e semanticamente fraca/insegura.")

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=["institutoeconomiaaonatural.cocrias.com", "institutoeconomiaaonatural.cocrias.com.br", "localhost", "127.0.0.1"])

# URL base do sistema usada em links absolutos (e-mails, etc)
BASE_URL = env('BASE_URL', default='http://127.0.0.1:8000')

# Application definition
INSTALLED_APPS = [
    # Django default
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party
    'rest_framework',
    'django_q',
    'axes',
    # Project apps
    'accounts',
    'people',
    'events',
    'impact_forms',
    'communications',
    'content',
    'blog',
    'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'axes.middleware.AxesMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'accounts.middleware.MustChangePasswordMiddleware',
]

ROOT_URLCONF = 'setup.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'setup.wsgi.application'

# Database
# Usando SQLite para contornar o problema de codificacao (UnicodeDecodeError)
# causado pelo caractere 'ç' no path do Windows com a biblioteca libpq do PostgreSQL.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email Settings (Configuração SMTP)
EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='ola@cocrias.com')
EMAIL_HOST = env('EMAIL_HOST', default='pro106.dnspro.com.br')
EMAIL_PORT = env.int('EMAIL_PORT', default=465)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='ola@cocrias.com')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='xxxxx')
EMAIL_USE_SSL = env.bool('EMAIL_USE_SSL', default=True)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=False)

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# Django Q2 — Task Queue (ORM backend, sem Redis)
Q_CLUSTER = {
    'name': 'economia_natural',
    'workers': 2,
    'recycle': 500,
    'timeout': 60,
    'compress': True,
    'save_limit': 250,
    'queue_limit': 500,
    'cpu_affinity': 1,
    'label': 'Django Q2',
    'orm': 'default',
}
CSRF_TRUSTED_ORIGINS = [
    'https://institutoeconomiaaonatural.cocrias.com.br',
]
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# Auth redirects
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

# Django Axes Security Configuration
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.ModelBackend',
]
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1  # 1 hora
AXES_LOCKOUT_TEMPLATE = None # Usa resposta padrão de erro do Django ou podemos customizar
AXES_RESET_ON_SUCCESS = True


# Security headers for Production (activated when DEBUG is False)
if not DEBUG:
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    CSRF_TRUSTED_ORIGINS = ['https://institutoeconomiaaonatural.cocrias.com']
    
    # Configuração de envio de erros e logs estruturados em produção
    import os
    LOGS_DIR = BASE_DIR / 'logs'
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR)
        
    ADMINS = [('Equipe IEN', 'suporte@institutoeconomiaaonatural.cocrias.com')]
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '{levelname} {asctime} {module} {message}',
                'style': '{',
            },
        },
        'handlers': {
            'file': {
                'level': 'ERROR',
                'class': 'logging.FileHandler',
                'filename': str(LOGS_DIR / 'django_error.log'),
                'formatter': 'verbose',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['file'],
                'level': 'ERROR',
                'propagate': True,
            },
        },
    }


