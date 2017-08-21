import os
from glob import glob

import dicom
import dicom_numpy

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


def load_dicom(path):
    """Function that orchestrates the loading of dicom datafiles of a dicom series into a numpy-array.

    Args:
        path (str): contains the path to the folder containing the dcm-files of a series.

    Returns:
        numpy-array containing the 3D-representation of the DICOM-series
    """

    file_pattern = os.path.join(path, '*.dcm')
    files = read_dicom_files(file_pattern)
    return _extract_voxel_data(files)
