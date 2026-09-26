"""
WSGI config for AssureX Claim Engine project.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assurex.settings.development')

application = get_wsgi_application()
