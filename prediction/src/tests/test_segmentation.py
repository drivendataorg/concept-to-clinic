import os

from config import Config

from ..algorithms.segment.trained_model import predict


def test_correct_paths(dicom_paths):
    assert os.path.isdir(Config.SEGMENT_ASSETS_DIR)

    for path in dicom_paths:
        assert os.path.isdir(path)


def test_segment_predict(dicom_path):
    predicted = predict(dicom_path, [])
    assert predicted['volumes'] == []


def test_classify_predict_inference(dicom_path, nodule_locations):
    predicted = predict(dicom_path, nodule_locations)
    assert isinstance(predicted['binary_mask_path'], str)
    assert isinstance(predicted['volumes'], list)
