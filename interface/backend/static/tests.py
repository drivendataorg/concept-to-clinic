from django.test import TestCase
from django.urls import reverse


class SmokeTest(TestCase):
    def test_landing(self):
        url = reverse('static:home')
        resp = self.client.get(url)
        self.assertContains(resp, 'Concept to Clinic')
        self.assertEqual(resp.status_code, 200)
