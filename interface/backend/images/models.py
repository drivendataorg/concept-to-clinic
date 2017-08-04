from django.db import models


class ImageSeries(models.Model):
    """
    Model representing a certain image series
    """
    patient_id = models.CharField(max_length=64)

    series_instance_uid = models.CharField(max_length=256)

    uri = models.CharField(max_length=512)


class ImageLocation(models.Model):
    """
    Model representing a certain voxel location on certain image
    """
    series = models.ForeignKey(ImageSeries, on_delete=models.CASCADE)

    x = models.PositiveSmallIntegerField(help_text='Voxel index for X axis, zero-index, from top left')

    y = models.PositiveSmallIntegerField(help_text='Voxel index for Y axis, zero-index, from top left')

    z = models.PositiveSmallIntegerField(help_text='Slice index for Z axis, zero-index')
