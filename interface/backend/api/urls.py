from collections import OrderedDict

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
    url,
)
from django.urls import NoReverseMatch
from rest_framework import routers
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.urlpatterns import format_suffix_patterns


class RelativeUrlRootView(routers.APIRootView):
    """ Provides relative URLs for the available endpoints.
    """
    def get(self, request, *args, **kwargs):
        # Return a plain {"name": "hyperlink"} response.
        ret = OrderedDict()
        namespace = request.resolver_match.namespace
        for key, url_name in self.api_root_dict.items():
            if namespace:
                url_name = namespace + ':' + url_name
            try:
                ret[key] = reverse(
                    url_name,
                    args=args,
                    kwargs=kwargs,
                    request=None,
                    format=kwargs.get('format', None)
                )
            except NoReverseMatch:
                # Don't bail out if eg. no list routes exist, only detail routes.
                continue

        return Response(ret)


router = routers.DefaultRouter()
router.APIRootView = RelativeUrlRootView

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
