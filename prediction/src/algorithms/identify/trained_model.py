# -*- coding: utf-8 -*-
"""
    algorithms.identify.trained_model
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    An API for a trained identification model to make predictions
    for where the centroids of nodules are in the DICOM image.
"""

import glob
import logging
import math
import os

import cv2
import dicom
import numpy
from src.preprocess.errors import EmptyDicomSeriesException

from . import helpers
from . import prediction

TARGET_VOXEL_MM = 1.00
EXTRACTED_IMAGE_DIR = "data/extracted/"


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
    z, x, y = preprocess(dicom_path, patient_id)
    results_df = run_prediction(patient_id)
    results_df['coord_x'] *= x
    results_df['coord_y'] *= y
    results_df['coord_z'] *= z
    rescaled_results_df = results_df[['coord_x', 'coord_y', 'coord_z', 'nodule_chance']].copy()
    rescaled_results_df.columns = ['x', 'y', 'z', 'p_nodule']
    rescaled_results_df[['x', 'y', 'z']] = rescaled_results_df[['x', 'y', 'z']].astype(int)
    rescaled_dict = rescaled_results_df.to_dict(orient='record')
    return rescaled_dict


def preprocess(dicom_path, patient_id):
    """Convert the data such that it can be used by the De Wit algorithm. Write the converted data to EXTRACTED_IMAGE_DIR.

    Args:
        dicom_path: a path to a DICOM directory
        patient_id: SeriesInstanceUID of the patient

    Returns:
        shape of the patient images (z, x, y)
    """

    target_dir = EXTRACTED_IMAGE_DIR + patient_id + "/"
    if not os.path.exists(target_dir):
        os.mkdir(target_dir)

    slices = helpers.load_patient(dicom_path)
    logging.info("Number of Slices", len(slices), "\tSliceThickness", slices[0].SliceThickness, "\tPixelSpacing",
                 slices[0].PixelSpacing)
    logging.info("Orientation: ", slices[0].ImageOrientationPatient)

    cos_value = (slices[0].ImageOrientationPatient[0])
    cos_degree = round(math.degrees(math.acos(cos_value)), 2)

    pixels = helpers.get_pixels_hu(slices)
    image = pixels
    logging.info("Image Shape: " + str(image.shape))

    invert_order = slices[1].ImagePositionPatient[2] > slices[0].ImagePositionPatient[2]
    logging.info("Invert order: ", invert_order, " - ", slices[1].ImagePositionPatient[2], ",",
                 slices[0].ImagePositionPatient[2])

    pixel_spacing = slices[0].PixelSpacing
    pixel_spacing.append(slices[0].SliceThickness)
    image = helpers.rescale_patient_images(image, pixel_spacing, TARGET_VOXEL_MM)
    if not invert_order:
        image = numpy.flipud(image)

    for i in range(image.shape[0]):
        patient_dir = target_dir
        if not os.path.exists(patient_dir):
            os.mkdir(patient_dir)
        img_path = patient_dir + "img_" + str(i).rjust(4, '0') + "_i.png"
        org_img = image[i]
        # if there exists slope,rotation image with corresponding degree
        if cos_degree > 0.0:
            org_img = helpers.cv_flip(org_img, org_img.shape[1], org_img.shape[0], cos_degree)
        img, mask = helpers.get_segmented_lungs(org_img.copy())
        org_img = helpers.normalize_hu(org_img)
        cv2.imwrite(img_path, org_img * 255)
        cv2.imwrite(img_path.replace("_i.png", "_m.png"), mask * 255)

    return image.shape


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

    if ext_name == 'luna16_fs':
        results_df = prediction.predict_cubes("/identify_models/model_luna16_full__fs_best.hd5", patient_id,
                                              magnification=magnification, ext_name="luna16_fs")
    else:
        results_df = prediction.predict_cubes(
            "/identify_models/model_luna_posnegndsb_v" + str(version) + "__fs_h" + str(holdout) + "_end.hd5",
            patient_id, magnification=magnification, ext_name="luna_posnegndsb_v" + str(version))
    return results_df
