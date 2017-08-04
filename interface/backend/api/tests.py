from django.test import (
    RequestFactory,
    TestCase
)
from django.urls import reverse

from backend.api.serializers import NoduleSerializer
from backend.cases.factories import (
    CaseFactory,
    NoduleFactory
)


class ViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_nodule_list_viewset(self):
        # first try an endpoint without a nodule
        url = reverse('nodule-list')
        response = self.client.get(url)
        payload = response.json()
        self.assertListEqual(payload, [])

        # now create a nodule and figure out what we expect to see in the list
        case = CaseFactory()
        nodules = NoduleFactory.create_batch(size=3, case=case)
        request = self.factory.get(url)
        serialized = [NoduleSerializer(n, context={'request': request}) for n in nodules]
        expected = [s.data for s in serialized]

        # check the actual response
        response = self.client.get(url)
        payload = response.json()
        self.assertListEqual(payload, expected)
