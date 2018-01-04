# -*- coding: utf-8 -*-
"""
    algorithms.identify.trained_model
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    An API for a trained identification model to make predictions
    for where the centroids of nodules are in the DICOM image.
"""

import glob
from os import path

import dicom
from src.preprocess.errors import EmptyDicomSeriesException
from src.preprocess.lung_segmentation import save_lung_segments

from . import prediction


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
    if dicom_path[-1] != '/':
        dicom_path += '/'
    dicom_files = glob.glob(dicom_path + "*.dcm")
    if not dicom_files:
        raise EmptyDicomSeriesException
    
    patient_id = dicom.read_file(dicom_files[0]).SeriesInstanceUID
    #z, x, y = save_lung_segments(dicom_path, patient_id)
    orig_patient_img, rescaled_img_masks = save_lung_segments(dicom_path, patient_id)
    z, x, y = rescaled_img_masks
    z2, x2,y2 = orig_patient_img
    
    print("output from save_lung_segments:")
    print(f"rescaled mask shape: z: {z}, x: {x}, y: {y}")
    print(f"orig img shape: z: {z2}, x: {x2}, y: {y2}")
    
    results_df, batch_data = run_prediction(patient_id)
    
    # diff copies of output preds for debug
    raw_preds = results_df.copy()
    not_rescaled = results_df.copy()
    results_df_2 = results_df.copy()
    
    # not rescaled or snapped
    not_rescaled_df = not_rescaled[['coord_x', 'coord_y', 'coord_z', 'nodule_chance']].copy()
    not_rescaled_df.columns = ['x', 'y', 'z', 'p_nodule']
    not_rescaled = not_rescaled_df.to_dict(orient='record')
    
    ## rescaled and snapped using rescaled mask
    results_df['coord_x'] *= x
    results_df['coord_y'] *= y
    results_df['coord_z'] *= z
    rescaled_results_df = results_df[['coord_x', 'coord_y', 'coord_z', 'nodule_chance']].copy()
    rescaled_results_df.columns = ['x', 'y', 'z', 'p_nodule']
    rescaled_results_df[['x', 'y', 'z']] = rescaled_results_df[['x', 'y', 'z']].astype(int)
    rescaled_dict = rescaled_results_df.to_dict(orient='record')
    
    # rescaled and snapped using orig mask 
    results_df_2['coord_x'] *= x2
    results_df_2['coord_y'] *= y2
    results_df_2['coord_z'] *= z2
    rescaled_results_df_2 = results_df_2[['coord_x', 'coord_y', 'coord_z', 'nodule_chance']].copy()
    rescaled_results_df_2.columns = ['x', 'y', 'z', 'p_nodule']
    rescaled_results_df_2[['x', 'y', 'z']] = rescaled_results_df_2[['x', 'y', 'z']].astype(int)
    rescaled_dict_2 = rescaled_results_df_2.to_dict(orient='record')
    
    return rescaled_dict, rescaled_dict_2, not_rescaled, raw_preds, batch_data


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
        raise ValueError("magnification must be one of {} but was {}".format(magnification_choices, magnification))
    if ext_name not in ext_name_choices:
        raise ValueError("ext_name must be one of {} but was {}".format(ext_name_choices, ext_name))
    if ext_name == 'luna_posnegndsb_v':
        if version not in version_choices:
            raise ValueError("version must be one of {} but was {}".format(version_choices, version))
        if holdout not in holdout_choices:
            raise ValueError("holdout must be one of {} but was {}".format(holdout_choices, holdout))
    
    path_to_saved_models = path.join('src', 'algorithms', 'identify', 'assets')
    if ext_name == 'luna16_fs':
        model_path = path.join(path_to_saved_models, 'model_luna16_full__fs_best.hd5')
        results_df, batch_data = prediction.predict_cubes(model_path, patient_id,
                                              magnification=magnification, ext_name="luna16_fs")
    else:
        model_path = path.join(path_to_saved_models,
                               "model_luna_posnegndsb_v" + str(version) + "__fs_h" + str(holdout) + "_end.hd5")
        results_df, batch_data = prediction.predict_cubes(model_path,
            patient_id, magnification=magnification, ext_name="luna_posnegndsb_v" + str(version))
    return results_df, batch_data
