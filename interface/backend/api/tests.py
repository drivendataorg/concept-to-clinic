import os

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from backend.api.serializers import (
    ImageFileSerializer,
    ImageSeriesSerializer,
    NoduleSerializer,
)

from backend.images.models import (
    ImageFile,
    ImageSeries,
)

from backend.cases.factories import (
    CaseFactory,
    CandidateFactory
)

from backend.cases import enums


class ViewTest(APITestCase):
    def test_nodule_list_viewset(self):
        # first try an endpoint without a nodule
        url = reverse('nodule-list')
        response = self.client.get(url)
        payload = response.json()
        self.assertListEqual(payload, [])

        # now create a nodule and figure out what we expect to see in the list
        case = CaseFactory()
        candidates = CandidateFactory.create_batch(size=3, case=case)
        nodules = []
        for candidate in candidates:
            nodule, _ = candidate.get_or_create_nodule()
            nodules.append(nodule)
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

    def test_images_preview_view(self):
        url = reverse('images-preview')
        response = self.client.get(url, {
            'dicom_location': '/images/LIDC-IDRI-0002/'
            '1.3.6.1.4.1.14519.5.2.1.6279.6001.490157381160200744295382098329/'
            '1.3.6.1.4.1.14519.5.2.1.6279.6001.619372068417051974713149104919/-80.750000.dcm'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_metdata = {
            'slice_thickness': 1.25,
            'slice_location': -80.75,
            'rescale_slope': 1,
            'rows': 512,
            'columns': 512,
            'pixel_spacing_col': 0.681641,
            'pixel_spacing_row': 0.681641,
        }

        response_data = response.json()
        for prop, expected in expected_metdata.items():
            self.assertEqual(response_data['metadata'].pop(prop), expected)

        # assert we have checked all the properties with pop
        self.assertFalse(len(response_data['metadata']))

        # assert we have image data at all
        self.assertIsNotNone(response_data['image'])

    def test_images_preview_bad_paths(self):
        url = reverse('images-preview')
        response = self.client.get(url, {
            'dicom_location': '/etc/passwd'
        })
        self.assertEqual(response.status_code, 403)

        response = self.client.get(url, {
            'dicom_location': '/images/does_not_exist'
        })
        self.assertEqual(response.status_code, 404)

    def test_candidates_mark(self):
        candidate = CandidateFactory()

        url = reverse('candidate-detail', kwargs={'pk': candidate.id})
        response = self.client.patch(url, {'review_result': enums.CandidateReviewResult.MARKED.value})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_candidates_dismiss(self):
        candidate = CandidateFactory()

        url = reverse('candidate-detail', kwargs={'pk': candidate.id})
        response = self.client.patch(url, {'review_result': enums.CandidateReviewResult.DISMISSED.value})

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class SerializerTest(TestCase):
    """ Tests the serializers that perform any custom logic.

        In general, create logic is tested by posting in the ViewTest test cases.
    """
    def test_image_file_serializer(self):
        image_file = ImageFile(path='/my_path')
        serialized = ImageFileSerializer(image_file)

        # we construct the preview url, so test it here
        self.assertEqual(serialized['preview_url'].value,
                         '/api/images/preview?dicom_location=/my_path')
        for s in serialized:
            self.assertIsNone(s.errors)

    def test_image_series_serializer(self):
        image_series = ImageSeries(uri='/images/LIDC-IDRI-0001/'
                                   '1.3.6.1.4.1.14519.5.2.1.6279.6001.298806137288633453246975630178/'
                                   '1.3.6.1.4.1.14519.5.2.1.6279.6001.179049373636438705059720603192')

        serialized = ImageSeriesSerializer(image_series, context={'request': None})

        for img in serialized['images'].value:
            self.assertTrue(os.path.exists(img.path))

        for s in serialized:
            self.assertIsNone(s.errors)

        # get, don't create if it exists
        orig_id = serialized.instance.id
        serialized = ImageSeriesSerializer(image_series, context={'request': None})
        self.assertEqual(orig_id, serialized.instance.id)
