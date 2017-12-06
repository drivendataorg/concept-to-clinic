from backend.api.views import (
    CaseViewSet,
    CandidateViewSet,
    NoduleViewSet,
    ImageSeriesViewSet,
    ImageAvailableApiView,
    ImagePreviewApiView,
    case_report,
    update_candidate_location,
    candidates_info
)
from django.conf.urls import (
    include,
    url
)
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns

router = routers.DefaultRouter()
router.register(r'cases', CaseViewSet)
router.register(r'candidates', CandidateViewSet)
router.register(r'nodules', NoduleViewSet)
router.register(r'images', ImageSeriesViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^images/available$', ImageAvailableApiView.as_view(), name='images-available'),
    url(r'^images/preview$', ImagePreviewApiView.as_view(), name='images-preview'),
    url(r'^candidates-info$', candidates_info, name='candidates-info'),
    url(r'^candidates/(?P<candidate_id>\d+)/move$', update_candidate_location, name='update-candidate-location'),
]

# Support different suffixes
urlpatterns += format_suffix_patterns([url(r'^cases/(?P<pk>\d+)/report$', case_report, name='case-report')])
