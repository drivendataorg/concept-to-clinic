import os
from glob import glob

import SimpleITK
import dicom
import numpy as np
import pytest

from ..preprocess import load_ct


@pytest.fixture
def metaimage_path():
    yield '../images/LUNA-0001/1.3.6.1.4.1.14519.5.2.1.6279.6001.102133688497886810253331438797'


@pytest.fixture
def dicom_path():
    yield '../images/LIDC-IDRI-0001/1.3.6.1.4.1.14519.5.2.1.6279.6001.298806137288633453246975630178/' \
          '1.3.6.1.4.1.14519.5.2.1.6279.6001.179049373636438705059720603192'


def test_load_metaimage(metaimage_path, dicom_path):
    path = glob(os.path.join(metaimage_path, '*.mhd'))[0]
    ct_array, meta = load_ct.load_metaimage(path)

    assert isinstance(ct_array, np.ndarray)
    assert isinstance(meta, SimpleITK.SimpleITK.Image)

    path = glob(os.path.join(dicom_path, '*.dcm'))
    try:
        load_ct.load_metaimage(path)
    except BaseException as e:
        assert 'Unable to determine ImageIO reader' in str(e)

    try:
        load_ct.load_metaimage('.')
    except BaseException as e:
        assert 'PNGImageIO failed to read header for file' in str(e)


def test_load_ct(metaimage_path, dicom_path):
    ct_array, meta = load_ct.load_ct(dicom_path)
    assert isinstance(ct_array, np.ndarray)
    assert ct_array.shape[2] == len(meta)

    ct_array, meta = load_ct.load_ct(metaimage_path)
    assert isinstance(ct_array, np.ndarray)
    assert isinstance(meta, SimpleITK.SimpleITK.Image)

    try:
        load_ct.load_ct('.')
    except ValueError as e:
        assert 'neither .mhd nor .dcm files.' in str(e)


def test_load_meta(metaimage_path, dicom_path):
    meta = load_ct.load_ct(dicom_path, voxel=False)
    assert isinstance(meta, list)
    assert len(meta) > 0
    assert all([isinstance(_slice, dicom.dataset.FileDataset)
                for _slice in meta])

    meta = load_ct.load_ct(metaimage_path, voxel=False)
    assert isinstance(meta, SimpleITK.SimpleITK.Image)


def test_metadata(metaimage_path, dicom_path):
    meta = load_ct.load_ct(dicom_path, voxel=False)
    meta = load_ct.MetaData(meta)
    zipped = zip(meta.spacing, (0.703125, 0.703125, 2.5))
    assert all([m_axis == o_axis for m_axis, o_axis in zipped])

    meta = load_ct.load_ct(metaimage_path, voxel=False)
    spacing = list(reversed(meta.GetSpacing()))
    meta = load_ct.MetaData(meta)
    assert meta.spacing == spacing

    try:
        load_ct.MetaData([1, 2, 3])
    except ValueError as e:
        assert 'either list[dicom.dataset.FileDataset] or SimpleITK' in str(e)
