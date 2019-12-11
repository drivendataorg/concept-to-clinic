import os

from django.core.exceptions import PermissionDenied
from django.test import TestCase

from backend.images.factories import ImageSeriesFactory
from backend.images.models import (
    ImageFile,
    ImageSeries,
)


class SmokeTest(TestCase):
    def test_create_image_series(self):
        image_series = ImageSeriesFactory()
        self.assertRegex(image_series.series_instance_uid, r'^[0-9\.]{64}')
        self.assertIn(image_series.series_instance_uid, image_series.uri)

    def test_get_create_image_series(self):
        uri = '/images/LIDC-IDRI-0001/' \
              '1.3.6.1.4.1.14519.5.2.1.6279.6001.298806137288633453246975630178/' \
              '1.3.6.1.4.1.14519.5.2.1.6279.6001.179049373636438705059720603192'

        image_series, created = ImageSeries.get_or_create(uri)
        assert created
        assert image_series.patient_id == 'LIDC-IDRI-0001'
        assert image_series.series_instance_uid == '1.3.6.1.4.1.14519.5.2.1.6279.6001.179049373636438705059720603192'
        assert image_series.uri == uri

        auto_loaded_images = image_series.images.all()
        self.assertEqual(len(auto_loaded_images), 16)
        for img in auto_loaded_images:
            self.assertTrue(os.path.exists(img.path))

        image_series, created = ImageSeries.get_or_create(uri)
        assert not created
        assert image_series.patient_id == 'LIDC-IDRI-0001'
        assert image_series.series_instance_uid == '1.3.6.1.4.1.14519.5.2.1.6279.6001.179049373636438705059720603192'
        assert image_series.uri == uri

        # assert all the images are not recreated
        for old, new in zip(auto_loaded_images, image_series.images.all()):
            self.assertEqual(old.id, new.id)

    def test_create_image_file(self):
        uri = '/images/LIDC-IDRI-0001/' \
              '1.3.6.1.4.1.14519.5.2.1.6279.6001.298806137288633453246975630178/' \
              '1.3.6.1.4.1.14519.5.2.1.6279.6001.179049373636438705059720603192'

        # no warnings should be logged
        try:
            with self.assertLogs(level='WARN'):
                image_series, created = ImageSeries.get_or_create(uri)
        except AssertionError as e:
            self.assertEqual(str(e), "no logs of level WARNING or higher triggered on root")

        image = image_series.images.all()[0]

        expected_metdata = {
            'slice_thickness': 2.5,
            'slice_location': -132.5,
            'rescale_slope': 1,
            'rows': 512,
            'columns': 512,
            'pixel_spacing_col': 0.703125,
            'pixel_spacing_row': 0.703125,
            'path': os.path.join(uri, '-132.500000.dcm'),
        }

        for prop, expected in expected_metdata.items():
            self.assertEqual(getattr(image, prop), expected)

    def test_invalid_path_on_image_file_create(self):
        with self.assertRaises(PermissionDenied):
            ImageFile(path='/not_valid/path').save()

        with self.assertRaises(FileNotFoundError):
            ImageFile(path='/images/LIDC-IDRI-0001/not_valid/path').save()

    def test_non_existant_dicom_property(self):
        uri = '/images/LIDC-IDRI-0001/' \
              '1.3.6.1.4.1.14519.5.2.1.6279.6001.298806137288633453246975630178/' \
              '1.3.6.1.4.1.14519.5.2.1.6279.6001.179049373636438705059720603192'

        path = os.path.join(uri, '-132.500000.dcm')

        image_series, created = ImageSeries.get_or_create(uri)

        # Monkey patch
        ImageFile.DICOM_PROPERTIES.update({
            'RescaleSlope': lambda x: NotImplemented,
        })

        # expected behavior is to log a warning that parsing for this
        # property fails
        with self.assertLogs(level='WARN') as cm:
            ImageFile(path=path, series=image_series).save()

        # just one warning
        self.assertEqual(len(cm.output), 1)
        self.assertIn('RescaleSlope', cm.output[0])
        self.assertIn(path, cm.output[0])

        # reset for other tests
        ImageFile.DICOM_PROPERTIES.update({
            'RescaleSlope': lambda x: {'rescale_slope': int(x)},
        })

    def test_parsed_property_no_model_attribute(self):
        uri = '/images/LIDC-IDRI-0001/' \
              '1.3.6.1.4.1.14519.5.2.1.6279.6001.298806137288633453246975630178/' \
              '1.3.6.1.4.1.14519.5.2.1.6279.6001.179049373636438705059720603192'

        path = os.path.join(uri, '-132.500000.dcm')

        image_series, created = ImageSeries.get_or_create(uri)

        # CASE ONE, Dicom prop does not exist, attr is not field
        ImageFile.DICOM_PROPERTIES.update({
            'DoesNotExist1': 'no_attribute',
        })

        # expected behavior is to log a warning
        with self.assertLogs(level='WARN') as cm:
            ImageFile(path=path, series=image_series).save()

        self.assertEqual(len(cm.output), 1)
        self.assertIn("'no_attribute' not a field", cm.output[0])

        # reset
        ImageFile.DICOM_PROPERTIES.pop('DoesNotExist1')

        # CASE TWO, Dicom prop exists, attr is not field
        ImageFile.DICOM_PROPERTIES.update({
            'RescaleSlope': 'no_attribute2',
        })

        # expected behavior is to log a warning
        with self.assertLogs(level='WARN') as cm:
            ImageFile(path=path, series=image_series).save()

        self.assertEqual(len(cm.output), 1)
        self.assertIn("'no_attribute2' not a field", cm.output[0])

        ImageFile.DICOM_PROPERTIES.update({
            'RescaleSlope': lambda x: {'rescale_slope': int(x)},
        })

        # CASE THREE, Dicom prop does not exist, field does exist
        ImageFile.DICOM_PROPERTIES.pop('Rows')
        ImageFile.DICOM_PROPERTIES.update({
            'DoesNotExist2': 'rows',
        })

        # no warnings should be logged
        try:
            with self.assertLogs(level='WARN') as cm:
                img_file = ImageFile(path=path, series=image_series)
                img_file.save()
        except AssertionError as e:
            self.assertEqual(str(e), "no logs of level WARNING or higher triggered on root")

        self.assertIsNone(img_file.rows)

        # reset
        ImageFile.DICOM_PROPERTIES['Rows'] = 'rows'

        # CASE FOUR, Dicom prop does not exist, rows set multiple times
        ImageFile.DICOM_PROPERTIES.update({
            'DoesNotExist2': 'rows',
        })

        # expected behavior is to log a warning
        with self.assertLogs(level='WARN') as cm:
            ImageFile(path=path, series=image_series).save()

        self.assertEqual(len(cm.output), 1)
        self.assertIn("Tried to set 'rows' more than once", cm.output[0])

        ImageFile.DICOM_PROPERTIES.pop('DoesNotExist2')
