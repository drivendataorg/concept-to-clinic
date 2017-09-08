from backend.api import serializers
from backend.cases.models import (
    Case,
    Candidate,
    Nodule,
)
from backend.images.models import ImageSeries
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.views import APIView


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


class ImageAvailableApiView(APIView):
    """
    View list of images from dataset directory
    """

    def get(self, request):
        """
        Return a list of files and folders in dataset in the form
        {'directories': [
            {
                'name': directory_name1,
                'children': [ file_name1, file_name2, ... ]
            }, ... ]
        }

        """
        return JsonResponse({'directories': []})


def candidate_mark(request, candidate_id):
    return JsonResponse({'response': "Candidate {} was marked".format(candidate_id)})


def candidate_dismiss(request, candidate_id):
    return JsonResponse({'response': "Candidate {} was dismissed".format(candidate_id)})
