"""
Adapted from pydanny/django-cookiecutter
"""
from config.settings.base import *  # noqa

# This ensures that Django will be able to detect a secure connection
# properly on Heroku.
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# SECURITY CONFIGURATION
# ------------------------------------------------------------------------------
# See https://docs.djangoproject.com/en/1.9/ref/middleware/#module-django.middleware.security
# and https://docs.djangoproject.com/ja/1.9/howto/deployment/checklist/#run-manage-py-check-deploy

# set this to 60 seconds and then to 518400 when you can prove it works
# SECURE_HSTS_SECONDS = 60
# SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool('DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS', default=True)
# SECURE_CONTENT_TYPE_NOSNIFF = env.bool('DJANGO_SECURE_CONTENT_TYPE_NOSNIFF', default=True)
# SECURE_BROWSER_XSS_FILTER = env.bool('DJANGO_SECURE_BROWSER_XSS_FILTER', default=True)
# SESSION_COOKIE_SECURE = env.bool('DJANGO_SESSION_COOKIE_SECURE', default=True)
SESSION_COOKIE_HTTPONLY = env.bool('DJANGO_SESSION_COOKIE_HTTPONLY', default=True)
# SECURE_SSL_REDIRECT = env.bool('DJANGO_SECURE_SSL_REDIRECT', default=True)
CSRF_COOKIE_SECURE = env.bool('DJANGO_CSRF_COOKIE_SECURE', default=True)
CSRF_COOKIE_HTTPONLY = env.bool('DJANGO_CSRF_COOKIE_HTTPONLY', default=True)
CSRF_USE_SESSIONS = env.bool('DJANGO_CSRF_USE_SESSIONS', default=False)
X_FRAME_OPTIONS = 'DENY'

# SITE CONFIGURATION
# ------------------------------------------------------------------------------
# Hosts/domain names that are valid for this site
# See https://docs.djangoproject.com/en/1.6/ref/settings/#allowed-hosts
ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=['*'])
# END SITE CONFIGURATION

INSTALLED_APPS += ["gunicorn"]
