# -*- coding: utf-8 -*-
"""
    algorithms.classify.trained_model
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    An API for a trained classification model to make predictions
    for if nodules are concerning or not.
"""

from src.algorithms.classify.src import gtr123_model
from src.preprocess.load_ct import load_ct, MetaData

import SimpleITK as sitk


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
    reader = sitk.ImageSeriesReader()
    filenames = reader.GetGDCMSeriesFileNames(dicom_path)

    if not filenames:
        raise ValueError("The path doesn't contain neither .mhd nor .dcm files")

    reader.SetFileNames(filenames)
    image = reader.Execute()

    if preprocess_ct:
        meta = load_ct(dicom_path)[1]
        voxel_data = preprocess_ct(image, MetaData(meta))
    else:
        voxel_data = image

    if preprocess_model_input:
        preprocessed = preprocess_model_input(voxel_data, centroids)
    else:
        preprocessed = voxel_data

    model_path = model_path or "src/algorithms/classify/assets/gtr123_model.ckpt"

    return gtr123_model.predict(preprocessed, centroids, model_path)
