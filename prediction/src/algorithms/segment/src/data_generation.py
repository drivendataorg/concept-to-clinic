import os

import numpy as np
import pylidc as pl
from config import Config
from tqdm import tqdm


def prepare_training_data():
    """Save a boolean mask of each DICOM scan at ../assets/segmented_lung_patient_{LIDC-ID}.npy that indicates whether
    a pixel was annotate by an expert as at least intermediate malicious or not.
    """
    INTERMEDIATE_MALICIOUS = 3
    ASSETS_DIR = Config.SEGMENT_ASSETS_DIR
    IMAGES_FULL_DIR = 'images_full'
    lidc_idri_directories = [os.path.join(Config.FULL_DICOM_PATHS, name) for name in os.listdir(Config.FULL_DICOM_PATHS)
                             if os.path.isdir(os.path.join(Config.FULL_DICOM_PATHS, name))]

    for path in tqdm(lidc_idri_directories):
        lidc_dir = path.split(IMAGES_FULL_DIR)[1]
        lidc_id = lidc_dir.split(os.path.sep)[1]
        lung_patient_file = os.path.join(ASSETS_DIR, "segmented_lung_patient_{}".format(lidc_id))

        if os.path.isfile(lung_patient_file):
            continue

        # Compute and save binary mask with information whether pixel is cancerous
        scan = pl.query(pl.Scan).filter(pl.Scan.patient_id == lidc_id).first()

        if scan is None:
            print("Scan for path '{}' was not found".format(path))
            continue

        vol = scan.to_volume(verbose=False)  # Leading zeros have to be removed from the DICOM file names

        # mask_vol is a boolean, indicator volume for the first annotation of the scan.
        mask_vol = np.zeros(vol.shape, dtype=np.bool)

        # Load DICOM files and obtain z-coords for each slice, so we can index into them.
        dicoms = scan.load_all_dicom_images(verbose=False)
        zs = [float(img.ImagePositionPatient[2]) for img in dicoms]

        cancerous_annotations = pl.query(pl.Annotation).filter(pl.Annotation.malignancy >= INTERMEDIATE_MALICIOUS,
                                                               pl.Annotation.scan_id == scan.id).all()

        for annotation in cancerous_annotations:
            mask, bbox = annotation.get_boolean_mask(return_bbox=True)

            # Obtain indexes of `mask` into `mask_vol`
            i1, i2 = bbox[0].astype(np.int)
            j1, j2 = bbox[1].astype(np.int)

            k1 = zs.index(bbox[2, 0])
            k2 = zs.index(bbox[2, 1])

            # In case the area already was segmented, don't overwrite it but add the annotated segmentation
            annotation_area = np.index_exp[i1:i2 + 1, j1:j2 + 1, k1:k2 + 1]
            if mask.shape != mask_vol[annotation_area].shape:
                annotation_area = np.index_exp[i1:i2 + 1, j1:j2 + 1, k1:k2]
            mask_vol[annotation_area] = np.logical_or(mask, mask_vol[annotation_area])

        np.save(lung_patient_file, mask_vol)
