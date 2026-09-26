"""
AssureX Claim Engine - Base Django Settings
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-assurex-dev-key-change-in-production-2024')

DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
]

THIRD_PARTY_APPS = [
    'crispy_forms',
    'crispy_bootstrap5',
    'django_extensions',
    'rest_framework',
]

LOCAL_APPS = [
    'apps.accounts',
    'apps.products',
    'apps.warranties',
    'apps.claims',
    'apps.reviewer',
    'apps.administrator',
    'apps.notifications',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'assurex.urls'

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
                # AssureX custom processors
                'apps.accounts.context_processors.notifications_count',
                'apps.accounts.context_processors.user_role_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'assurex.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'database' / 'assurex.db',
    }
}

# Override with DATABASE_URL if set (Railway / production)
_db_url = os.environ.get('DATABASE_URL', '')
if _db_url:
    try:
        import dj_database_url as _dj_db
        DATABASES['default'] = _dj_db.config(
            default=_db_url,
            conn_max_age=600,
            conn_health_checks=True,
        )
    except ImportError:
        pass  # dj-database-url not installed — keep SQLite

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Auth URLs
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Karachi'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# File Upload
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

ALLOWED_DOCUMENT_TYPES = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png']
MAX_DOCUMENT_SIZE_MB = 5

# ML Model paths
ML_MODEL_PATH = BASE_DIR / 'model' / 'python_model' / 'assurex_model.pkl'
ML_PREPROCESSOR_PATH = BASE_DIR / 'model' / 'python_model' / 'preprocessor.pkl'
ML_LABEL_ENCODER_PATH = BASE_DIR / 'model' / 'python_model' / 'label_encoder.pkl'
TM_MODEL_PATH = BASE_DIR / 'model' / 'teachable_machine'

# Warranty Policy files
WARRANTY_POLICIES_DIR = BASE_DIR / 'policies'

# Confidence thresholds (configurable via Admin)
DEFAULT_CONFIDENCE_THRESHOLD = 0.70
DEFAULT_CONFIDENCE_DIFF_STRONG = 5.0    # % - Strong match
DEFAULT_CONFIDENCE_DIFF_ACCEPTABLE = 15.0  # % - Acceptable match
DEFAULT_CONFIDENCE_DIFF_WEAK = 25.0     # % - Weak match
# > 25% = Model Disagreement / Uncertain

# Warranty expiry alert days
WARRANTY_EXPIRY_ALERT_DAYS = 30

# OCR Settings
TESSERACT_PATH = os.environ.get('TESSERACT_PATH', r'C:\Program Files\Tesseract-OCR\tesseract.exe')

# Session
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# Messages
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.DEBUG: 'secondary',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

# ─────────────────────────────────────────────────────────────────
# Email Configuration
# Dev:  prints emails to the console (no SMTP needed)
# Prod: set EMAIL_HOST_USER + EMAIL_HOST_PASSWORD in .env
# ─────────────────────────────────────────────────────────────────
_email_host_user = os.environ.get('EMAIL_HOST_USER', '')

if DEBUG or not _email_host_user:
    # Console backend — emails printed to terminal during development
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND  = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST     = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_PORT     = int(os.environ.get('EMAIL_PORT', 587))
    EMAIL_USE_TLS  = True
    EMAIL_HOST_USER     = _email_host_user
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')

DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'AssureX <noreply@assurex.com>')
SERVER_EMAIL       = DEFAULT_FROM_EMAIL
