import numpy as np
import pytest

from src.preprocess import load_ct, preprocess_ct


@pytest.fixture
def dicom_path():
    yield '../images/LIDC-IDRI-0001/1.3.6.1.4.1.14519.5.2.1.6279.6001.298806137288633453246975630178/' \
          '1.3.6.1.4.1.14519.5.2.1.6279.6001.179049373636438705059720603192'


def test_create_params():
    preprocess_ct.Params()
    params = preprocess_ct.Params(spacing=1., ndim=3)
    assert len(params.spacing) == 3
    spacing = [shape == 1. for shape in params.spacing]
    assert all(spacing)

    with pytest.raises(ValueError):
        preprocess_ct.Params(clip_lower='one', clip_upper=0)
    with pytest.raises(ValueError):
        preprocess_ct.Params(clip_lower=1, clip_upper=0)
    with pytest.raises(ValueError):
        preprocess_ct.Params(ndim=0)
    with pytest.raises(RuntimeError):
        preprocess_ct.Params(spacing=(1, 1, 1, 1), ndim=3)
    with pytest.raises(ValueError):
        preprocess_ct.Params(min_max_normalize=[False])


def test_preprocess_dicom_pure(dicom_path):
    params = preprocess_ct.Params()
    preprocess = preprocess_ct.PreprocessCT(params)

    dicom_array, meta = load_ct.load_dicom(dicom_path)
    assert isinstance(dicom_array, np.ndarray)

    dicom_array, meta = load_ct.load_dicom(dicom_path)
    meta = load_ct.MetaData(meta)
    dicom_array = preprocess(dicom_array, meta)
    assert isinstance(dicom_array, np.ndarray)


def test_preprocess_dicom_clips(dicom_path):
    params = preprocess_ct.Params(clip_lower=-1, clip_upper=40)
    preprocess = preprocess_ct.PreprocessCT(params)

    dicom_array, meta = load_ct.load_ct(dicom_path)
    meta = load_ct.MetaData(meta)
    dicom_array = preprocess(dicom_array, meta)
    assert isinstance(dicom_array, np.ndarray)
    assert dicom_array.max() <= 40
    assert dicom_array.min() >= -1


def test_preprocess_dicom_min_max_scale(dicom_path):
    params = preprocess_ct.Params(clip_lower=-1000, clip_upper=400, min_max_normalize=True)
    preprocess = preprocess_ct.PreprocessCT(params)

    dicom_array, meta = load_ct.load_ct(dicom_path)
    meta = load_ct.MetaData(meta)
    dicom_array = preprocess(dicom_array, meta)
    assert isinstance(dicom_array, np.ndarray)
    assert dicom_array.max() <= 1
    assert dicom_array.min() >= 0
