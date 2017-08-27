# -*- coding: utf-8 -*-
"""
    algorithms.segment.trained_model
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    An API for a trained segmentation model to predict nodule boundaries and
    descriptive statistics.
"""

from src.preprocess.load_dicom import load_dicom, load_meta

import numpy as np
import os
import scipy.ndimage


def predict(dicom_path, centroids):
    """ Predicts nodule boundaries.

    Given a pth to a DICOM image and a list of centroids
        (1) load the segmentation model from its serialized state
        (2) pre-process the dicom data into whatever format the segmentation
            model expects
        (3) for each pixel create an indicator 0 or 1 of if the pixel is
            cancerous
        (4) write this binary mask to disk, and return the path to the mask

    Args:
        dicom_path (str): a path to a DICOM directory
        centroids (list[dict]): A list of centroids of the form::
            {'x': int,
             'y': int,
             'z': int}

    Returns:
        dict: Dictionary containing path to serialized binary masks and
            volumes per centroid with form::
            {'binary_mask_path': str,
             'volumes': list[float]}
    """
    load_dicom(dicom_path)
    segment_path = os.path.join(os.path.dirname(__file__),
                                'assets', 'test_mask.npy')
    volumes = calculate_volume(segment_path, centroids)
    return_value = {
        'binary_mask_path': segment_path,
        'volumes': volumes
    }

    return return_value


def calculate_volume(segment_path, centroids, dicom_path=None):
    """ Calculates tumor volume in cubic mm if a dicom_path has been provided.

    Given the path to the serialized mask and a list of centroids
        (1) For each centroid, calculate the volume of the tumor.
        (2) DICOM has voxels' sizes in mm therefore the volume should be in real
        measurements (not pixels).
    Args:
        segment_path (str): a path to a mask file
        centroids (list[dict]): A list of centroids of the form::
            {'x': int,
             'y': int,
             'z': int}
        dicom_path (str): contains the path to the folder containing the dcm-files of a series.
            If None then volume will be returned in voxels.

    Returns:
        list[float]: a list of volumes in cubic mm (if a dicom_path has been provided)
            of a connected component for each centroid.
    """

    mask = np.load(segment_path)
    mask, _ = scipy.ndimage.label(mask)
    labels = [mask[centroid['x'], centroid['y'], centroid['z']] for centroid in centroids]
    volumes = np.bincount(mask.flatten())
    volumes = volumes[labels].tolist()

    if dicom_path:
        dicom_files = load_meta(dicom_path)
        slice_locations = [dcm_file.SliceLocation for dcm_file in dicom_files]
        slice_thickness = np.diff(slice_locations).mean()
        # Every DICOM study preserve the same PixelSpacing along its sub files
        voxel_shape = dicom_files[0].PixelSpacing
        # Taking into account ijk -> xyz transformation
        voxel_shape = np.prod([voxel_shape[1], voxel_shape[0], slice_thickness])
        volumes = [volume * voxel_shape for volume in volumes]

    return volumes
