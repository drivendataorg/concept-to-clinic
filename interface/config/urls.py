from django.conf import settings
from django.conf.urls import (
    include,
    url
)
from django.views.static import serve
from django.views.generic import RedirectView

urlpatterns = (
    url(r'^api/', include('backend.api.urls', namespace='')),
    url(r'^', RedirectView.as_view(url='api/'), name="available-routes"),
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
