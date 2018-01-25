"""
This file contains logic to evaluate the prediction models.
"""
import glob
import os
from tqdm import tqdm
import sys
from collections import defaultdict

import numpy as np
import pylidc as pl

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
try:
    from src.algorithms.classify import trained_model
    from src.algorithms.evaluation.metrics import get_accuracy, logloss
    from src.algorithms.segment.src.training import get_lidc_id_index, get_full_dicom_paths
    from src.preprocess.lung_segmentation import get_z_range, save_lung_segments, DATA_SHAPE
    from src.algorithms.segment.src.evaluate import evaluate
    from src.algorithms.segment.src.models.simple_3d_model import Simple3DModel
    from config import Config
except ModuleNotFoundError as e:
    raise ModuleNotFoundError("Error when trying to import a module from a top level: " + str(e))

CONFIDENCE_THRESHOLD = 0.5


def evaluate_classification(model_path=None):
    """
    Evaluate a classification model on the LIDC dataset
    Args:
        model_path: path to the serialized classification model. If None is given the grt123 model is taken
    """
    if model_path is None:
        model_path = Config.ALGO_CLASSIFY_GTR123_PATH

    scans = pl.query(pl.Scan).all()
    confidences = []
    log_losses = []

    for scan in tqdm(scans):
        try:
            dicom_path = os.path.join(Config.SMALL_DICOM_PATHS, scan.patient_id, scan.study_instance_uid,
                                      scan.series_instance_uid)
            min_z, max_z = get_z_range(dicom_path)
            nodule_list = []
            for annotation in scan.annotations:
                centroid_x, centroid_y, centroid_z = annotation.centroid()
                z_index = int((centroid_z - min_z) / scan.slice_thickness)
                assert z_index >= 0, "Z index should be bigger than -1 but was {}".format(z_index)
                nodule_list.append({'x': round(centroid_x), 'y': round(centroid_y), 'z': round(z_index)})
            predicted = trained_model.predict(dicom_path, nodule_list, model_path)
            confidences.extend([d['p_concerning'] for d in predicted])
            np_confidences = np.array(confidences)
            true_positives = len(np_confidences[np_confidences >= CONFIDENCE_THRESHOLD])
            false_negatives = len(np_confidences) - true_positives
            print("Average accuracy: {}".format(get_accuracy(true_positives, 0, 0, false_negatives)))
            for score in confidences:
                log_losses.append(logloss(1, score))
            print("Average Log Loss: {}".format(np.mean(np.array(log_losses))))
        except Exception as e:
            print("The following error occurred when evaluating the scans of patient {}: {}".format(scan.patient_id, e))


def evaluate_segmentation(model=None):
    """
    Evaluate a segmentation model on the LIDC dataset
    Args:
        model: a SegmentationModel instance. If None is given the Simple3DModel is taken
    """
    if model is None:
        model = Simple3DModel()
        model.load_best()

    assets_dir = Config.SEGMENT_ASSETS_DIR
    dicom_paths = get_full_dicom_paths()

    if not dicom_paths:
        raise ValueError("No LIDC dicom images found")

    labels = glob.glob(os.path.join(assets_dir, "segmented_lung_patient_*.npy"))
    if not labels:
        raise ValueError("No labels were found")

    lidc_id_index = get_lidc_id_index(dicom_paths[0])

    input_image_shaped = np.zeros((1, *DATA_SHAPE))
    score_sums = defaultdict(lambda: 0)
    count = 0

    for path in tqdm(dicom_paths):
        directories = path.split(os.path.sep)
        lidc_id = directories[lidc_id_index]
        patient_id = directories[lidc_id_index + 2]  # last directory name is patient ID
        _, input_img = save_lung_segments(path, patient_id)
        mask_path = os.path.join(assets_dir, "segmented_lung_patient_{}.npy").format(lidc_id)
        if not os.path.isfile(mask_path):
            print("Expected mask for {} (patient {}) to exist at {} but it didn't exist".format(lidc_id, patient_id,
                                                                                                mask_path))
            continue
        output_img = np.load(mask_path)
        # Swap Z-Axis with X-Axis
        input_img = np.swapaxes(input_img, 0, 2)

        # Pad scan image and segmentation mask to DATA_SHAPE for easier comparison
        input_img = np.pad(input_img, ((0, DATA_SHAPE[0] - input_img.shape[0]),
                                       (0, DATA_SHAPE[1] - input_img.shape[1]),
                                       (0, DATA_SHAPE[2] - input_img.shape[2])), mode='constant')
        output_img = np.pad(output_img, ((0, DATA_SHAPE[0] - output_img.shape[0]),
                                         (0, DATA_SHAPE[1] - output_img.shape[1]),
                                         (0, DATA_SHAPE[2] - output_img.shape[2])), mode='constant')
        input_image_shaped[0, :, :, :, 0] = input_img
        predicted = model.predict(input_image_shaped)
        scores_dict = evaluate(output_img, predicted)
        for metric in scores_dict.keys():
            score_sums[metric] += scores_dict[metric]
        count += 1
        print("Average metrics after {} rounds:".format(count))
        for metric in scores_dict.keys():
            print("{}: {}".format(metric, score_sums[metric] / count))
