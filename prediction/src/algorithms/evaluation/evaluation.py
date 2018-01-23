"""
This file contains logic to evaluate the prediction models.
"""
import os

import numpy as np
import pylidc as pl
from tqdm import tqdm
from src.algorithms.classify import trained_model
from src.algorithms.evaluation.metrics import get_accuracy, logloss
from src.preprocess.lung_segmentation import get_z_range

try:
    from ....config import Config
except ValueError:
    from config import Config

CONFIDENCE_THRESHOLD = 0.5


def evaluate_classification(model_path=None):
    """
    Evaluate a classification model on the LIDC dataset
    Args:
        model_path: path to the serialized classification model. If None is given the grt123 model is taken
    """
    if model_path is None:
        model_path = os.path.join(Config.ALGOS_DIR, 'classify', 'assets', 'gtr123_model.ckpt')

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
            print("The following error occured when evaluating the scans of patient {}: {}".format(scan.patient_id, e))


if __name__ == '__main__':
    evaluate_classification()
