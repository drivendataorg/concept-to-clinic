import glob

import pylidc as pl
from src.algorithms.identify.prediction import load_patient_images
from src.preprocess.lung_segmentation import save_lung_segments, get_z_range


def get_dicom_paths():
    """Return DICOM paths to all LIDC direcotries
    e.g. ['../images_full/LIDC-IDRI-0001/1.3.6.1.4.1.14519.5.2.1.6279.6001.298806137288633453246975630178/' \
          '1.3.6.1.4.1.14519.5.2.1.6279.6001.179049373636438705059720603192']"""
    return glob.glob("../images_full/LIDC-IDRI-*/**/**")


def test_lung_segmentation():
    """Test whether the annotations of the LIDC images are inside the segmented lung masks.
    Iterate over all local LIDC images, fetch the annotations, compute their positions within the masks and check that
    at this point the lung masks are set to 255."""

    dicom_paths = get_dicom_paths()
    for path in dicom_paths:
        min_z, max_z = get_z_range(path)
        directories = path.split('/')
        lidc_id = directories[2]
        patient_id = directories[-1]
        original_shape, mask_shape = save_lung_segments(path, patient_id)
        scan = pl.query(pl.Scan).filter(pl.Scan.patient_id == lidc_id).first()
        for annotation in scan.annotations:
            centroid_x, centroid_y, centroid_z = annotation.centroid()
            patient_mask = load_patient_images(patient_id, wildcard="*_m.png", exclude_wildcards=[])
            x_mask = int(mask_shape[1] / original_shape[1] * centroid_x)
            y_mask = int(mask_shape[2] / original_shape[2] * centroid_y)
            z_mask = int(abs(min_z) - abs(centroid_z))
            mask_value = patient_mask[z_mask, x_mask, y_mask]
            assert mask_value == 255
