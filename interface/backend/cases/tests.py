import json

from backend.cases.factories import (
    CandidateFactory,
    CaseFactory,
    NoduleFactory
)
from backend.cases.models import Case, Candidate, Nodule
from backend.images.models import ImageSeries, ImageLocation
from django.test import TestCase
from django.urls import reverse

from . import enums


class SmokeTest(TestCase):
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
        def assertDictContainsNestedSubset(superset, subset):
            self.assertTrue(all(item in superset.items() for item in subset.items()))

        url = reverse('case-report', kwargs={'case_id': 0}) + ".json"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        series = ImageSeries.objects.create(patient_id='42', series_instance_uid='13', uri='/images/1.dcm')
        case = Case.objects.create(series=series)
        centroid1 = ImageLocation.objects.create(series=series, x=1, y=2, z=3)
        candidate1 = Candidate.objects.create(case=case, centroid=centroid1, probability_concerning=0.8)
        centroid2 = ImageLocation.objects.create(series=series, x=10, y=20, z=30)
        candidate2 = Candidate.objects.create(case=case, centroid=centroid2, probability_concerning=0.98)
        nodule1 = Nodule.objects.create(case=case, candidate=candidate1, centroid=centroid1)
        nodule2 = Nodule.objects.create(case=case, candidate=candidate2, centroid=centroid2)

        url = reverse('case-report', kwargs={'case_id': case.id}) + ".json"
        response = self.client.get(url)
        payload = json.loads(response.content)
        self.assertEqual(payload['id'], case.id)

        self.assertDictContainsSubset(payload['series'],
                                      {'id': series.id, 'patient_id': '42', 'series_instance_uid': '13',
                                       'uri': '/images/1.dcm'})

        candidate1_dict = payload['candidates'][0]
        self.assertEqual(candidate1_dict['id'], candidate1.id)
        self.assertEqual(candidate1_dict['case_id'], case.id)
        self.assertEqual(candidate1_dict['probability_concerning'], 0.8)
        self.assertEqual(candidate1_dict['centroid']['series'],
                         {'id': series.id, 'patient_id': '42', 'series_instance_uid': '13', 'uri': '/images/1.dcm'})
        self.assertEqual(candidate1_dict['centroid']['x'], 1)
        self.assertEqual(candidate1_dict['centroid']['y'], 2)
        self.assertEqual(candidate1_dict['centroid']['z'], 3)

        candidate2_dict = payload['candidates'][1]
        self.assertEqual(candidate2_dict['id'], candidate2.id)
        self.assertEqual(candidate2_dict['case_id'], case.id)
        self.assertEqual(candidate2_dict['probability_concerning'], 0.98)
        self.assertEqual(candidate2_dict['centroid']['series'],
                         {'id': series.id, 'patient_id': '42', 'series_instance_uid': '13', 'uri': '/images/1.dcm'})
        self.assertEqual(candidate2_dict['centroid']['x'], 10)
        self.assertEqual(candidate2_dict['centroid']['y'], 20)
        self.assertEqual(candidate2_dict['centroid']['z'], 30)

        nodule1_dict = payload['nodules'][0]
        self.assertEqual(nodule1_dict['id'], nodule1.id)
        self.assertEqual(nodule1_dict['centroid']['id'], centroid1.id)
        self.assertEqual(nodule1_dict['centroid']['series'],
                         {'id': series.id, 'patient_id': '42', 'series_instance_uid': '13', 'uri': '/images/1.dcm'})
        self.assertEqual(nodule1_dict['centroid']['x'], 1)
        self.assertEqual(nodule1_dict['centroid']['y'], 2)
        self.assertEqual(nodule1_dict['centroid']['z'], 3)

        nodule2_dict = payload['nodules'][1]
        self.assertEqual(nodule2_dict['id'], nodule2.id)
        self.assertEqual(nodule2_dict['centroid']['series'],
                         {'id': series.id, 'patient_id': '42', 'series_instance_uid': '13', 'uri': '/images/1.dcm'})
        self.assertEqual(nodule2_dict['centroid']['x'], 10)
        self.assertEqual(nodule2_dict['centroid']['y'], 20)
        self.assertEqual(nodule2_dict['centroid']['z'], 30)

    def test_update_nodule_lung_orientation(self):
        nodule = NoduleFactory()
        url = reverse('nodule-update', kwargs={'nodule_id': nodule.id})

        self.assertEquals(nodule.lung_orientation, enums.LungOrientation.NONE.value)

        self.client.post(url, json.dumps({'lung_orientation': 'LEFT'}), 'application/json')
        nodule.refresh_from_db()
        self.assertEquals(nodule.lung_orientation, enums.LungOrientation.LEFT.value)

        self.client.post(url, json.dumps({'lung_orientation': 'RIGHT'}), 'application/json')
        nodule.refresh_from_db()
        self.assertEquals(nodule.lung_orientation, enums.LungOrientation.RIGHT.value)

        self.client.post(url, json.dumps({'lung_orientation': 'NONE'}), 'application/json')
        nodule.refresh_from_db()
        self.assertEquals(nodule.lung_orientation, enums.LungOrientation.NONE.value)
