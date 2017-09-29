import numpy as np
import pytest

from ..algorithms.identify import trained_model
from ..tests.test_endpoints import skip_slow_test


@pytest.fixture
def dicom_path_001():
    yield '../images/LIDC-IDRI-0001/1.3.6.1.4.1.14519.5.2.1.6279.6001.298806137288633453246975630178/' \
          '1.3.6.1.4.1.14519.5.2.1.6279.6001.179049373636438705059720603192'


@pytest.fixture
def dicom_path_003():
    yield "/images/LIDC-IDRI-0003/1.3.6.1.4.1.14519.5.2.1.6279.6001.101370605276577556143013894866/" \
          "1.3.6.1.4.1.14519.5.2.1.6279.6001.170706757615202213033480003264"


@pytest.fixture
def nodule_locations_001():
    yield {"x": 317, "y": 367, "z": 7}


@pytest.fixture
def nodule_locations_003():
    yield {"x": 369, "y": 347, "z": 6}


@pytest.mark.skipif(skip_slow_test, reason='Takes very long')
def test_identify_nodules_001(dicom_path_001, nodule_locations_001):
    predicted = trained_model.predict(dicom_path_001)

    first = predicted[0]

    dist = np.sqrt(np.sum([(first[s] - nodule_locations_001[s]) ** 2 for s in ["x", "y", "z"]]))

    assert (dist < 10)


@pytest.mark.skipif(skip_slow_test, reason='Takes very long')
def test_identify_nodules_003(dicom_path_003, nodule_locations_003):
    predicted = trained_model.predict(dicom_path_003)

    first = predicted[0]

    dist = np.sqrt(np.sum([(first[s] - nodule_locations_003[s]) ** 2 for s in ["x", "y", "z"]]))

    assert (dist < 10)
