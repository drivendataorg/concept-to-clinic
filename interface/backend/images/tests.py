from django.test import TestCase

from backend.images.factories import ImageSeriesFactory


class SmokeTest(TestCase):
    def test_create_image_series(self):
        image_series = ImageSeriesFactory()
        self.assertRegex(image_series.series_instance_uid, '^[0-9\.]{64}')
        self.assertIn(image_series.series_instance_uid, image_series.uri)
