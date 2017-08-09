import dicom
import dicom_numpy
from glob import glob
import os

from .errors import EmptyDicomSeriesException


def _read_files(file_pattern):
    try:
        files = [dicom.read_file(fn) for fn in glob(file_pattern)]
        if len(files) == 0:
            raise EmptyDicomSeriesException
    except dicom.errors.InvalidDicomError as e:
        print("Exception reading *.dcm-files: ", e)
        raise e
    files = sorted(files, key=lambda x: float(x.SliceLocation))
    return files


def _extract_voxel_data(datasets):
    try:
        voxel_ndarray, ijk_to_xyz = dicom_numpy.combine_slices(datasets)
    except dicom_numpy.DicomImportException as e:
        print("Exception extracting voxel data: ", e)
        raise e
    except AttributeError as e:
        print("Exception extracting voxel data: ", e)
        raise dicom_numpy.DicomImportException('Invalid dicom.dataset.Dataset among datasets! ', e)
    return voxel_ndarray


def load_dicom(path):
    """
    Function that orchestrates the loading of dicom datafiles of a dicom series into a numpy-array.

    :param path: String containing the path to the folder containing the dcm-files of a series.
    :return: numpy-array containing the 3D-representation of the DICOM-series
    """

    file_pattern = os.path.join(path, '*.dcm')
    files = _read_files(file_pattern)
    dicom_array = _extract_voxel_data(files)
    return dicom_array
