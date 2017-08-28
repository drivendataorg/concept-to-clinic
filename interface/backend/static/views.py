from django.conf import settings
from django.shortcuts import render


def home(request):
    return render(request, '../frontend/index.html', {'short_hash': settings.APP_VERSION_NUMBER})
