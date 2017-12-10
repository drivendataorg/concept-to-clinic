from django.urls import reverse
from rest_framework import serializers

from backend.cases.models import (
    Case,
    Candidate,
    Nodule,
)
from backend.images.models import (
    ImageFile,
    ImageSeries,
    ImageLocation,
)


class ImageFileSerializer(serializers.ModelSerializer):
    """ Serializes an ImageFile model object.

        In addition to the properties on the object, it returns a `preview_url` which
        will return the dicom image data encoded in base64.
    """
    class Meta:
        model = ImageFile
        fields = '__all__'

    preview_url = serializers.SerializerMethodField()

    def get_preview_url(self, instance):
        return f"{reverse('images-preview')}?dicom_location={instance.path}"


class ImageSeriesSerializer(serializers.HyperlinkedModelSerializer):
    """ Serializes an ImageSeries model object.

        Will also contain an `images` property with all of the serialized
        image files in this series.
    """
    class Meta:
        model = ImageSeries
        fields = '__all__'

    images = ImageFileSerializer(many=True, read_only=True)

    def create(self, validated_data):
        series, _ = ImageSeries.get_or_create(validated_data['uri'])
        return series


class ImageLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageLocation
        fields = ('x', 'y', 'z')


class CandidateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Candidate
        fields = '__all__'
        read_only_fields = ('created',)

    centroid = ImageLocationSerializer()

    def create(self, validated_data):
        case_data = validated_data.pop('case')
        centroid_data = validated_data.pop('centroid')
        image_location = ImageLocation.objects.create(**centroid_data)
        candidate = Candidate.objects.create(case=case_data, centroid=image_location, **validated_data)
        return candidate

    def update(self, instance, validated_data):
        centroid_data = validated_data.pop('centroid', None)
        if centroid_data is not None:
            instance.centroid.x = centroid_data.get('x', instance.centroid.x)
            instance.centroid.y = centroid_data.get('y', instance.centroid.y)
            instance.centroid.z = centroid_data.get('z', instance.centroid.z)
            instance.centroid.save()
        return super().update(instance, validated_data)


class NoduleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Nodule
        fields = '__all__'
        read_only_fields = ('created',)

    centroid = ImageLocationSerializer(source='candidate.centroid', read_only=True)

    def create(self, validated_data):
        return Nodule.objects.get_or_create(candidate=validated_data['candidate'])


class CaseSerializer(serializers.HyperlinkedModelSerializer):
    """ Serializes a Case model object

        Case is the top level of the object hierarchy, and it contains
        the image series, candidates, and nodules for the currently active
        case.
    """
    class Meta:
        model = Case
        fields = '__all__'
        read_only_fields = ('created',)

    series = ImageSeriesSerializer()
    candidates = CandidateSerializer(many=True, read_only=True)
    nodules = NoduleSerializer(many=True, read_only=True)

    def create(self, validated_data):
        series = ImageSeriesSerializer.create(**validated_data['series'])
        return Case.objects.create(series=series, **validated_data)
