from django.test import TestCase

from backend.cases.factories import (
    CandidateFactory,
    CaseFactory,
    NoduleFactory
)


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
