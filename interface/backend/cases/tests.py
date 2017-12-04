from backend.cases.factories import (
    CandidateFactory,
    CaseFactory,
    NoduleFactory
)
from backend.cases.models import Case, Candidate, Nodule
from backend.images.models import ImageSeries, ImageLocation
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse

from . import enums


class SmokeTest(APITestCase):
    def assertDictIsSubset(self, subset, superset):
        self.assertTrue(set(subset.items()).issubset(set(superset.items())))

    def test_create_case(self):
        case = CaseFactory()
        self.assertIsNotNone(case.series)

    def test_create_candidate(self):
        candidate = CandidateFactory()

        # check p(concerning)
        self.assertGreater(candidate.probability_concerning, 0.0)
        self.assertLess(candidate.probability_concerning, 1.0)

        # check the centroid location
        self.assertIsInstance(candidate.centroid.x, int)
        self.assertIsInstance(candidate.centroid.y, int)
        self.assertIsInstance(candidate.centroid.z, int)

    def test_create_nodule(self):
        nodule = NoduleFactory()

        # check the centroid location
        self.assertIsInstance(nodule.centroid.x, int)
        self.assertIsInstance(nodule.centroid.y, int)
        self.assertIsInstance(nodule.centroid.z, int)

    def test_report(self):
        url = reverse('case-report', kwargs={'pk': 0})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        series = ImageSeries.objects.create(patient_id='42', series_instance_uid='13', uri='/images/1.dcm')
        new_case = Case.objects.create(series=series)
        centroid1 = ImageLocation.objects.create(series=series, x=1, y=2, z=3)
        candidate1 = Candidate.objects.create(case=new_case, centroid=centroid1, probability_concerning=0.8)
        centroid2 = ImageLocation.objects.create(series=series, x=10, y=20, z=30)
        candidate2 = Candidate.objects.create(case=new_case, centroid=centroid2, probability_concerning=0.98)
        nodule1 = Nodule.objects.create(case=new_case, candidate=candidate1, centroid=centroid1)
        nodule2 = Nodule.objects.create(case=new_case, candidate=candidate2, centroid=centroid2)

        url = reverse('case-report', kwargs={'pk': new_case.pk})
        response = self.client.get(url)
        expected = {'patient_id': '42', 'series_instance_uid': '13', 'uri': '/images/1.dcm'}
        self.assertDictIsSubset(expected, response.data['series'])

        candidate1_dict = dict(response.data['candidates'][0])
        self.assertEqual(candidate1_dict['probability_concerning'], 0.8)
        self.assertEqual(candidate1_dict['centroid']['x'], nodule1.centroid.x)
        self.assertEqual(candidate1_dict['centroid']['y'], nodule1.centroid.y)
        self.assertEqual(candidate1_dict['centroid']['z'], nodule1.centroid.z)

        candidate2_dict = response.data['candidates'][1]
        self.assertEqual(candidate2_dict['probability_concerning'], 0.98)
        self.assertEqual(candidate2_dict['centroid']['x'], nodule2.centroid.x)
        self.assertEqual(candidate2_dict['centroid']['y'], nodule2.centroid.y)
        self.assertEqual(candidate2_dict['centroid']['z'], nodule2.centroid.z)

        nodule1_dict = response.data['nodules'][0]
        self.assertEqual(nodule1_dict['centroid']['x'], nodule1.centroid.x)
        self.assertEqual(nodule1_dict['centroid']['y'], nodule1.centroid.y)
        self.assertEqual(nodule1_dict['centroid']['z'], nodule1.centroid.z)

        nodule2_dict = response.data['nodules'][1]
        self.assertEqual(nodule2_dict['centroid']['x'], nodule2.centroid.x)
        self.assertEqual(nodule2_dict['centroid']['y'], nodule2.centroid.y)
        self.assertEqual(nodule2_dict['centroid']['z'], nodule2.centroid.z)

    def test_update_nodule_lung_orientation(self):
        nodule = NoduleFactory()
        url = reverse('nodule-detail', kwargs={'pk': nodule.pk})

        self.assertEquals(nodule.lung_orientation, enums.LungOrientation.NONE.value)

        resp = self.client.patch(url, {'lung_orientation': enums.LungOrientation.LEFT.value})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        nodule.refresh_from_db()
        self.assertEquals(nodule.lung_orientation, enums.LungOrientation.LEFT.value)

        resp = self.client.patch(url, {'lung_orientation': enums.LungOrientation.RIGHT.value})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        nodule.refresh_from_db()
        self.assertEquals(nodule.lung_orientation, enums.LungOrientation.RIGHT.value)

        resp = self.client.patch(url, {'lung_orientation': enums.LungOrientation.NONE.value})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        nodule.refresh_from_db()
        self.assertEquals(nodule.lung_orientation, enums.LungOrientation.NONE.value)

    def test_candidates_mark(self):
        candidate = CandidateFactory()
        url = reverse('candidate-detail', kwargs={'pk': candidate.pk})
        resp = self.client.patch(url, {'review_result': enums.CandidateReviewResult.MARKED.value})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        candidate.refresh_from_db()
        self.assertEquals(candidate.review_result, enums.CandidateReviewResult.MARKED.value)

    def test_candidates_dismiss(self):
        candidate = CandidateFactory()
        url = reverse('candidate-detail', kwargs={'pk': candidate.pk})
        resp = self.client.patch(url, {'review_result': enums.CandidateReviewResult.DISMISSED.value})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        candidate.refresh_from_db()
        self.assertEquals(candidate.review_result, enums.CandidateReviewResult.DISMISSED.value)
