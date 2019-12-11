import factory
import factory.fuzzy
from backend.images import models


class ImageSeriesFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ImageSeries

    patient_id = factory.Sequence(lambda n: "TEST-SERIES-{:04d}".format(n))

    series_instance_uid = factory.Sequence(lambda n: "1.3.6.1.4.1.14519.5.2.1.6279.6001.{:030d}".format(n))

    uri = factory.LazyAttribute(lambda f: 'file:///tmp/{}/'.format(f.series_instance_uid))


class ImageLocationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ImageLocation

    x = factory.fuzzy.FuzzyInteger(0, 256)

    y = factory.fuzzy.FuzzyInteger(0, 256)

    z = factory.fuzzy.FuzzyInteger(0, 16)
