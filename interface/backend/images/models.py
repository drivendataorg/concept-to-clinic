import base64
import logging
import os

import dicom
import numpy as np

from django.conf import settings
from django.db import models
from django.core.exceptions import PermissionDenied
from django.utils._os import safe_join


class ImageFile(models.Model):
    """
    Model for an individual file for an image--that is, a single DICOM slice as
    it is represented on disk.
    """

    # Explicitly map all the dicom properties that we need to parse and their
    # model equivalents; create a lambda that returns a dict for any type conversions
    # or one-to-many relationships
    DICOM_PROPERTIES = {
        'SliceLocation': lambda x: {'slice_location': float(x)},
        'SliceThickness': lambda x: {'slice_thickness': float(x)},
        'RescaleSlope': lambda x: {'rescale_slope': int(x)},
        'Rows': 'rows',
        'Columns': 'columns',
        'PixelSpacing': lambda x: {'pixel_spacing_col': float(x[0]), 'pixel_spacing_row': float(x[1])},
    }

    series = models.ForeignKey('ImageSeries', related_name='images', on_delete=models.CASCADE)
    slice_location = models.FloatField(null=True)
    slice_thickness = models.FloatField(null=True)
    rescale_slope = models.IntegerField(null=True)
    rows = models.IntegerField(null=True)
    columns = models.IntegerField(null=True)
    pixel_spacing_col = models.FloatField(null=True)
    pixel_spacing_row = models.FloatField(null=True)
    path = models.FilePathField(path=settings.DATASOURCE_DIR,
                                recursive=True,
                                allow_files=True,
                                allow_folders=False,
                                max_length=512)

    class Meta:
        ordering = ('slice_location',)

    def save(self, *args, **kwargs):
        self._populate_dicom_properties()
        super().save(*args, **kwargs)

    def _populate_dicom_properties(self):
        """
        Parse DICOM properties from the file and store the relevant ones on the
        object.
        """

        logger = logging.getLogger(__name__)
        for k, v in self.load_dicom_data_from_disk(self.path)['metadata'].items():
            # check that the field is a property on the object
            if not hasattr(self.__class__, k):
                logger.warning(f"Property '{k}' not a field on ImageFile, discarding value '{v}'.")

            else:
                self.__setattr__(k, v)

    @classmethod
    def load_dicom_data_from_disk(cls, filepath, parse_metadata=True, encode_image_data=False):
        """
        Loads the dicom properties that we care about from disk.

        For the values we load, see ImageFile.DICOM_PROPERTIES

        Args:
            filepath (str): the path to the file (so this can be used if ImageFile is not in database yet)
            parse_metadata (bool, optional): weather or not to parse any metadata from the file (skip for just img)
            encode_image_data (bool, optional): Base64 encode image data and return it.
        """
        if not os.path.abspath(filepath).startswith(settings.DATASOURCE_DIR):
            raise PermissionDenied

        dcm_data = dicom.read_file(filepath)

        # parse metadata
        metadata = cls._parse_metadata(dcm_data, filepath) if parse_metadata else dict()

        # encode image data as base64 if asked for it
        image = cls._dicom_to_base64(dcm_data) if encode_image_data else None

        return dict(metadata=metadata, image=image)

    @classmethod
    def _parse_metadata(cls, dcm_data, filepath):
        """
        Parses metadata from dicom file and creates a dictionary which we can
        use to populate the ImageFile object
        """
        logger = logging.getLogger(__name__)

        # only allow a key to be read from a single DICOM property
        # and warn on attempted overwrite
        def _update_once(d1, d2):
            for k, v in d2.items():
                if k in d1:
                    logger.warning(f"Tried to set '{k}' more than once, ignoring value '{v}'.")
                else:
                    d1[k] = v

        metadata = dict()
        for dicom_prop, model_attribute in cls.DICOM_PROPERTIES.items():
            if callable(model_attribute):
                try:
                    processed_values = model_attribute(dcm_data.get(dicom_prop, None))
                    _update_once(metadata, processed_values)
                except:  # noqa
                    # bare except is normally unforgivable but we _really_ don't care what went wrong here --
                    # we will surface the error message and move on
                    logger.warning(f"Property '{dicom_prop}' failed to parse for file '{filepath}'.")
            else:
                _update_once(metadata, {model_attribute: dcm_data.get(dicom_prop, None)})

        return metadata

    def get_image_data(self):
        """
        Shortcut for just the encoded image from
        `load_dicom_properties_from_disk`.
        """
        return self.load_dicom_data_from_disk(self.path, parse_metadata=False, encode_image_data=True)['image']

    @staticmethod
    def _pixel_data2str(buf):
        _min, _max = buf.min(), buf.max()
        buf = 254 * (np.array(buf, dtype=np.float) - _min) / (_max - _min) + 1
        return buf.astype(np.uint16)

    @classmethod
    def _dicom_to_base64(cls, ds):
        """
        Returning base64 encoded string for a dicom image
        """
        rescaled = cls._pixel_data2str(ds.pixel_array)
        return base64.b64encode(rescaled.tobytes())


class ImageSeries(models.Model):
    """
    Model representing a certain image series
    """
    patient_id = models.CharField(max_length=64)
    series_instance_uid = models.CharField(max_length=256)
    uri = models.CharField(max_length=512)

    @classmethod
    def get_or_create(cls, uri):
        """
        Return the ImageSeries instance with the same PatientID and
        SeriesInstanceUID as the DICOM images in the given directory. If none
        exists so far, create one.

        Returns a tuple of (ImageSeries, created), where created is a boolean
        specifying whether the object was created.

        Args:
            uri (str): absolute URI to a directory with DICOM images of a
                       patient

        Returns:
            (ImageSeries, bool): the looked up ImageSeries instance and whether
                                 it had to be created
        """
        # get all the images in the folder that are valid dicom extensions
        files = [f for f in os.listdir(uri)
                 if os.path.splitext(f)[-1] in settings.IMAGE_EXTENSIONS]

        # load series-level metadata from the first dicom file
        plan = dicom.read_file(safe_join(uri, files[0]))

        patient_id = plan.PatientID
        series_instance_uid = plan.SeriesInstanceUID

        series, created = ImageSeries.objects.get_or_create(patient_id=patient_id,
                                                            series_instance_uid=series_instance_uid,
                                                            uri=uri)

        # create models that point to each of the individual image files
        for f in files:
            image, _ = ImageFile.objects.get_or_create(path=safe_join(uri, f), series=series)

        return series, created

    def __str__(self):
        return f"{self.patient_id}"


class ImageLocation(models.Model):
    """
    Model representing a certain voxel location on certain image.
    """

    x = models.PositiveSmallIntegerField(help_text='Voxel index for X axis, zero-index, from top left')
    y = models.PositiveSmallIntegerField(help_text='Voxel index for Y axis, zero-index, from top left')
    z = models.PositiveSmallIntegerField(help_text='Slice index for Z axis, zero-index')
