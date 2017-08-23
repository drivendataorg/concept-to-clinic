# -*- coding: utf-8 -*-
"""
    algorithms.segment.trained_model
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    An API for a trained segmentation model to predict nodule boundaries and
    descriptive statistics.
"""

from src.preprocess.load_dicom import load_dicom


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
    segment_path = 'path/to/segmentation'
    volumes = calculate_volume(segment_path, centroids)
    return_value = {
        'binary_mask_path': segment_path,
        'volumes': volumes
    }
    return return_value


def calculate_volume(segment_path, centroids):
    """ Calculates tumor volume from pixel masks

    Args:
        segment_path (str): A path to the serialized binary mask for
            each centroid
        centroids (list[dict]): A list of centroids of the form::
            {'x': int,
             'y': int,
             'z': int}

    Returns:
        list[float]: List of volumes per centroid
    """
    return [0.5 for centroid in centroids]
