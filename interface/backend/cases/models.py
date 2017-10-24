from enum import IntEnum, unique

from backend.images.models import ImageSeriesSerializer, ImageLocationSerializer
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator
)
from django.db import models
from django.utils import timezone
from rest_framework import serializers


def django_enum(cls):
    # decorator needed to enable enums in django templates
    cls.do_not_call_in_templates = True
    return cls


class PleuralSpace(models.Model):
    created = models.DateTimeField(default=timezone.now)

    @unique  # ensures all variables are unique
    @django_enum
    class TypesOne(IntEnum):
        NONE = 0
        SMALL = 1
        MODERATE = 2
        LARGE = 3

    @unique  # ensures all variables are unique
    @django_enum
    class TypesTwo(IntEnum):
        NONE = 0
        MILD = 1
        MODERATE = 2
        EXTENSIVE = 3

    effusion = models.IntegerField(
        choices=[(choice.value, choice.name.replace("_", " ")) for choice in TypesOne],
        default=TypesOne.NONE.value)

    calcification = models.IntegerField(
        choices=[(choice.value, choice.name.replace("_", " ")) for choice in TypesTwo],
        default=TypesTwo.NONE.value)

    thickening = models.IntegerField(
        choices=[(choice.value, choice.name.replace("_", " ")) for choice in TypesTwo],
        default=TypesTwo.NONE.value)

    pneumothorax = models.IntegerField(
        choices=[(choice.value, choice.name.replace("_", " ")) for choice in TypesOne],
        default=TypesOne.NONE.value)


class Case(models.Model):
    """
    An analysis session on an image series.
    """
    created = models.DateTimeField(default=timezone.now)

    series = models.ForeignKey('images.ImageSeries', related_name='cases')

    kVp = models.IntegerField(default=None)
    mA = models.IntegerField(default=None)
    DLP = models.IntegerField(default=None)

    SCREENING_VISIT_CHOICES = (
        ("BL", "Baseline"),
        ("Y1", "Year 1"),
        ("Y2", "Year 2")
    )

    screening_visit = models.CharField(max_length=2, choices=SCREENING_VISIT_CHOICES, default="BL")
    clinical_information = models.CharField(max_length=250, default="Lung cancer screening.")
    comparison = models.CharField(max_length=250, default="None.")

    DIAGNOSTIC_QUALITY_CHOICES = (
        ("SF", "Satisfactory"),
        ("LI", "Limited, but interpretable"),
        ("ND", "Non - diagnostic")
    )

    diagnostic_quality = models.CharField(max_length=2, choices=DIAGNOSTIC_QUALITY_CHOICES, default="SF")
    exam_parameters_comment = models.CharField(max_length=250, default="")

    @unique  # ensures all variables are unique
    @django_enum
    class ShapeChoices(IntEnum):
        NONE = 0
        MILD = 1
        MODERATE = 2
        SEVERE = 3

    @unique  # ensures all variables are unique
    @django_enum
    class HeartShapeChoices(IntEnum):
        NORMAL = 0
        MILDLY_ENLARGED = 1
        MODERATELY_ENLARGED = 2
        SEVERELY_ENLARGED = 3

    COPD = models.IntegerField(
        choices=[(choice.value, choice.name.replace("_", " ")) for choice in ShapeChoices],
        default=ShapeChoices.NONE.value)

    fibrosis = models.IntegerField(
        choices=[(choice.value, choice.name.replace("_", " ")) for choice in ShapeChoices],
        default=ShapeChoices.NONE.value)

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
        choices=[(choice.value, choice.name.replace("_", " ")) for choice in HeartShapeChoices],
        default=HeartShapeChoices.NORMAL.value)

    coronary_calcification = models.IntegerField(
        choices=[(choice.value, choice.name.replace("_", " ")) for choice in ShapeChoices],
        default=ShapeChoices.NONE.value)

    pericardial_effusion = models.IntegerField(
        choices=[(choice.value, choice.name.replace("_", " ")) for choice in ShapeChoices],
        default=ShapeChoices.NONE.value)

    upper_abdomen = models.CharField(max_length=250, default="None")
    thorax = models.CharField(max_length=250, default="None")
    base_of_neck = models.CharField(max_length=250, default="None")

    need_comparison = models.CharField(max_length=250, default="No")

    PERIODS = (
        ("T1", "12 months from screening exam"),
        ("T2", "3 months from screening exam"),
        ("T3", "6 months from screening exam"),
        ("T4", "3 to 6 months from screening exam"),
        ("T5", "24 months from screening exam")
    )

    repeat_CT = models.CharField(max_length=2, choices=PERIODS, default="T1")

    PHYSICIAN = (
        ("NO", "No."),
        ("YC", "Yes, Suspect cancer."),
        ("YM", "Yes, non - malignant finding.")
    )

    see_physician = models.CharField(max_length=2, choices=PHYSICIAN, default="NO")

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

    @unique  # ensures all variables are unique
    @django_enum
    class LungOrientation(IntEnum):
        NONE = 0
        LEFT = 1
        RIGHT = 2

    @unique  # ensures all variables are unique
    @django_enum
    class AppearanceFeature(IntEnum):
        NONE = 0
        UNCHANGED = 1
        INCREASED = 2
        DECREASED = 3
        NEW = 4

    @unique  # ensures all variables are unique
    @django_enum
    class DensityFeature(IntEnum):
        NONE = 0
        SOLID = 1
        SEMI_SOLID = 2
        GROUND_GLASS = 3

    created = models.DateTimeField(default=timezone.now)

    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='nodules')

    candidate = models.OneToOneField(Candidate, on_delete=models.CASCADE, null=True)

    centroid = models.OneToOneField('images.ImageLocation', on_delete=models.CASCADE)

    lung_orientation = models.IntegerField(
        choices=[(choice.value, choice.name.replace("_", " ")) for choice in LungOrientation],
        default=LungOrientation.NONE.value)

    diameter = models.DecimalField(max_digits=5, decimal_places=2, default=None)

    appearance_feature = models.IntegerField(
        choices=[(choice.value, choice.name.replace("_", " ")) for choice in AppearanceFeature],
        default=AppearanceFeature.NONE.value)

    density_feature = models.IntegerField(
        choices=[(choice.value, choice.name.replace("_", " ")) for choice in DensityFeature],
        default=DensityFeature.NONE.value)

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
