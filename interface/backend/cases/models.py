from backend.images.models import ImageSeriesSerializer, ImageLocationSerializer
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator
)
from django.db import models
from django.utils import timezone
from rest_framework import serializers

from . import enums


class Case(models.Model):
    """
    An analysis session on an image series.
    """
    created = models.DateTimeField(default=timezone.now)
    series = models.ForeignKey('images.ImageSeries', related_name='cases')


class PleuralSpace(models.Model):
    """
    Contains the info about the degrees of diseases progress
    """
    effusion = models.IntegerField(choices=enums.format_enum(enums.PleuralSpaceChoicesOne),
                                   help_text="Describes the degree of effusion progress")

    calcification = models.IntegerField(choices=enums.format_enum(enums.PleuralSpaceChoicesTwo),
                                        help_text="Describes the degree of Calcification progress")

    thickening = models.IntegerField(choices=enums.format_enum(enums.PleuralSpaceChoicesTwo),
                                     help_text="Describes the degree of Thickening progress")

    pneumothorax = models.IntegerField(choices=enums.format_enum(enums.PleuralSpaceChoicesOne),
                                       help_text="Describes the degree of Pneumothorax progress")


class CasePleuralSpaces(models.Model):
    """
    Contains left and right pleural spaces.
    """
    case = models.OneToOneField(Case, related_name='%(class)s_case', primary_key=True)

    left_pleural_space = models.ForeignKey(PleuralSpace,
                                           on_delete=models.CASCADE,
                                           related_name="left_pleural_space",
                                           null=True)
    right_pleural_space = models.ForeignKey(PleuralSpace,
                                            on_delete=models.CASCADE,
                                            related_name="right_pleural_space",
                                            null=True)


class TechnicalParameters(models.Model):
    """
    Contains configuration of CT scanner.
    """
    case = models.OneToOneField(Case, related_name='%(class)s_case', primary_key=True)

    kVp = models.IntegerField(help_text="Peak kilovoltage, maximum voltage applied across an X-ray tube")
    mA = models.IntegerField(help_text="Milli amper")
    DLP = models.IntegerField(help_text="Dose-length product")


class ClinicalInformation(models.Model):
    """
    Contains patient's information.
    """
    case = models.OneToOneField(Case, related_name='%(class)s_case', primary_key=True)

    screening_visit = models.CharField(max_length=2, choices=enums.SCREENING_VISIT_CHOICES)
    clinical_information = models.CharField(max_length=250)


class CaseComparison(models.Model):
    """
    Contains the information of comparison.
    """
    case = models.OneToOneField(Case, related_name='%(class)s_case', primary_key=True)

    comparison = models.CharField(max_length=250, help_text="Comparison with previous screening")


class ExamParameters(models.Model):
    """
    Contains information of the diagnostic quality.
    """
    case = models.OneToOneField(Case, related_name='%(class)s_case', primary_key=True)

    diagnostic_quality = models.CharField(max_length=2, choices=enums.DIAGNOSTIC_QUALITY_CHOICES)
    exam_parameters_comment = models.CharField(max_length=250, help_text="Comment on the quality of diagnostic")


class LungsFindings(models.Model):
    """
    Contains the information about findings in lungs.
    """
    case = models.OneToOneField(Case, related_name='%(class)s_case', primary_key=True)

    COPD = models.IntegerField(choices=enums.format_enum(enums.ShapeChoices),
                               help_text="Term used to describe progressive lung diseases. "
                                         "Describes the degree of copd progress")
    fibrosis = models.IntegerField(choices=enums.format_enum(enums.ShapeChoices),
                                   help_text="Describes the degree of fibrosis progress")

    lymph_nodes = models.CharField(max_length=250, help_text="Description of the lymph nodes")
    other_findings = models.CharField(max_length=250, help_text="Description of other findings")


class HeartFindings(models.Model):
    """
    Contains the information about findings in heart.
    """
    case = models.OneToOneField(Case, related_name='%(class)s_case', primary_key=True)

    heart_size = models.IntegerField(choices=enums.format_enum(enums.HeartShapeChoices))

    coronary_calcification = models.IntegerField(choices=enums.format_enum(enums.ShapeChoices),
                                                 help_text="Describes the degree of Coronary calcification")

    pericardial_effusion = models.IntegerField(choices=enums.format_enum(enums.ShapeChoices),
                                               help_text="Describes the degree of Pericardial effusion")


class OtherFindings(models.Model):
    """
    Contains the information about additional or unrelated findings.
    """
    case = models.OneToOneField(Case, related_name='%(class)s_case', primary_key=True)

    upper_abdomen = models.CharField(max_length=250, help_text="describes other findings in upper abdomen")
    thorax = models.CharField(max_length=250, help_text="describes other findings in thorax")
    base_of_neck = models.CharField(max_length=250, help_text="describes other findings in the Base of neck")


class ExtraInformation(models.Model):
    """
    Additional information.
    """
    case = models.OneToOneField(Case, related_name='%(class)s_case', primary_key=True)

    need_comparison = models.CharField(max_length=250, help_text="Shows if comparison is needed")

    repeat_CT = models.CharField(max_length=2, choices=enums.PERIODS, help_text="The date of next ct")
    see_physician = models.CharField(max_length=2, choices=enums.PHYSICIAN,
                                     help_text="Shows if the patient should visit physician")

    impression_comment = models.CharField(max_length=250, default="")


class Candidate(models.Model):
    """
    Predicted location of a possible nodule.
    """
    created = models.DateTimeField(default=timezone.now)

    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='candidates')

    centroid = models.OneToOneField('images.ImageLocation', on_delete=models.CASCADE)

    probability_concerning = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])

    # defines whether the nodule was marked for further analysis or not(feedback given by user)
    review_result = models.IntegerField(choices=enums.format_enum(enums.CandidateReviewResult),
                                        default=enums.CandidateReviewResult.NONE)


class Nodule(models.Model):
    """
    Actual nodule, either confirmed as concerning from prediction or manually added.
    """

    created = models.DateTimeField(default=timezone.now)

    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='nodules')

    candidate = models.OneToOneField(Candidate, on_delete=models.CASCADE, null=True)

    centroid = models.OneToOneField('images.ImageLocation', on_delete=models.CASCADE)

    lung_orientation = models.IntegerField(choices=enums.format_enum(enums.LungOrientation),
                                           default=enums.LungOrientation.NONE)


class NoduleFeatures(models.Model):
    """
    Contains additional descriptive features of the nodule.
    """
    case = models.OneToOneField(Case, related_name='%(class)s_case', primary_key=True)

    appearance_feature = models.IntegerField(choices=enums.format_enum(enums.AppearanceFeature))
    diameter = models.DecimalField(max_digits=5, decimal_places=2)
    density_feature = models.IntegerField(choices=enums.format_enum(enums.DensityFeature))


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
