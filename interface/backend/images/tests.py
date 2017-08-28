from django.test import TestCase

from backend.images.factories import ImageSeriesFactory
from backend.images.models import ImageSeries


class SmokeTest(TestCase):
    def test_create_image_series(self):
        image_series = ImageSeriesFactory()
        self.assertRegex(image_series.series_instance_uid, '^[0-9\.]{64}')
        self.assertIn(image_series.series_instance_uid, image_series.uri)

    def test_get_create_image_series(self):
        uri = '/images/LIDC-IDRI-0001/1.3.6.1.4.1.14519.5.2.1.6279.6001.298806137288633453246975630178/' \
          '1.3.6.1.4.1.14519.5.2.1.6279.6001.179049373636438705059720603192'
        image_series, created = ImageSeries.get_or_create(uri)
        assert created
        assert image_series.patient_id == 'LIDC-IDRI-0001'
        assert image_series.series_instance_uid == '1.3.6.1.4.1.14519.5.2.1.6279.6001.179049373636438705059720603192'
        assert image_series.uri == uri
        image_series, created = ImageSeries.get_or_create(uri)
        assert not created
        assert image_series.patient_id == 'LIDC-IDRI-0001'
        assert image_series.series_instance_uid == '1.3.6.1.4.1.14519.5.2.1.6279.6001.179049373636438705059720603192'
        assert image_series.uri == uri
