import os
from glob import glob

import dicom
import dicom_numpy
import numpy as np

from .errors import EmptyDicomSeriesException


def read_dicom_files(file_pattern):
    try:
        files = [dicom.read_file(fn) for fn in glob(file_pattern)]

        if len(files) == 0:
            raise EmptyDicomSeriesException
    except dicom.errors.InvalidDicomError as e:
        print('Exception reading *.dcm-files: ', e)
        raise e

    return sorted(files, key=lambda x: float(x.SliceLocation))


def _extract_voxel_data(datasets):
    try:
        voxel_ndarray, ijk_to_xyz = dicom_numpy.combine_slices(datasets)
    except dicom_numpy.DicomImportException as e:
        print('Exception extracting voxel data: ', e)
        raise e
    except AttributeError as e:
        print('Exception extracting voxel data: ', e)
        raise dicom_numpy.DicomImportException('Invalid dicom.dataset.Dataset among datasets! ', e)

    return voxel_ndarray


def load_dicom(path, preprocess=None):
    """Function that orchestrates the loading of dicom datafiles of a dicom series into a numpy-array.

    Args:
        path (str): contains the path to the folder containing the dcm-files of a series.
        preprocess (callable[list[DICOM], ndarray] -> ndarray): A python function or method 
            aimed at preprocessing dicom.

    Returns:
        numpy-array containing the 3D-representation of the DICOM-series
    """

    file_pattern = os.path.join(path, '*.dcm')
    files = read_dicom_files(file_pattern)
    voxel_data = _extract_voxel_data(files)

    if preprocess is not None:
        voxel_data = preprocess(files, voxel_data)
        print(type(voxel_data))
        if not isinstance(voxel_data, np.ndarray):
            raise TypeError('The signature of preprocess must be '
                + 'callable[list[DICOM], ndarray] -> ndarray')
    
    return voxel_data
