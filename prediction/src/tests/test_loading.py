import os

from glob import glob
from tempfile import NamedTemporaryFile

import SimpleITK
import dicom
import dicom_numpy
import numpy as np
import pytest

from ..preprocess import errors
from ..preprocess.load_ct import (
    read_dicom_files, _extract_voxel_data, load_dicom, load_ct, load_metaimage,
    MetaData)


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


def test_load_metaimage(ct_path, dicom_path):
    path = glob(os.path.join(ct_path, '*.mhd'))[0]
    ct_array, meta = load_metaimage(path)

    assert isinstance(ct_array, np.ndarray)
    assert isinstance(meta, SimpleITK.SimpleITK.Image)

    path = glob(os.path.join(dicom_path, '*.dcm'))

    try:
        load_metaimage(path)
    except BaseException as e:
        assert 'Unable to determine ImageIO reader' in str(e)

    try:
        load_metaimage('.')
    except BaseException as e:
        assert 'PNGImageIO failed to read header for file' in str(e)


def test_load_ct(ct_path, dicom_path):
    ct_array, meta = load_ct(dicom_path)
    assert isinstance(ct_array, np.ndarray)
    assert ct_array.shape[0] == len(meta)

    ct_array, meta = load_ct(ct_path)
    assert isinstance(ct_array, np.ndarray)
    assert isinstance(meta, SimpleITK.SimpleITK.Image)

    try:
        load_ct('.')
    except ValueError as e:
        assert 'contain any .mhd or .dcm files' in str(e)


def test_load_ct_no_voxel(ct_path, dicom_path):
    meta = load_ct(dicom_path, voxel=False)
    assert isinstance(meta, list)
    assert len(meta) > 0
    assert all(isinstance(_slice, dicom.dataset.FileDataset) for _slice in meta)

    meta = load_ct(ct_path, voxel=False)
    assert isinstance(meta, SimpleITK.SimpleITK.Image)


def test_metadata(ct_path, dicom_path):
    meta = load_ct(dicom_path, voxel=False)
    meta = MetaData(meta)
    zipped = zip(meta.spacing, (2.5, 0.703125, 0.703125))
    assert all(m_axis == o_axis for m_axis, o_axis in zipped)

    meta = load_ct(ct_path, voxel=False)
    # the default axes order which is used is: (z, y, x)
    spacing = meta.GetSpacing()[::-1]
    meta = MetaData(meta)
    assert meta.spacing == spacing

    try:
        MetaData([1, 2, 3])
    except ValueError as e:
        assert 'either list[dicom.dataset.FileDataset] or SimpleITK' in str(e)
