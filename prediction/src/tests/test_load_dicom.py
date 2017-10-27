import os

from tempfile import NamedTemporaryFile

import dicom
import dicom_numpy
import numpy as np
import pytest

from ..preprocess import errors
from ..preprocess.load_ct import read_dicom_files, _extract_voxel_data, load_dicom


def test_read_files(dicom_path):
    files = read_dicom_files(os.path.join(dicom_path, '*.dcm'))

    assert isinstance(files, list)
    assert len(files) > 0
    assert isinstance(files[0], dicom.dataset.Dataset)

    with NamedTemporaryFile() as not_a_dcm:
        with pytest.raises(dicom.errors.InvalidDicomError):
            read_dicom_files(not_a_dcm.name)

    with pytest.raises(errors.EmptyDicomSeriesException):
        read_dicom_files(os.path.join('.', '*.dcm'))


def test_extract_voxel_data(dicom_path):
    files = read_dicom_files(os.path.join(dicom_path, '*.dcm'))
    dicom_array = _extract_voxel_data(files)

    assert isinstance(dicom_array, np.ndarray)
    assert dicom_array.shape[0] == len(files)

    with pytest.raises(dicom_numpy.DicomImportException):
        _extract_voxel_data([dicom.dataset.Dataset()])


def test_load_dicom(dicom_path):
    dicom_array, meta = load_dicom(dicom_path)
    assert isinstance(dicom_array, np.ndarray)

    with pytest.raises(errors.EmptyDicomSeriesException):
        load_dicom('.')

