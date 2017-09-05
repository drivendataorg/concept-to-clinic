from backend.api.views import (
    CaseViewSet,
    CandidateViewSet,
    NoduleViewSet,
    ImageSeriesViewSet,
    candidate_mark,
    candidate_dismiss,
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
    url(r'^candidates/(?P<candidate_id>\d+)/dismiss$', candidate_dismiss, name='candidate-dismiss'),
    url(r'^candidates/(?P<candidate_id>\d+)/mark$', candidate_mark, name='candidate-mark'),
]
