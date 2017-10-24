import glob
import math
import os

import numpy as np
import pylidc as pl
from keras.callbacks import ModelCheckpoint
from keras.models import load_model

from .model import simple_model_3d
from ....preprocess.lung_segmentation import save_lung_segments

try:
    from .....config import Config
except ValueError:
    from config import Config


def get_data_shape():
    # We need a fixed input (and thus output) size of the model. Something like taking the biggest spreads in every
    # dimension would be possible but we would then be supposed to pad all images to this size. My 8 GB GPU memory was
    # not enough for trying this with the 3D U-Net so I decided to temporarily set the shape to a smaller, fixed one.
    # dicom_paths = get_dicom_paths()
    # max_x, max_y, max_z = get_max_scaled_dimensions(dicom_paths)
    # return max_x, max_y, max_z, 1

    return 128, 128, 128, 1


def get_best_model_path():
    current_dir = os.path.dirname(os.path.realpath(__file__))
    assets_dir = os.path.abspath(os.path.join(current_dir, '../assets'))
    return os.path.join(assets_dir, 'best_model.hdf5')


def get_max_scaled_dimensions(dicom_paths):
    """Return the maximum x, y and z dimensions of all scaled DICOM images"""
    max_x, max_y, max_z = 0, 0, 0
    for path in dicom_paths:
        print(path)
        directories = path.split('/')
        lidc_id = directories[2]
        scan = pl.query(pl.Scan).filter(pl.Scan.patient_id == lidc_id).first()
        dicoms = scan.load_all_dicom_images()
        scaled_x, scaled_y = dicoms[0].Rows * scan.pixel_spacing, dicoms[0].Columns * scan.pixel_spacing
        scaled_z = len(dicoms) * scan.slice_thickness
        scaled_x, scaled_y, scaled_z = math.ceil(scaled_x), math.ceil(scaled_y), math.ceil(scaled_z)

        if scaled_x > max_x:
            max_x = scaled_x
        if scaled_y > max_y:
            max_y = scaled_y
        if scaled_z > max_z:
            max_z = scaled_z
    return max_x, max_y, max_z


def train(load_checkpoint=False):
    """Load the training masks from the asset folder and train a keras model"""
    CUBOID_IMAGE_SHAPE = get_data_shape()
    CUBOID_BATCH = 1  # How many training pairs should be passed to model.fit in one batch

    assets_dir = Config.SEGMENT_ASSETS_DIR
    dicom_paths = glob.glob(Config.DICOM_PATHS_DOCKER_WILDCARD)

    labels = glob.glob(os.path.join(assets_dir, "segmented_lung_patient_*.npy"))

    input_data = np.zeros((CUBOID_BATCH, *CUBOID_IMAGE_SHAPE))
    output_data = np.zeros((CUBOID_BATCH, *CUBOID_IMAGE_SHAPE))
    best_model_path = get_best_model_path()

    if os.path.isfile(best_model_path) and load_checkpoint:
        model = load_model(best_model_path)
    else:
        model = simple_model_3d(CUBOID_IMAGE_SHAPE)

    for batch_index in range(0, len(labels), CUBOID_BATCH):

        for index, path in enumerate(dicom_paths[batch_index:batch_index + CUBOID_BATCH]):
            directories = path.split(os.path.sep)
            lidc_id = directories[5]
            patient_id = directories[-1]
            _, input_img = save_lung_segments(path, patient_id)
            output_img = np.load(os.path.join(assets_dir, "segmented_lung_patient_{}.npy").format(lidc_id))

            new_input_img, new_output_img = np.zeros(CUBOID_IMAGE_SHAPE), np.zeros(CUBOID_IMAGE_SHAPE)
            new_input_img[:, :, :, 0] = input_img[:CUBOID_IMAGE_SHAPE[0], :CUBOID_IMAGE_SHAPE[1],
                                                  :CUBOID_IMAGE_SHAPE[2]]
            new_output_img[:, :, :, 0] = output_img[:CUBOID_IMAGE_SHAPE[0], :CUBOID_IMAGE_SHAPE[1],
                                                    :CUBOID_IMAGE_SHAPE[2]]

            input_data[index, :, :, :, :] = new_input_img
            output_data[index, :, :, :, :] = new_output_img

        model_checkpoint = ModelCheckpoint(best_model_path, monitor='loss', verbose=1, save_best_only=True)
        model.fit(input_data, output_data, callbacks=[model_checkpoint], epochs=10)
