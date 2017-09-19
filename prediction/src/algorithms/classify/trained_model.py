# -*- coding: utf-8 -*-
"""
    algorithms.classify.trained_model
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    An API for a trained classification model to make predictions
    for if nodules are concerning or not.
"""

import numpy as np
import keras.models
from src.preprocess.load_ct import load_ct, MetaData


def predict(dicom_path, centroids, model_path=None,
            preprocess_ct=None, preprocess_model_input=None):
    """ Predicts if centroids are concerning or not.

    Given path to a DICOM image and an iterator of centroids:
        (1) load the classification model from its serialized state
        (2) pre-process the dicom into whatever format the classification
            model expects
        (3) for each centroid (which represents a nodule), yield a probability
            that the nodule is concerning

    Args:
        dicom_path (str): A path to the DICOM image
        centroids (list[dict]): A list of centroids of the form::
            {'x': int,
             'y': int,
             'z': int}
        model_path (str): A path to the serialized model
        preprocess_ct (preprocess.preprocess_dicom.PreprocessDicom): A preprocess
            method which aimed at brining the input data to the desired view.
        preprocess_model_input (callable[ndarray, list[dict]]): preprocess for a model
            input.

    Returns:
        list[dict]: a list of centroids with the probability they are
        concerning of the form::
            {'x': int,
             'y': int,
             'z': int,
             'p_concerning': float}
    """
    if not len(centroids) or model_path is None:
        return []

    model = keras.models.load_model(model_path)
    ct_array, meta = load_ct(dicom_path)
    if preprocess_ct is not None:
        meta = MetaData(meta)
        ct_array = preprocess_ct(ct_array, meta)
        if not isinstance(ct_array, np.ndarray):
            raise TypeError('The signature of preprocess_ct must be ' +
                            'callable[list[DICOM], ndarray] -> ndarray')

    patches = preprocess_model_input(ct_array, centroids)
    predictions = model.predict(patches)
    predictions = predictions.astype(np.float)

    for i, centroid in enumerate(centroids):
        centroid['p_concerning'] = predictions[i, 0]

    return centroids
