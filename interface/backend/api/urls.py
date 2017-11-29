from backend.api.views import (
    CaseViewSet,
    CandidateViewSet,
    NoduleViewSet,
    ImageSeriesViewSet,
    ImageAvailableApiView,
    ImageMetadataApiView,
    review_candidate,
    case_report,
    nodule_update,
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
    url(r'^images/metadata$', ImageMetadataApiView.as_view(), name='images-metadata'),
    url(r'^candidates-info$', candidates_info, name='candidates-info'),
    url(r'^candidates/(?P<candidate_id>\d+)/review$', review_candidate, name='review-candidate'),
    url(r'^candidates/(?P<candidate_id>\d+)/move$', update_candidate_location, name='update-candidate-location'),
    url(r'^nodules/(?P<nodule_id>\d+)/update$', nodule_update, name='nodule-update'),
]

# Support different suffixes
urlpatterns += format_suffix_patterns([url(r'^cases/(?P<case_id>\d+)/report$', case_report, name='case-report')])
