import dicom
import base64
from PIL import Image
import numpy as np
from io import BytesIO
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

    def create(self, validated_data):
        return Case.objects.create(
            series=ImageSeries.objects.create(**validated_data['series']), **validated_data
        )


class CandidateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Candidate
        fields = '__all__'
        read_only_fields = ('created',)

    centroid = ImageLocationSerializer()
    case = CaseSerializer()

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


class DicomMetadataSerializer(serializers.BaseSerializer):
    """
    Serialize a Dicom image metadata including a base64 version of the
    image in following format:
    {
        metadata: {
            "Specific Character Set": "ISO_IR 100",
            "Image Type": [
                "ORIGINAL",
                "SECONDARY",
                "AXIAL"
            ],
            "SOP Class UID": "1.2.840.10008.5.1.4.1.1.2",
            ......
        },
        image: "data:image/jpg;base64,/9j/4AAQSkZJRgABAQ.....fnkw3n"
    }
    """

    def to_representation(self, obj):
        """
        Put dicom metadata into a separate dictionary
        """
        dicom_dict = {}
        repr(obj)   # Bit hacky! But does the work to populate the elements
        for dicom_value in obj.values():
            if dicom_value.tag == (0x7fe0, 0x0010):
                # discard pixel data
                continue
            if isinstance(dicom_value.value, dicom.dataset.Dataset):
                dicom_dict[dicom_value.name] = self.dicom_dataset_to_dict(dicom_value.value)
            else:
                dicom_dict[dicom_value.name] = self._convert_value(dicom_value.value)
        return {
            'metadata': dicom_dict,
            'image': self.dicom_to_base64(obj),
        }

    def dicom_to_base64_depricated(self, ds):
        """
        Returning base64 encoded string for a dicom image
        """
        buff_output = BytesIO()
        img = Image.fromarray((ds.pixel_array)).convert('RGB')
        img.save(buff_output, format='jpeg')
        preamble = 'data:image/jpg;base64,'
        base64_encoded = base64.b64encode(buff_output.getvalue()).decode()
        return preamble + base64_encoded

    def pixel_data2str(self, buf):
        _min, _max = buf.min(), buf.max()
        buf = 254 * (np.array(buf, dtype=np.float) - _min) / (_max - _min) + 1
        return buf.astype(np.uint16)

    def dicom_to_base64(self, ds):
        """
        Returning base64 encoded string for a dicom image
        """
        rescaled = self.pixel_data2str(ds.pixel_array)
        return base64.b64encode(rescaled.tobytes())

    def _sanitise_unicode(self, s):
        return s.replace(u"\u0000", "").strip()

    def _convert_value(self, v):
        if isinstance(v, (list, int, float)):
            converted_val = v
        elif isinstance(v, str):
            converted_val = self._sanitise_unicode(v)
        elif isinstance(v, bytes):
            converted_val = self._sanitise_unicode(v.decode('ascii', 'replace'))
        elif isinstance(v, dicom.valuerep.DSfloat):
            converted_val = float(v)
        elif isinstance(v, dicom.valuerep.IS):
            converted_val = int(v)
        elif isinstance(v, dicom.valuerep.PersonName3):
            converted_val = str(v)
        else:
            converted_val = repr(v)
        return converted_val
