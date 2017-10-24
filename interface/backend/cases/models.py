from backend.images.models import ImageSeriesSerializer, ImageLocationSerializer
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator
)
from django.db import models
from django.utils import timezone
from rest_framework import serializers

from . import enum


class PleuralSpace(models.Model):
    created = models.DateTimeField(default=timezone.now)

    effusion = models.IntegerField(
        choices=enum.format_enum(enum.TypesOne),
        default=enum.TypesOne.NONE.value)

    calcification = models.IntegerField(
        choices=enum.format_enum(enum.TypesTwo),
        default=enum.TypesTwo.NONE.value)

    thickening = models.IntegerField(
        choices=enum.format_enum(enum.TypesTwo),
        default=enum.TypesTwo.NONE.value)

    pneumothorax = models.IntegerField(
        choices=enum.format_enum(enum.TypesOne),
        default=enum.TypesOne.NONE.value)


class Case(models.Model):
    """
    An analysis session on an image series.
    """
    created = models.DateTimeField(default=timezone.now)

    series = models.ForeignKey('images.ImageSeries', related_name='cases')

    kVp = models.IntegerField(default=None)
    mA = models.IntegerField(default=None)
    DLP = models.IntegerField(default=None)

    screening_visit = models.CharField(max_length=2, choices=enum.SCREENING_VISIT_CHOICES, default="BL")
    clinical_information = models.CharField(max_length=250, default="Lung cancer screening.")
    comparison = models.CharField(max_length=250, default="None.")

    diagnostic_quality = models.CharField(max_length=2, choices=enum.DIAGNOSTIC_QUALITY_CHOICES, default="SF")
    exam_parameters_comment = models.CharField(max_length=250, default="")

    COPD = models.IntegerField(
        choices=enum.format_enum(enum.ShapeChoices),
        default=enum.ShapeChoices.NONE.value)

    fibrosis = models.IntegerField(
        choices=enum.format_enum(enum.ShapeChoices),
        default=enum.ShapeChoices.NONE.value)

    lymph_nodes = models.CharField(max_length=250, default="None.")

    other_findings = models.CharField(max_length=250, default="None.")

    left_pleural_space = models.ForeignKey(PleuralSpace,
                                           on_delete=models.CASCADE,
                                           related_name="left_pleural_space",
                                           null=True)
    right_pleural_space = models.ForeignKey(PleuralSpace,
                                            on_delete=models.CASCADE,
                                            related_name="right_pleural_space",
                                            null=True)

    heart_size = models.IntegerField(
        choices=enum.format_enum(enum.HeartShapeChoices),
        default=enum.HeartShapeChoices.NORMAL.value)

    coronary_calcification = models.IntegerField(
        choices=enum.format_enum(enum.ShapeChoices),
        default=enum.ShapeChoices.NONE.value)

    pericardial_effusion = models.IntegerField(
        choices=enum.format_enum(enum.ShapeChoices),
        default=enum.ShapeChoices.NONE.value)

    upper_abdomen = models.CharField(max_length=250, default="None")
    thorax = models.CharField(max_length=250, default="None")
    base_of_neck = models.CharField(max_length=250, default="None")

    need_comparison = models.CharField(max_length=250, default="No")

    repeat_CT = models.CharField(max_length=2, choices=enum.PERIODS, default="T1")
    see_physician = models.CharField(max_length=2, choices=enum.PHYSICIAN, default="NO")

    impression_comment = models.CharField(max_length=250, default="")


class Candidate(models.Model):
    """
    Predicted location of a possible nodule.
    """
    created = models.DateTimeField(default=timezone.now)

    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='candidates')

    centroid = models.OneToOneField('images.ImageLocation', on_delete=models.CASCADE)

    probability_concerning = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])


class Nodule(models.Model):
    """
    Actual nodule, either confirmed as concerning from prediction or manually added.
    """

    created = models.DateTimeField(default=timezone.now)

    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='nodules')

    candidate = models.OneToOneField(Candidate, on_delete=models.CASCADE, null=True)

    centroid = models.OneToOneField('images.ImageLocation', on_delete=models.CASCADE)

    lung_orientation = models.IntegerField(
        choices=enum.format_enum(enum.LungOrientation),
        default=enum.LungOrientation.NONE.value)

    diameter = models.DecimalField(max_digits=5, decimal_places=2, default=None)

    appearance_feature = models.IntegerField(
        choices=enum.format_enum(enum.AppearanceFeature),
        default=enum.AppearanceFeature.NONE.value)

    density_feature = models.IntegerField(
        choices=enum.format_enum(enum.DensityFeature),
        default=enum.DensityFeature.NONE.value)

    image_no = models.PositiveIntegerField(default=None)


class CandidateSerializer(serializers.ModelSerializer):
    centroid = ImageLocationSerializer(read_only=True)

    class Meta:
        model = Candidate
        fields = ('id', 'created', 'centroid', 'case_id', 'probability_concerning')


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
