import numpy as np
import os
import pytest
import shutil

from ..preprocess import crop_dicom as cd


@pytest.fixture
def dicom_path():
    os.makedirs('./temp')
    yield '../images/LIDC-IDRI-0001/1.3.6.1.4.1.14519.5.2.1.6279.6001.298806137288633453246975630178/' \
          '1.3.6.1.4.1.14519.5.2.1.6279.6001.179049373636438705059720603192'
    shutil.rmtree('./temp')


def test_crop_dicom(dicom_path):
    uncropped_series = cd.crop_dicom(dicom_path, [0, 0, -95], [512, 512, -132.5], './temp/test1')
    assert os.path.exists('./temp/test1/-95.000000.dcm')
    assert os.path.exists('./temp/test1/-120.000000.dcm')
    assert len([name for name in os.listdir('./temp/test1') if os.path.isfile('./temp/test1/' + name)]) == 16
    assert len(uncropped_series) == 16
    assert uncropped_series[0].Rows == 512
    assert uncropped_series[0].Columns == 512

    cropped_series = cd.crop_dicom(dicom_path, [100, 100, -101], [120, 120, -106])
    assert len(cropped_series) == 2
    assert cropped_series[0].Rows == 20
    assert cropped_series[0].Columns == 20
    assert np.asarray(cropped_series[0].pixel_array).shape[0] == 20
    assert np.asarray(cropped_series[0].pixel_array).shape[1] == 20
    assert np.asarray([x for x in cropped_series if x.SliceLocation == -102.5][0].pixel_array)[0][0] == \
        np.asarray([x for x in uncropped_series if x.SliceLocation == -102.5][0].pixel_array)[100][100]
    assert np.asarray([x for x in cropped_series if x.SliceLocation == -102.5][0].pixel_array)[19][19] == \
        np.asarray([x for x in uncropped_series if x.SliceLocation == -102.5][0].pixel_array)[119][119]
