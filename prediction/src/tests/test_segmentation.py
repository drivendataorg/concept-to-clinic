import os
import time

import pylidc as pl
import pytest

from config import Config

from . import get_timeout
from ..algorithms.identify.prediction import load_patient_images
from ..algorithms.segment.trained_model import predict
from ..preprocess.lung_segmentation import save_lung_segments, get_z_range


def test_correct_paths(dicom_paths):
    assert os.path.isdir(Config.SEGMENT_ASSETS_DIR)

    for path in dicom_paths:
        assert os.path.isdir(path)


def test_segment_predict_load(dicom_path):
    predicted = predict(dicom_path, [])
    assert predicted['volumes'] == []


def test_segment_predict_inference(dicom_path, nodule_locations):
    predicted = predict(dicom_path, nodule_locations)
    assert isinstance(predicted['binary_mask_path'], str)
    assert predicted['volumes']
    assert predicted['volumes'][0] > 0


def test_nodule_segmentation(dicom_path, nodule_001):
    predict(dicom_path, [nodule_001])


@pytest.mark.stop_timeout
def test_lung_segmentation(dicom_paths):
    """Test whether the annotations of the LIDC images are inside the segmented lung masks.
    Iterate over all local LIDC images, fetch the annotations, compute their positions within the masks and check that
    at this point the lung masks are set to 255."""

    for path in dicom_paths:
        min_z, max_z = get_z_range(path)
        directories = path.split('/')
        lidc_id = directories[2]
        patient_id = directories[-1]
        original, mask = save_lung_segments(path, patient_id)
        original_shape, mask_shape = original.shape, mask.shape
        scan = pl.query(pl.Scan).filter(pl.Scan.patient_id == lidc_id).first()

        for annotation in scan.annotations:
            centroid_x, centroid_y, centroid_z = annotation.centroid()
            patient_mask = load_patient_images(patient_id, wildcard="*_m.png")
            x_mask = int(mask_shape[1] / original_shape[1] * centroid_x)
            y_mask = int(mask_shape[2] / original_shape[2] * centroid_y)
            z_mask = int(abs(min_z) - abs(centroid_z))
            mask_value = patient_mask[z_mask, x_mask, y_mask]
            assert mask_value == 255


@pytest.mark.stop_timeout
def test_stop_timeout():
    timeout = get_timeout()
    if timeout > 0:
        time.sleep(timeout + 1)
        raise ValueError("This test should timeout")
