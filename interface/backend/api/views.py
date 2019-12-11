import mimetypes
import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.shortcuts import get_object_or_404
from django.utils._os import safe_join

from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.api import serializers
from backend.cases.models import (
    Case,
    Candidate,
    Nodule,
)

from backend.images.models import (
    ImageSeries,
    ImageFile,
)


class ViewSetBase(viewsets.ModelViewSet):
    def get_serializer_context(self):
        context = super(ViewSetBase, self).get_serializer_context()

        # by default absolute URLs are constructed with the request; since
        # we proxy requests, we want relative URLs so we remove the request
        context.update({'request': None})

        return context


class CaseViewSet(ViewSetBase):
    queryset = Case.objects.all()
    serializer_class = serializers.CaseSerializer

    def create(self, request):
        # construct full path to file
        series_uri = request.data['uri'].strip('/')
        full_uri = safe_join(settings.DATASOURCE_DIR, series_uri)

        # get case if this uri and image series ex
        series, _ = ImageSeries.get_or_create(full_uri)
        new_case = Case.objects.create(series=series)
        serialized = self.serializer_class(new_case, context={'request': None}).data
        return Response(serialized)


class CandidateViewSet(ViewSetBase):
    queryset = Candidate.objects.all()
    serializer_class = serializers.CandidateSerializer

    def partial_update(self, request, pk, *args, **kwargs):
        instance = get_object_or_404(Candidate, pk=pk)
        context = self.get_serializer_context()
        serializer = self.serializer_class(instance, data=request.data, partial=True, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


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


class ImagePreviewApiView(APIView):
    def get(self, request):
        '''
        Get metadata of a DICOM image that is not yet imported into the database. This can
        be used to preview the DICOM images before creating the model (e.g., during selection).
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
            return Response(ImageFile.load_dicom_data_from_disk(path, encode_image_data=True))
        except IOError:
            raise NotFound(f"DICOM file not found on disk with path '{path}'")


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
def case_report(request, pk, format=None):
    case = get_object_or_404(Case, pk=pk)
    return Response(serializers.CaseSerializer(case, context={'request': None}).data)
