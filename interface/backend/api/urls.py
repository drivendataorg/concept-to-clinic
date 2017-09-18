from backend.api.views import (
    CaseViewSet,
    CandidateViewSet,
    NoduleViewSet,
    ImageSeriesViewSet,
    ImageAvailableApiView,
    candidate_mark,
    candidate_dismiss,
    case_report,
    nodule_update
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
    url(r'^candidates/(?P<candidate_id>\d+)/dismiss$', candidate_dismiss, name='candidate-dismiss'),
    url(r'^candidates/(?P<candidate_id>\d+)/mark$', candidate_mark, name='candidate-mark'),
    url(r'^nodules/(?P<nodule_id>\d+)/update$', nodule_update, name='nodule-update'),
]

# Support different suffixes
urlpatterns += format_suffix_patterns([url(r'^cases/(?P<case_id>\d+)/report$', case_report, name='case-report')])
