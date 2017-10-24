# -*- coding: utf-8 -*-
"""
    algorithms.segment.trained_model
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    An API for a trained segmentation model to predict nodule boundaries and
    descriptive statistics.
"""

import os

import numpy as np
import scipy.ndimage
from keras.models import load_model

from ...algorithms.segment.src.model import dice_coef_loss, dice_coef
from ...algorithms.segment.src.training import get_best_model_path, get_data_shape
from ...preprocess.load_ct import load_ct, MetaData


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
    model = load_model(get_best_model_path(), custom_objects={'dice_coef_loss': dice_coef_loss, 'dice_coef': dice_coef})
    x, y, z, channels = get_data_shape()
    input_data = np.ndarray((1, x, y, z, channels))  # batch, x, y, z, channels
    # Crop the input data to the required data shape and pad with zeros
    padded_data = np.zeros_like(input_data)
    min_x, min_y, min_z = min(x, voxel_data.shape[0]), min(y, voxel_data.shape[1]), min(z, voxel_data.shape[2])
    padded_data[0, :min_x, :min_y, :min_z, 0] = voxel_data[:min_x, :min_y, :min_z]
    input_data = padded_data

    output_data = model.predict(input_data)
    segment_path = os.path.join(os.path.dirname(__file__), 'assets', "lung-mask.npy")
    np.save(segment_path, output_data[0, :, :, :, 0])
    volumes = calculate_volume(segment_path, centroids)

    return {
        'binary_mask_path': segment_path,
        'volumes': volumes
    }


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

    mask = np.load(segment_path)
    mask, _ = scipy.ndimage.label(mask)
    labels = [mask[centroid['x'], centroid['y'], centroid['z']] for centroid in centroids]
    volumes = np.bincount(mask.flatten())
    volumes = volumes[labels].tolist()

    if ct_path:
        meta = load_ct(ct_path, voxel=False)
        meta = MetaData(meta)
        spacing = np.prod(meta.spacing)
        volumes = [volume * spacing for volume in volumes]

    return volumes
