from django.core.validators import (
    MaxValueValidator,
    MinValueValidator
)
from django.db import models
from django.utils import timezone


class Case(models.Model):
    """
    An analysis session on an image series.
    """
    created = models.DateTimeField(default=timezone.now)

    series = models.ForeignKey('images.ImageSeries', related_name='cases')


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
    Actual nodule, either confirmed as concerning from prediciton or manually added.
    """
    created = models.DateTimeField(default=timezone.now)

    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='nodules')

    candidate = models.OneToOneField(Candidate, on_delete=models.CASCADE, null=True)

    centroid = models.OneToOneField('images.ImageLocation', on_delete=models.CASCADE)
