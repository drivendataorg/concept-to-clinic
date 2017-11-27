# -*- coding: utf-8 -*-
"""
    algorithms.identify.trained_model
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    An API for a trained identification model to make predictions
    for where the centroids of nodules are in the DICOM image.
"""
from os import path

import SimpleITK as sitk

from config import Config
from . import prediction
from .src import gtr123_model

MODELS_DIR = path.join(Config.CURRENT_DIR, 'identify_models')


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
    reader = sitk.ImageSeriesReader()
    if dicom_path.endswith('.mhd'):
        if not path.isfile(dicom_path):
            message = "The path {} does not exist"
            raise ValueError(message.format(dicom_path))
    else:
        filenames = reader.GetGDCMSeriesFileNames(dicom_path)
        if not filenames:
            message = "The path {} doesn't contain any .mhd or .dcm files"
            raise ValueError(message.format(dicom_path))

    # all required preprocssing and prediction is implemented in gtr123_model
    result = gtr123_model.predict(dicom_path)
    return result


def run_prediction(patient_id, magnification=1, ext_name="luna_posnegndsb_v", version=1, holdout=1):
    """Predict the nodules based on the extracted and transformed images using a specified model.

    Args:
        patient_id: SeriesInstanceUID of the patient
        magnification: what magnification to use, one of (1, 1.5, 2)
        ext_name: external name of the model, one of ("luna16_fs", "luna_posnegndsb_v")
        version: version of the model, only used if ext_name equals "luna_posnegndsb_v", one of (1, 2)
        holdout: whether to use, only used if ext_name equals "luna_posnegndsb_v", one of (0, 1)

    Returns:
        list(dict): a list of centroids in the form::
            {'x': int,
             'y': int,
             'z': int,
             'p_nodule': float}
    """
    magnification_choices = [1, 1.5, 2]
    ext_name_choices = ["luna16_fs", "luna_posnegndsb_v"]
    version_choices = [1, 2]
    holdout_choices = [0, 1]

    if magnification not in magnification_choices:
        message = 'magnification must be one of {} but was {}'
        raise ValueError(message.format(magnification_choices, magnification))

    if ext_name not in ext_name_choices:
        raise ValueError('ext_name must be one of {} but was {}'.format(ext_name_choices, ext_name))

    if ext_name == 'luna_posnegndsb_v':
        if version not in version_choices:
            raise ValueError('version must be one of {} but was {}'.format(version_choices, version))

        if holdout not in holdout_choices:
            raise ValueError('holdout must be one of {} but was {}'.format(holdout_choices, holdout))

    if ext_name == 'luna16_fs':
        model_path = path.join(MODELS_DIR, 'model_luna16_full__fs_best.hd5')
        ext = 'luna16_fs'
        results_df = prediction.predict_cubes(model_path, patient_id, magnification=magnification, ext_name=ext)
    else:
        model = 'model_luna_posnegndsb_v{}__fs_h{}_end.hd5'
        model_path = path.join(MODELS_DIR, model.format(version, holdout))
        ext = 'luna_posnegndsb_v{}'.format(version)
        results_df = prediction.predict_cubes(model_path, patient_id, magnification=magnification, ext_name=ext)

    return results_df
