import numpy as np
import pytest

from src.preprocess import load_ct, preprocess_ct


def test_create_params():
    preprocess_ct.Params()

    with pytest.raises(TypeError):
        preprocess_ct.Params(clip_lower='one', clip_upper=0)
        preprocess_ct.Params(clip_lower=1, clip_upper=0)
        preprocess_ct.Params(ndim=0)
        preprocess_ct.Params(min_max_normalize=[False])


def test_preprocess_dicom_pure(dicom_path):
    preprocess = preprocess_ct.PreprocessCT()

    dicom_array, meta = load_ct.load_dicom(dicom_path)
    assert isinstance(dicom_array, np.ndarray)

    dicom_array, _ = preprocess(*load_ct.load_dicom(dicom_path))
    assert isinstance(dicom_array, np.ndarray)


def test_preprocess_dicom_clips(dicom_path):
    preprocess = preprocess_ct.PreprocessCT(clip_lower=-1, clip_upper=40)
    dicom_array, _ = preprocess(*load_ct.load_ct(dicom_path))
    assert isinstance(dicom_array, np.ndarray)
    assert dicom_array.max() <= 40
    assert dicom_array.min() >= -1


def test_preprocess_dicom_min_max_scale(dicom_path):
    preprocess = preprocess_ct.PreprocessCT(clip_lower=-1000, clip_upper=400, min_max_normalize=True)
    dicom_array, _ = preprocess(*load_ct.load_ct(dicom_path))
    assert isinstance(dicom_array, np.ndarray)
    assert dicom_array.max() <= 1
    assert dicom_array.min() >= 0
