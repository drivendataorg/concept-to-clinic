# -*- coding: utf-8 -*-
"""
    algorithms.segment.trained_model
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    An API for a trained segmentation model to predict nodule boundaries and
    descriptive statistics.
"""

import numpy as np
import scipy.ndimage

from ...algorithms.segment.src.models.simple_3d_model import Simple3DModel
from ...preprocess.load_ct import load_ct, MetaData
from ...preprocess.preprocess_ct import mm_coordinates_to_voxel
from ...preprocess.lung_segmentation import DATA_SHAPE


def predict(dicom_path, centroids):
    """ Predicts nodule boundaries.

    Given a path to DICOM images and a list of centroids
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
    voxel_data, meta = load_ct(dicom_path)
    # Bring voxel data to shape X, Y, Z
    voxel_data = voxel_data.swapaxes(0, 2)
    voxel_data = voxel_data.swapaxes(0, 1)
    # Pad to input shape
    input_data = np.zeros((1, *DATA_SHAPE))
    input_data[0, :voxel_data.shape[0], :voxel_data.shape[1], :voxel_data.shape[2], 0] = voxel_data
    model = Simple3DModel().load_best()
    segment_path = model.predict(input_data)
    volumes = calculate_volume(segment_path, centroids, dicom_path)
    return {'binary_mask_path': segment_path, 'volumes': volumes}


def calculate_volume(segment_path, centroids, ct_path=None):
    """ Calculates tumor volume in cubic mm if a ct_path has been provided.

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
        ct_path (str): contains the path to the folder containing the dcm-files of a series.
            If None then volume will be returned in voxels.

    Returns:
        list[float]: a list of volumes in cubic mm (if a ct_path has been provided)
            of a connected component for each centroid.
    """
    if not centroids:
        return[]

    mask = np.load(segment_path)
    mask, _ = scipy.ndimage.label(mask)

    if ct_path:
        meta = load_ct(ct_path, voxel=False)
        meta = MetaData(meta)

    coords = [[centroid['z'], centroid['y'], centroid['x']] for centroid in centroids]

    if ct_path:
        coords = [mm_coordinates_to_voxel(coord, meta) for coord in coords]

    labels = [mask[coord[0], coord[1], coord[2]] for coord in coords]

    volumes = np.bincount(mask.flatten())
    volumes = volumes[labels].tolist()

    if ct_path:
        spacing = np.prod(meta.spacing)
        volumes = [volume * spacing for volume in volumes]

    return volumes
