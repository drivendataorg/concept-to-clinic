from django.test import (
    RequestFactory,
    TestCase
)
from django.urls import reverse
from rest_framework.test import APIRequestFactory
from rest_framework import status

from backend.api.serializers import NoduleSerializer
from backend.cases.factories import (
    CaseFactory,
    NoduleFactory
)


class ViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.rest_factory = APIRequestFactory()

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

    def test_images_available_view(self):
        url = reverse('images-available')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
