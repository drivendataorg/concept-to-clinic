import os
from glob import glob

import SimpleITK
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


def load_dicom(path, voxel=True):
    """Function that orchestrates the loading of dicom datafiles of a dicom series into a numpy-array.

    Args:
        path (str): contains the path to the folder containing the dcm-files of a series.
        voxel (bool): whether to return or not to return  voxel data of the CT scan

    Returns:
        voxel_data (np.ndarray): numpy-array containing the 3D-representation of the DICOM-series.
        files (list[dicom.dataset.FileDataset]): DICOM-meta data.
    """

    file_pattern = os.path.join(path, '*.dcm')
    meta = read_dicom_files(file_pattern)
    if voxel:
        voxel_data = _extract_voxel_data(meta)
        meta = [voxel_data, meta]

    return meta


def load_metaimage(path, voxel=True):
    """Function that load a MetaImage files.

    Args:
        path (str): the path directly to the .mhd file itself, .raw
            file related to that .mhd should lie in the same directory.
        voxel (bool): whether to return or not to return  voxel data of the CT scan

    Returns:
        voxel_data (np.ndarray): numpy-array containing the 3D-representation of a MetaImage file.
        itkimage (SimpleITK.SimpleITK.Image): containing the meta-information of a MetaImage file.
    """

    meta = SimpleITK.ReadImage(path)
    if voxel:
        voxel_data = SimpleITK.GetArrayFromImage(meta)
        meta = [voxel_data, meta]

    return meta


def load_ct(path, voxel=True):
    """Function that orchestrates the loading of DICOM or MetaImage datafiles into a numpy-array.

    Args:
        path (str): contains the path to the folder containing either dcm-files of a series
            or .mhd/.raw files of MetaImage format. It also may can contain a path directly to
            a .mhd file itself.
        voxel (bool): whether to return or not to return  voxel data of the CT scan

    Returns:
        voxel_data (np.ndarray): numpy-array containing the 3D-representation of either
            DICOM-series or MetaImage file.
        meta (list[dicom.dataset.FileDataset] | SimpleITK.SimpleITK.Image): meta-information
            of a MetaImage file or DICOM-series in its original format.
    """
    dicom_pattern = os.path.join(path, '*.dcm')
    dicom_pattern = glob(dicom_pattern)
    mhd_pattern = os.path.join(path, '*.mhd')
    mhd_pattern = [path] + glob(mhd_pattern)
    mhd_pattern = next(filter(lambda x: x[-4:].lower() == '.mhd', mhd_pattern), None)
    if dicom_pattern:
        meta = load_dicom(path, voxel=voxel)
    elif mhd_pattern:
        meta = load_metaimage(mhd_pattern, voxel=voxel)
    else:
        raise ValueError('The path doesn\'t contain neither .mhd nor .dcm files.')

    return meta


class MetaData:
    """The standardised way to store meta information of CT.

    CT may be extracted from either DICOM or MetaImage file each of which has its own format
    for meta data (such as slice_thikness, spacing, etc.).


    Args:
        meta (list[dicom.dataset.FileDataset] | SimpleITK.SimpleITK.Image): CT's meta information
            from one of the primary formats.

    Returns:
        preprocess.load_dicom.MetaData
    """

    def extract_spacing_dcm(self):
        slice_thickness = float(self.meta[0].SliceThickness)
        # Every DICOM file have the same PixelSpacing
        spacing = self.meta[0].PixelSpacing
        # Taking into account ijk -> xyz transformation
        return np.asarray([spacing[1], spacing[0], slice_thickness])

    def extract_spacing_mhd(self):
        # Again, taking into account ijk -> xyz transformation
        return list(reversed(self.meta.GetSpacing()))

    def __init__(self, meta):
        self.meta = meta

        dicom_meta = False
        if isinstance(self.meta, list) and self.meta:
            dicom_meta = all([isinstance(_slice, dicom.dataset.FileDataset) for _slice in meta])
        mhd_meta = isinstance(self.meta, SimpleITK.SimpleITK.Image)
        if dicom_meta:
            # list of methods for DICOM meta
            self.spacing = self.extract_spacing_dcm()
        elif mhd_meta:
            # list of methods for MetaImage meta
            self.spacing = self.extract_spacing_mhd()
        else:
            raise ValueError('The meta should be either list[dicom.dataset.FileDataset] or SimpleITK.SimpleITK.Image')
