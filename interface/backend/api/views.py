import json
import mimetypes
import os

import dicom
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
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from ..cases import enum


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


class ImageMetadataApiView(APIView):
    def get(self, request):
        '''
        Get metadata of a DICOM image including the image in base64 format.
        Example: .../api/images/metadata?dicom_location=FULL_PATH_TO_IMAGE
        ---
        parameters:
            - name: dicom_location
            description: full location of the image
            required: true
            type: string
        '''
        path = request.GET['dicom_location']
        ds = dicom.read_file(path, force=True)
        return Response(serializers.DicomMetadataSerializer(ds).data)


class ImageAvailableApiView(APIView):
    """
    View list of images from dataset directory
    """

    def __init__(self, *args, **kwargs):
        super(ImageAvailableApiView, self).__init__(**kwargs)
        self.fss = FileSystemStorage(settings.DATASOURCE_DIR)

    @staticmethod
    def filename_to_dict(name, location):
        d = {
            'type': 'file',
            'mime_guess': mimetypes.guess_type(name)[0],
            'name': name,
            'path': os.path.join(location, name)
        }
        return d

    @staticmethod
    def is_hidden(location):
        """
        Check whether a file or a directory is hidden.
        """
        return os.path.basename(location).startswith('.')

    def walk(self, location, dir_name='/'):
        """
        Recursively walkthrough directories and files
        """
        folders, files = self.fss.listdir(location)
        tree = {
            'name': dir_name,
            'type': 'folder',
            'files': [self.filename_to_dict(filename, location)
                      for filename in sorted(files)
                      if not self.is_hidden(filename)],
            'children': [self.walk(os.path.join(location, dir), dir)
                         for dir in sorted(folders)
                         if not self.is_hidden(dir)]
        }
        return tree

    def get(self, request):
        """
        Return a sorted (by name) list of files and folders in dataset

        Format::

          {
            "directories": {
              "name": "/",
              "children": [
                {
                  "name": "LIDC-IDRI-0002",
                  "children": [
                    {
                      "name": "1.3.6.1.4.1.14519.5.2.1.6279.6001.490157381160200744295382098329",
                      "children": [
                        {
                          "name": "1.3.6.1.4.1.14519.5.2.1.6279.6001.619372068417051974713149104919",
                          "children": [],
                          "files": [
                            {
                              "type": "file",
                              "mime_guess": "application/dicom",
                              "name": "-80.750000.dcm",
                              "path": "/images/LIDC-IDRI-0002/1.3.[...snip...]3149104919/-80.750000.dcm"
                            },
                            {
                              "type": "file",
                              "mime_guess": "application/dicom",
                              "name": "-82.000000.dcm",
                              "path": "/images/LIDC-IDRI-0002/1.3.[...snip...]3149104919/-82.000000.dcm"
                            },
                            ...
                          ],
                          "type": "folder"
                        }
                      ],
                      "files": [],
                      "type": "folder"
                    }
                  ],
                  "files": [],
                  "type": "folder"
                }
              ],
              "files": [],
              "type": "folder"
            }
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


@api_view(['GET'])
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

    orientation_choices = [orientation.name for orientation in enum.LungOrientation]

    if lung_orientation not in orientation_choices:
        return Response({'response': "ValueError: lung_orientation must be one of {}".format(orientation_choices)}, 500)

    Nodule.objects.filter(pk=nodule_id).update(lung_orientation=enum.LungOrientation[lung_orientation].value)
    return Response(
        {'response': "Lung orientation of nodule {} has been changed to '{}'".format(nodule_id, lung_orientation)})
