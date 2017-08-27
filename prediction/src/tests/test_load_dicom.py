import os

import dicom
import dicom_numpy
import numpy as np
import pytest

from ..preprocess import load_dicom as ld
from ..preprocess import errors


@pytest.fixture
def dicom_path():
    open('./not_a_dcm.xml', 'w+')
    yield '../images/LIDC-IDRI-0001/1.3.6.1.4.1.14519.5.2.1.6279.6001.298806137288633453246975630178/' \
          '1.3.6.1.4.1.14519.5.2.1.6279.6001.179049373636438705059720603192'
    os.remove('./not_a_dcm.xml')


def test_read_files(dicom_path):
    files = ld.read_dicom_files(os.path.join(dicom_path, '*.dcm'))

    assert isinstance(files, list)
    assert len(files) > 0
    assert isinstance(files[0], dicom.dataset.Dataset)

    with pytest.raises(dicom.errors.InvalidDicomError):
        ld.read_dicom_files('./not_a_dcm.xml')

    with pytest.raises(errors.EmptyDicomSeriesException):
        ld.read_dicom_files(os.path.join('.', '*.dcm'))


def test_extract_voxel_data(dicom_path):
    files = ld.read_dicom_files(os.path.join(dicom_path, '*.dcm'))
    dicom_array = ld._extract_voxel_data(files)

    assert isinstance(dicom_array, np.ndarray)
    assert dicom_array.shape[2] == len(files)

    with pytest.raises(dicom_numpy.DicomImportException):
        ld._extract_voxel_data([dicom.dataset.Dataset()])


def test_load_dicom(dicom_path):
    dicom_array = ld.load_dicom(dicom_path)

    assert isinstance(dicom_array, np.ndarray)

    with pytest.raises(errors.EmptyDicomSeriesException):
        ld.load_dicom('.')


def test_load_meta(dicom_path):
    dicom_series = ld.load_meta(dicom_path)

    assert isinstance(dicom_series, list)
