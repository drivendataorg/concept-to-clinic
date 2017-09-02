from django.conf import settings


def settings_context(request):
    return {'settings': settings}
