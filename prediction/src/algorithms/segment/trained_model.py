# -*- coding: utf-8 -*-
"""
    algorithms.segment.trained_model
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    An API for a trained segmentation model to predict nodule boundaries and
    descriptive statistics.
"""


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
        str: a path to the serialized binary mask that can be used for
             segmentation
    """
    return 'path/to/segmentation'
