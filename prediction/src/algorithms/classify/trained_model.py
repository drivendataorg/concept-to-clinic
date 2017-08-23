# -*- coding: utf-8 -*-
"""
    algorithms.classify.trained_model
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    An API for a trained classification model to make predictions
    for if nodules are concerning or not.
"""

from src.preprocess.load_dicom import load_dicom


def predict(dicom_path, centroids):
    """ Predicts if centroids are concerning or not.

    Given path to a DICOM image and an iterator of centroids:
        (1) load the classification model from its serialized state
        (2) pre-process the dicom into whatever format the classification
            model expects
        (3) for each centroid (which represents a nodule), yield a probability
            that the nodule is concerning

    Args:
        dicom_path (str): A path to the DICOM image
        centroids (list(dict)): A list of centroids of the form::
            {'x': int,
             'y': int,
             'z': int}

    Returns:
        list(dict): a list of centroids with the probability they are
        concerning of the form::
            {'x': int,
             'y': int,
             'z': int,
             'p_concerning': float}
    """
    load_dicom(dicom_path)
    for centroid in centroids:
        centroid['p_concerning'] = 0.5

    return centroids
