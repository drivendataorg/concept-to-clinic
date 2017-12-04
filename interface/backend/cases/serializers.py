from rest_framework import serializers
from backend.images.serializers import (
    ImageSeriesSerializer, ImageLocationSerializer
)
from .models import (
    Candidate, Case
)


class CandidateSerializer(serializers.ModelSerializer):
    centroid = ImageLocationSerializer(read_only=True)

    class Meta:
        model = Candidate
        fields = ('id', 'created', 'centroid',
                  'case_id', 'probability_concerning')


class NoduleSerializer(serializers.ModelSerializer):
    candidates = CandidateSerializer(read_only=True, many=True)
    centroid = ImageLocationSerializer(read_only=True)

    class Meta:
        model = Case
        fields = ('id', 'created', 'candidates', 'centroid')


class CaseSerializer(serializers.ModelSerializer):
    series = ImageSeriesSerializer()
    candidates = CandidateSerializer(read_only=True, many=True)
    nodules = NoduleSerializer(read_only=True, many=True)

    class Meta:
        model = Case
        fields = ('id', 'created', 'series', 'candidates', 'nodules')
