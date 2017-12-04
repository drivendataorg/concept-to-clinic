import json
import mimetypes
import os
import glob

import dicom
from backend.api import serializers
from backend.cases.serializers import CaseSerializer
from backend.cases.models import (
    Case,
    Candidate,
    Nodule
)

from backend.images.models import ImageSeries
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView


class ViewSetBase(viewsets.ModelViewSet):
    def get_serializer_context(self):
        context = super(ViewSetBase, self).get_serializer_context()

        # getting rid of absulute URLs
        context.update({'request': None})

        return context


class CaseViewSet(ViewSetBase):
    queryset = Case.objects.all()
    serializer_class = serializers.CaseSerializer


class CandidateViewSet(ViewSetBase):
    queryset = Candidate.objects.all()
    serializer_class = serializers.CandidateSerializer

    def partial_update(self, request, pk, *args, **kwargs):
        instance = get_object_or_404(Candidate, pk=pk)
        context = self.get_serializer_context()
        serializer = self.serializer_class(instance, data=request.data, partial=True, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(append_files_to_candidate(serializer.data))


class NoduleViewSet(ViewSetBase):
    queryset = Nodule.objects.all()
    serializer_class = serializers.NoduleSerializer

    def partial_update(self, request, pk, *args, **kwargs):
        instance = get_object_or_404(Nodule, pk=pk)
        context = self.get_serializer_context()
        serializer = self.serializer_class(instance, data=request.data, partial=True, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ImageSeriesViewSet(ViewSetBase):
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
        try:
            ds = dicom.read_file(path, force=True)
        except IOError as err:
            print(err)
            return Response(serializers.DicomMetadataSerializer().data)
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
def candidates_info(request):
    all_candidates = Candidate.objects.prefetch_related('case__series').all()
    serialized_candidates = serializers.CandidateSerializer(all_candidates, context={'request': None}, many=True).data

    # append DICOM files to response
    [append_files_to_candidate(candidate) for candidate in serialized_candidates]

    return Response(serialized_candidates)


@api_view(['POST'])
def update_candidate_location(request, candidate_id):
    try:
        request_body = json.loads(request.body)
        x = request_body['x']
        y = request_body['y']
        z = request_body['z']
    except Exception as e:
        return Response({'response': "An error occurred: {}".format(e)}, 500)

    # find the candidate and update the centroid location
    candidate = Candidate.objects.get(pk=candidate_id)
    candidate.centroid.x = x
    candidate.centroid.y = y
    candidate.centroid.z = z

    candidate.centroid.save()

    serialized_candidate = serializers.CandidateSerializer(candidate, context={'request': None}).data
    append_files_to_candidate(serialized_candidate)

    return Response(serialized_candidate)


@api_view(['GET'])
def case_report(request, pk, format=None):
    case = get_object_or_404(Case, pk=pk)
    return Response(CaseSerializer(case).data)


def append_files_to_candidate(candidate):
    series = candidate['case']['series']

    if 'files' not in series:
        # using `glob1` as it returns filenames without a directory path
        series['files'] = glob.glob1(series['uri'], '*.dcm')
