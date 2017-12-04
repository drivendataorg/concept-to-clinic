from rest_framework import serializers
from .models import (
    ImageSeries, ImageLocation
)


class ImageSeriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageSeries
        fields = ('id', 'patient_id', 'series_instance_uid', 'uri')


class ImageLocationSerializer(serializers.ModelSerializer):
    series = ImageSeriesSerializer()

    class Meta:
        model = ImageLocation
        fields = ('id', 'series', 'x', 'y', 'z')
