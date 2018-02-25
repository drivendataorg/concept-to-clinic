from src.preprocess import load_ct, preprocess_ct
from ..preprocess.improved_lung_segmentation import improved_lung_segmentation


def test_segmentation_over_LIDC(full_dicom_path):
    """
    Function is needed for fast loading and seeing DICOM or LUNA.

    Segmentation and separation of the lungs are provided with function
    "improved_lung_segmentation".
    """
    preprocess = preprocess_ct.PreprocessCT(to_hu=True)
    patient, _ = preprocess(*load_ct.load_ct(full_dicom_path))
    lung, lung_left, lung_right, trachea = improved_lung_segmentation(patient)


def test_segmentation_over_LUNA(full_mhd_path):
    """
    Function is needed for fast loading and seeing DICOM or LUNA.

    Segmentation and separation of the lungs are provided with function
    "improved_lung_segmentation".
    """
    preprocess = preprocess_ct.PreprocessCT(to_hu=True)
    patient, _ = preprocess(*load_ct.load_ct(full_mhd_path))
    lung, lung_left, lung_right, trachea = improved_lung_segmentation(patient)
