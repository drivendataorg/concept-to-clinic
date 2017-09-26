import json
import mimetypes
import os

from backend.api import serializers
from backend.cases.models import (
    Case,
    Candidate,
    Nodule,
    CaseSerializer
)
from backend.images.models import ImageSeries
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import get_object_or_404
from rest_framework import renderers
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.decorators import renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
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

    def __init__(self, *args, **kwargs):
        super(ImageAvailableApiView, self).__init__(**kwargs)
        self.fss = FileSystemStorage(settings.DATASOURCE_DIR)

    @staticmethod
    def filename_to_dict(name, location):
        d = {'type': 'file', 'mime_guess': mimetypes.guess_type(name)[0], 'name': name}
        d['path'] = os.path.join(location, name)
        return d

    def walk(self, location, dir_name='/'):
        """
        Recursively walkthrough directories and files
        """
        folders, files = self.fss.listdir(location)
        tree = {'name': dir_name, 'children': []}
        tree['files'] = [self.filename_to_dict(filename, location) for filename in sorted(files)]
        tree['type'] = 'folder'
        tree['children'] = [self.walk(os.path.join(location, dir), dir) for dir in folders]
        return tree

    def get(self, request):
        """
        Return a sorted(by name) list of files and folders
        in dataset

        Format::

            {'directories': [
                {
                    'name': directory_name1,
                    'children': [
                        file_name1,
                        file_name2,
                        {
                            'name': 'nested_dir_1',
                            'children': [
                                'file_name_1',
                                'file_name_2',
                                ....
                            ]
                        }
                        ... ]
                }, ... ]
            }
        """
        tree = self.walk(settings.DATASOURCE_DIR)
        return Response({'directories': tree})


@api_view(['GET'])
def candidate_mark(request, candidate_id):
    return Response({'response': "Candidate {} was marked".format(candidate_id)})


@api_view(['GET'])
def candidate_dismiss(request, candidate_id):
    return Response({'response': "Candidate {} was dismissed".format(candidate_id)})


class JsonHtmlRenderer(renderers.BaseRenderer):
    media_type = 'text/html'
    format = 'html'

    def render(self, data, media_type=None, renderer_context=None):
        return "<pre>{}</pre>".format(json.dumps(data, indent=4, sort_keys=True, cls=DjangoJSONEncoder))


@api_view(['GET'])
# Render .json and .html requests
@renderer_classes((JSONRenderer, JsonHtmlRenderer))
def case_report(request, case_id, format=None):
    case = get_object_or_404(Case, pk=case_id)

    return Response(CaseSerializer(case).data)


@api_view(['POST'])
def nodule_update(request, nodule_id):
    try:
        lung_orientation = json.loads(request.body)['lung_orientation']
    except Exception as e:
        return Response({'response': "An error occurred: {}".format(e)}, 500)

    if lung_orientation is None:
        lung_orientation = 'NONE'

    orientation_choices = [orientation.name for orientation in Nodule.LungOrientation]

    if lung_orientation not in orientation_choices:
        return Response({'response': "ValueError: lung_orientation must be one of {}".format(orientation_choices)}, 500)

    Nodule.objects.filter(pk=nodule_id).update(lung_orientation=Nodule.LungOrientation[lung_orientation].value)
    return Response(
        {'response': "Lung orientation of nodule {} has been changed to '{}'".format(nodule_id, lung_orientation)})
