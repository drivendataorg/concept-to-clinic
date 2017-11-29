from backend.api.serializers import NoduleSerializer
from backend.cases.factories import (
    CaseFactory,
    NoduleFactory
)
from django.test import TestCase
from django.urls import reverse
from rest_framework import status


class ViewTest(TestCase):
    def test_nodule_list_viewset(self):
        # first try an endpoint without a nodule
        url = reverse('nodule-list')
        response = self.client.get(url)
        payload = response.json()
        self.assertListEqual(payload, [])

        # now create a nodule and figure out what we expect to see in the list
        case = CaseFactory()
        nodules = NoduleFactory.create_batch(size=3, case=case)
        serialized = [NoduleSerializer(n, context={'request': None}) for n in nodules]
        expected = [s.data for s in serialized]

        # check the actual response
        response = self.client.get(url)
        payload = response.json()
        self.assertListEqual(payload, expected)

    def test_images_available_view(self):
        url = reverse('images-available')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_images_metadata_view(self):
        url = reverse('images-metadata')
        response = self.client.get(url, {
            'dicom_location': '/images/LIDC-IDRI-0002/'
            '1.3.6.1.4.1.14519.5.2.1.6279.6001.490157381160200744295382098329/'
            '1.3.6.1.4.1.14519.5.2.1.6279.6001.619372068417051974713149104919/-80.750000.dcm'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
