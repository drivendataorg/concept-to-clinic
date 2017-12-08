import factory
import factory.fuzzy
from backend.cases import models
from backend.images.factories import (
    ImageLocationFactory,
    ImageSeriesFactory
)


class CaseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Case

    series = factory.SubFactory(ImageSeriesFactory)


class CandidateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Candidate

    case = factory.SubFactory(CaseFactory)
    centroid = factory.SubFactory(ImageLocationFactory)
    probability_concerning = factory.fuzzy.FuzzyFloat(0.01, 0.99)


class NoduleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Nodule

    candidate = factory.SubFactory(CandidateFactory)
