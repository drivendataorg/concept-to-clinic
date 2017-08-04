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

    case = factory.SubFactory(CaseFactory)

    candidate = factory.SubFactory(
        CandidateFactory,
        case=factory.SelfAttribute('..case'),
    )

    centroid = factory.SubFactory(
        ImageLocationFactory,
        x=factory.SelfAttribute('..candidate.centroid.x'),
        y=factory.SelfAttribute('..candidate.centroid.y'),
        z=factory.SelfAttribute('..candidate.centroid.z')
    )

    # centroid = factory.SubFactory(
    #     ImageLocationFactory,
    #     series=factory.LazyAttribute(lambda o: o.factory_parent.candidate.centroid.series),
    #     x=factory.LazyAttribute(lambda o: o.factory_parent.candidate.centroid.x),
    #     y=factory.LazyAttribute(lambda o: o.factory_parent.candidate.centroid.y),
    #     z=factory.LazyAttribute(lambda o: o.factory_parent.candidate.centroid.z),
    # )

