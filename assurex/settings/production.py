"""
AssureX - Production Settings (Railway)
"""
from .base import *
import os

DEBUG = False

# ── ALLOWED HOSTS ──────────────────────────────────────────────
# Railway sets RAILWAY_PUBLIC_DOMAIN automatically
# Also read custom ALLOWED_HOSTS env var (comma-separated)
_railway_domain = os.environ.get('RAILWAY_PUBLIC_DOMAIN', '')
_allowed = os.environ.get('ALLOWED_HOSTS', '')
ALLOWED_HOSTS = [h.strip() for h in _allowed.split(',') if h.strip()]
if _railway_domain and _railway_domain not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(_railway_domain)
if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ['*']   # fallback — restrict after go-live

# ── DATABASE (Railway PostgreSQL via DATABASE_URL) ─────────────
import dj_database_url
_db_url = os.environ.get('DATABASE_URL', '')
if _db_url:
    DATABASES = {
        'default': dj_database_url.config(
            default=_db_url,
            conn_max_age=600,
            conn_health_checks=True,
            ssl_require=True,
        )
    }
else:
    # Fallback to individual env vars (manual PostgreSQL setup)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME':     os.environ.get('DB_NAME', 'assurex'),
            'USER':     os.environ.get('DB_USER', 'assurex_user'),
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
            'HOST':     os.environ.get('DB_HOST', 'localhost'),
            'PORT':     os.environ.get('DB_PORT', '5432'),
        }
    }

# ── SSL / PROXY ────────────────────────────────────────────────
# Railway terminates SSL at the proxy — do NOT redirect inside app
SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE  = True
CSRF_COOKIE_SECURE     = True
SECURE_HSTS_SECONDS    = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD    = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# ── TESSERACT (Linux path on Railway) ─────────────────────────
TESSERACT_PATH = os.environ.get('TESSERACT_PATH', '/usr/bin/tesseract')

# ── EMAIL ──────────────────────────────────────────────────────
EMAIL_BACKEND      = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST         = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT         = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS      = True
EMAIL_HOST_USER    = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD= os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'AssureX <noreply@assurex.com>')

# ── LOGGING — stdout (Railway captures stdout logs) ───────────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '[{levelname}] {asctime} {module}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'assurex': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
