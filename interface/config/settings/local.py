"""
Adapted from pydanny/django-cookiecutter
"""

from config.settings.base import *  # noqa

# DEBUG
# ------------------------------------------------------------------------------
DEBUG = env.bool('DEBUG', default=True)
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG
ALLOWED_HOSTS = ['*']

# Mail settings
# ------------------------------------------------------------------------------
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# CACHING
# ------------------------------------------------------------------------------
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# django-debug-toolbar
# ------------------------------------------------------------------------------
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
INSTALLED_APPS += ['debug_toolbar']
INTERNAL_IPS = ('127.0.0.1',)
# django-extensions
# ------------------------------------------------------------------------------
INSTALLED_APPS += ['django_extensions']
