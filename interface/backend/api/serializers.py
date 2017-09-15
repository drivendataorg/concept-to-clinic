from backend.cases.models import (
    Case,
    Candidate,
    Nodule,
)
from backend.images.models import (
    ImageSeries,
    ImageLocation
)
from rest_framework import serializers


class ImageSeriesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ImageSeries
        fields = '__all__'


class ImageLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageLocation
        fields = '__all__'


class CaseSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Case
        fields = '__all__'
        read_only_fields = ('created',)

    series = ImageSeriesSerializer()


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


class NoduleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Nodule
        fields = '__all__'
        read_only_fields = ('created',)

    centroid = ImageLocationSerializer()

    def create(self, validated_data):
        return Nodule.objects.create(
            case=validated_data['case'],
            candidate=validated_data['candidate'],
            centroid=ImageLocation.objects.create(**validated_data['centroid']),
        )
