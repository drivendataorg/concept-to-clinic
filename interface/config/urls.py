from django.conf import settings
from django.conf.urls import (
    include,
    url
)
from django.views.static import serve

urlpatterns = (
    url(r'^api/', include('backend.api.urls', namespace='')),
)

if settings.DEBUG:
    urlpatterns += (
        url(r'^storage/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    )

    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns += (
            url(r'^__debug__/', include(debug_toolbar.urls)),
        )
