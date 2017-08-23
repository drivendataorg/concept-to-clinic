# -*- coding: utf-8 -*-
"""
    algorithms.identify.trained_model
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    An API for a trained identification model to make predictions
    for where the centroids of nodules are in the DICOM image.
"""

from src.preprocess.load_dicom import load_dicom


def predict(dicom_path):
    """ Predicts centroids of nodules in a DICOM image.

    Given an iterator of DICOM objects, this method will:
        (1) load the identification model from its serialized state
        (2) pre-process the dicom into whatever format the identification model
            expects
        (3) return centroids with a probability that each centroid
            is a nodule (as opposed to not a nodule)

    Note:
        This model doesn't detect whether or not a nodule is cancerous, that
        is done in the ``classify`` model.

    Args:
        dicom_path (str): a path to a DICOM image

    Returns:
        list(dict): a list of centroids in the form::
            {'x': int,
             'y': int,
             'z': int,
             'p_nodule': float}
    """
    load_dicom(dicom_path)
    return [{'x': 0,
             'y': 0,
             'z': 0,
             'p_nodule': 0.5}]
