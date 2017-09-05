from backend.api import serializers
from backend.cases.models import (
    Case,
    Candidate,
    Nodule,
)
from backend.images.models import ImageSeries
from rest_framework import viewsets


class CaseViewSet(viewsets.ModelViewSet):
    queryset = Case.objects.all()
    serializer_class = serializers.CaseSerializer


class CandidateViewSet(viewsets.ModelViewSet):
    queryset = Candidate.objects.all()
    serializer_class = serializers.CandidateSerializer


class NoduleViewSet(viewsets.ModelViewSet):
    queryset = Nodule.objects.all()
    serializer_class = serializers.NoduleSerializer


class ImageSeriesViewSet(viewsets.ModelViewSet):
    queryset = ImageSeries.objects.all()
    serializer_class = serializers.ImageSeriesSerializer
