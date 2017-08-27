import numpy as np
import pytest

from ..preprocess import load_dicom, preprocess_dicom


@pytest.fixture
def dicom_path():
    yield '../images/LIDC-IDRI-0001/1.3.6.1.4.1.14519.5.2.1.6279.6001.298806137288633453246975630178/' \
          '1.3.6.1.4.1.14519.5.2.1.6279.6001.179049373636438705059720603192'


def test_create_params():
    preprocess_dicom.Params()
    params = preprocess_dicom.Params(voxel_shape=1., ndim=3)
    assert len(params.voxel_shape) == 3
    voxel_shape = [shape == 1. for shape in params.voxel_shape]
    assert all(params.voxel_shape)

    with pytest.raises(ValueError):
        preprocess_dicom.Params(clip_lower='one', clip_upper=0)
    with pytest.raises(ValueError):
        preprocess_dicom.Params(clip_lower=1, clip_upper=0)
    with pytest.raises(ValueError):
        preprocess_dicom.Params(ndim=0)
    with pytest.raises(RuntimeError):
        preprocess_dicom.Params(voxel_shape=(1, 1, 1, 1), ndim=3)
    with pytest.raises(ValueError):
        preprocess_dicom.Params(min_max_normalize=[False])


def test_preprocess_dicom_pure(dicom_path):
    params = preprocess_dicom.Params()
    preprocess = preprocess_dicom.PreprocessDicom(params)

    dicom_array = load_dicom.load_dicom(dicom_path)
    assert isinstance(dicom_array, np.ndarray)

    dicom_array = load_dicom.load_dicom(dicom_path, preprocess)
    assert isinstance(dicom_array, np.ndarray)


def test_preprocess_dicom_clips(dicom_path):
    params = preprocess_dicom.Params(clip_lower=-1, clip_upper=40)
    preprocess = preprocess_dicom.PreprocessDicom(params)

    dicom_array = load_dicom.load_dicom(dicom_path, preprocess)
    assert isinstance(dicom_array, np.ndarray)
    assert dicom_array.max() <= 40
    assert dicom_array.min() >= -1


def test_preprocess_dicom_min_max_scale(dicom_path):
    params = preprocess_dicom.Params(clip_lower=-1000, clip_upper=400, min_max_normalize=True)
    preprocess = preprocess_dicom.PreprocessDicom(params)

    dicom_array = load_dicom.load_dicom(dicom_path, preprocess)
    assert isinstance(dicom_array, np.ndarray)
    assert dicom_array.max() <= 1
    assert dicom_array.min() >= 0
