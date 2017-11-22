import glob
import os

import numpy as np

from .models.simple_3d_model import Simple3DModel
from ....preprocess.lung_segmentation import save_lung_segments, DATA_SHAPE

try:
    from .....config import Config
except ValueError:
    from config import Config

BEST_MODEL_PATH = os.path.join(Config.SEGMENT_ASSETS_DIR, 'best_model.hdf5')


def get_full_dicom_paths():
    """
    Return the folder paths to the LIDC images e.g. ['/images_full/LIDC-IDRI-0307/1.3.6..../1.3.4.../']
    """
    dicom_paths = Config.FULL_DICOM_PATHS
    return glob.glob(os.path.join(dicom_paths, "**/**/**/"))


def get_lidc_id_index(path):
    """
    This method is necessary since the model should be trained outside of the docker container which results in
    different paths to the full LIDC images.
    Args:
        path: absolute path to a LIDC directory

    Returns: index of the LIDC id if the path is split at the directory separators
    """
    directories = path.split(os.path.sep)
    for index, directory in enumerate(directories):
        if directory.startswith("LIDC-IDRI-"):
            return index
    raise ValueError("Provided path is no valid LIDC path")


def train():
    """Load the training masks from the asset folder and train a keras model"""
    CUBOID_IMAGE_SHAPE = DATA_SHAPE
    CUBOID_BATCH = 4  # How many training pairs should be passed to model.fit in one batch

    assets_dir = Config.SEGMENT_ASSETS_DIR
    dicom_paths = get_full_dicom_paths()

    if not dicom_paths:
        raise ValueError("No LIDC dicom images found")

    labels = glob.glob(os.path.join(assets_dir, "segmented_lung_patient_*.npy"))
    if not labels:
        raise ValueError("No labels were found")

    input_data = np.zeros((CUBOID_BATCH, *CUBOID_IMAGE_SHAPE))
    output_data = np.zeros((CUBOID_BATCH, *CUBOID_IMAGE_SHAPE))
    model = Simple3DModel()
    lidc_id_index = get_lidc_id_index(dicom_paths[0])

    for batch_index in range(0, len(labels), CUBOID_BATCH):
        for index, path in enumerate(dicom_paths[batch_index:batch_index + CUBOID_BATCH]):
            directories = path.split(os.path.sep)
            lidc_id = directories[lidc_id_index]
            patient_id = directories[lidc_id_index + 2]  # last directory name is patient ID
            _, input_img = save_lung_segments(path, patient_id)
            mask_path = os.path.join(assets_dir, "segmented_lung_patient_{}.npy").format(lidc_id)
            if not os.path.isfile(mask_path):
                print("Mask for {} (patient {}) does not exist".format(lidc_id, patient_id))
                continue
            output_img = np.load(mask_path)

            new_input_img, new_output_img = np.zeros(CUBOID_IMAGE_SHAPE), np.zeros(CUBOID_IMAGE_SHAPE)

            new_input_img[:, :, :, 0] = input_img[:CUBOID_IMAGE_SHAPE[0], :CUBOID_IMAGE_SHAPE[1],
                                                  :CUBOID_IMAGE_SHAPE[2]]

            new_output_img[:, :, :, 0] = output_img[:CUBOID_IMAGE_SHAPE[0], :CUBOID_IMAGE_SHAPE[1],
                                                    :CUBOID_IMAGE_SHAPE[2]]

            input_data[index, :, :, :, :] = new_input_img
            output_data[index, :, :, :, :] = new_output_img

        model.fit(input_data, output_data)
