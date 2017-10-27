from os import path, listdir
from tempfile import TemporaryDirectory

import numpy as np

from ..preprocess.crop_dicom import crop_dicom


def test_crop_dicom(dicom_path):
    with TemporaryDirectory() as test_path:
        uncropped_series = crop_dicom(dicom_path, [0, 0, -95], [512, 512, -132.5], test_path)
        assert path.exists(path.join(test_path, '-95.000000.dcm'))
        assert path.exists(path.join(test_path, '-120.000000.dcm'))
        assert len([name for name in listdir(test_path) if path.isfile(path.join(test_path, name))]) == 16
        assert len(uncropped_series) == 16
        assert uncropped_series[0].Rows == 512
        assert uncropped_series[0].Columns == 512

    cropped_series = crop_dicom(dicom_path, [100, 100, -101], [120, 120, -106])
    assert len(cropped_series) == 2
    assert cropped_series[0].Rows == 20
    assert cropped_series[0].Columns == 20
    assert np.asarray(cropped_series[0].pixel_array).shape[0] == 20
    assert np.asarray(cropped_series[0].pixel_array).shape[1] == 20
    assert np.asarray([x for x in cropped_series if x.SliceLocation == -102.5][0].pixel_array)[0][0] == \
        np.asarray([x for x in uncropped_series if x.SliceLocation == -102.5][0].pixel_array)[100][100]

    assert np.asarray([x for x in cropped_series if x.SliceLocation == -102.5][0].pixel_array)[19][19] == \
        np.asarray([x for x in uncropped_series if x.SliceLocation == -102.5][0].pixel_array)[119][119]
