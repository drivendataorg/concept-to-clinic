# -*- coding: utf-8 -*-
"""
    preprocess.preprocess_patch
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    An API for a patch preprocessing, for concrete classification model architecture.
"""

import numpy as np
import keras.backend as K


def preprocess_patch_LR3DCNN(dicom_array, centroid):
    """Patch preprocessing function for LR3DCNN architecture.

    Args:
        dicom_array (ndarray): numpy-array containing the 3D-representation
            of the DICOM-series
        centroids (dict): A centroid's dict of the form::
            {'x': int,
             'y': int,
             'z': int}

    Returns:
        list[ndarray, ndarray, ndarray]

    """
    in_shapes = [(12, 21, 21),
                 (21, 12, 21),
                 (21, 21, 12)]

    in_patch = [dicom_array[centroid['x'] - in_shape[0]: centroid['x'] + in_shape[0],
                centroid['y'] - in_shape[1]: centroid['y'] + in_shape[1],
                centroid['z'] - in_shape[2]: centroid['z'] + in_shape[2]]
                for i, in_shape in enumerate(in_shapes)]

    return in_patch


def preprocess_LR3DCNN(dicom_array, centroids):
    """Peprocess function for LR3DCNN architecture.

    Args:
        dicom_array (ndarray): numpy-array containing the 3D-representation
            of the DICOM-series
        centroids (list(dict)): A list of centroids of the form::
            {'x': int,
             'y': int,
             'z': int}

    Returns:
        list[ndarray, ndarray, ndarray]

    """
    LR3DCNN_input = [[], [], []]
    for centroid in centroids:
        patch = preprocess_patch_LR3DCNN(dicom_array, centroid)
        for i in range(len(LR3DCNN_input)):
            LR3DCNN_input[i].append(patch[i])

    if K.image_data_format() == 'channels_last':
        channel_axis = -1
    else:
        channel_axis = 1

    for i in range(len(LR3DCNN_input)):
        LR3DCNN_input[i] = np.asarray(LR3DCNN_input[i])
        LR3DCNN_input[i] = np.expand_dims(LR3DCNN_input[i], channel_axis)

    return LR3DCNN_input
