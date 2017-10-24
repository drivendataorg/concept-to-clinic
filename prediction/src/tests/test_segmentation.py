import os
import glob
import pytest
from config import Config

from ..algorithms.segment import trained_model


def test_correct_paths():
    assert os.path.isdir(Config.SEGMENT_ASSETS_DIR)
    for path in glob.glob(Config.DICOM_PATHS_DOCKER_WILDCARD):
        assert os.path.isdir(path)


@pytest.fixture
def dicom_path():
    yield '../images/LIDC-IDRI-0001/1.3.6.1.4.1.14519.5.2.1.6279.6001.298806137288633453246975630178/' \
          '1.3.6.1.4.1.14519.5.2.1.6279.6001.179049373636438705059720603192'


def test_segment_predict(dicom_path):
    predicted = trained_model.predict(dicom_path, [])

    assert predicted['volumes'] == []


def test_classify_predict_inference(dicom_path):
    predicted = trained_model.predict(dicom_path, [{'x': 50, 'y': 50, 'z': 21}])

    assert isinstance(predicted['binary_mask_path'], str)
    assert isinstance(predicted['volumes'], list)
