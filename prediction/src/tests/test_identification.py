import numpy as np

from . import skip_if_slow
from ..algorithms.identify import trained_model


@skip_if_slow
def test_identify_nodules_001(dicom_path, nodule_001):
    predicted = trained_model.predict(dicom_path)
    first = predicted[0]
    dist = np.sqrt(np.sum([(first[s] - nodule_001[s]) ** 2 for s in ["x", "y", "z"]]))
    assert (dist < 10)


@skip_if_slow
def test_identify_nodules_003(dicom_path_003, nodule_003):
    predicted = trained_model.predict(dicom_path_003)
    first = predicted[0]
    dist = np.sqrt(np.sum([(first[s] - nodule_003[s]) ** 2 for s in ["x", "y", "z"]]))
    assert (dist < 10)
