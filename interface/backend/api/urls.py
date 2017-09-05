from backend.api.views import (
    CaseViewSet,
    CandidateViewSet,
    NoduleViewSet,
    ImageSeriesViewSet,
)
from django.conf.urls import (
    include,
    url
)
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'cases', CaseViewSet)
router.register(r'candidates', CandidateViewSet)
router.register(r'nodules', NoduleViewSet)
router.register(r'images', ImageSeriesViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
