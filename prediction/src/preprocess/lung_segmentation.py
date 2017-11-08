import logging
import math
import os
import sys

import cv2
import dicom
import numpy
import scipy

from dicom.errors import InvalidDicomError
from skimage.filters import roberts
from skimage.measure import label, regionprops
from skimage.morphology import disk, binary_erosion, binary_closing
from skimage.segmentation import clear_border

try:
    from ...config import Config
except ValueError:
    from config import Config


def get_z_range(dicom_path):
    """Return the Z range of the images in the DICOM path
    e.g. -379.0, -31.5

    Args:
        dicom_path: path that contains DICOM images

    Returns:
        minimum and maximum of the Z range
    """
    slices = load_patient(dicom_path)
    min_z, max_z = sys.float_info.max, sys.float_info.min
    for slice in slices:
        z = float(slice.ImagePositionPatient[2])
        if z < min_z:
            min_z = z
        if z > max_z:
            max_z = z
    return min_z, max_z


def save_lung_segments(dicom_path, patient_id):
    """Write the converted scan images and related lung masks to EXTRACTED_IMAGE_DIR.

    Args:
        dicom_path: a path to a DICOM directory
        patient_id: SeriesInstanceUID of the patient

    Returns:
        Original patient images (z, x, y),
        Rescaled mask images (z, x, y)
    """
    EXTRACTED_IMAGE_DIR = Config.EXTRACTED_IMAGE_DIR
    TARGET_VOXEL_MM = 1.00
    target_dir = os.path.join(os.getcwd(), EXTRACTED_IMAGE_DIR, patient_id)
    os.makedirs(target_dir, exist_ok=True)

    slices = load_patient(dicom_path)

    cos_value = (slices[0].ImageOrientationPatient[0])
    cos_degree = round(math.degrees(math.acos(cos_value)), 2)

    original_image = get_pixels_hu(slices)
    invert_order = slices[1].ImagePositionPatient[2] > slices[0].ImagePositionPatient[2]

    pixel_spacing = slices[0].PixelSpacing
    pixel_spacing.append(slices[0].SliceThickness)
    image = rescale_patient_images(original_image, pixel_spacing, TARGET_VOXEL_MM)
    if not invert_order:
        image = numpy.flipud(image)

    for index, org_img in enumerate(image):
        patient_dir = target_dir
        os.makedirs(patient_dir, exist_ok=True)
        img_path = patient_dir + "img_" + str(index).rjust(4, '0') + "_i.png"
        # if there exists slope,rotation image with corresponding degree
        if cos_degree > 0.0:
            org_img = cv_flip(org_img, org_img.shape[1], org_img.shape[0], cos_degree)
        img, mask = get_segmented_lungs(org_img.copy())
        org_img = normalize_hu(org_img)
        cv2.imwrite(img_path, org_img * 255)
        cv2.imwrite(img_path.replace("_i.png", "_m.png"), mask * 255)

    return original_image, image


def load_patient(src_dir):
    slices = []

    for s in os.listdir(src_dir):
        try:
            dicom_slice = dicom.read_file(os.path.join(src_dir, s))
        except InvalidDicomError:
            logging.error("{} is no valid DICOM".format(s))
        else:
            slices.append(dicom_slice)
    slices.sort(key=lambda x: int(x.InstanceNumber))

    try:
        slice_thickness = numpy.abs(slices[0].ImagePositionPatient[2] - slices[1].ImagePositionPatient[2])
    except IndexError as e:
        slice_thickness = numpy.abs(slices[0].SliceLocation - slices[1].SliceLocation)

    for s in slices:
        s.SliceThickness = slice_thickness

    return slices


def get_pixels_hu(slices):
    image = numpy.stack([s.pixel_array for s in slices])
    image = image.astype(numpy.int16)
    image[image == -2000] = 0

    for slice_number in range(len(slices)):
        intercept = slices[slice_number].RescaleIntercept
        slope = slices[slice_number].RescaleSlope

        if slope != 1:
            image[slice_number] = slope * image[slice_number].astype(numpy.float64)
            image[slice_number] = image[slice_number].astype(numpy.int16)

        image[slice_number] += numpy.int16(intercept)

    return numpy.array(image, dtype=numpy.int16)


def normalize_hu(image):
    MIN_BOUND = -1000.0
    MAX_BOUND = 400.0
    image = (image - MIN_BOUND) / (MAX_BOUND - MIN_BOUND)
    image[image > 1] = 1.
    image[image < 0] = 0.
    return image


def get_segmented_lungs(im):
    # Step 1: Convert into a binary image.
    binary = im < -400
    # Step 2: Remove the blobs connected to the border of the image.
    cleared = clear_border(binary)
    # Step 3: Label the image.
    label_image = label(cleared)
    # Step 4: Keep the labels with 2 largest areas.
    areas = [r.area for r in regionprops(label_image)]
    areas.sort()

    if len(areas) > 2:
        for region in regionprops(label_image):
            if region.area < areas[-2]:
                for coordinates in region.coords:
                    label_image[coordinates[0], coordinates[1]] = 0

    binary = label_image > 0
    # Step 5: Erosion operation with a disk of radius 2.
    # This operation is seperate the lung nodules attached to the blood vessels.
    selem = disk(2)
    binary = binary_erosion(binary, selem)
    # Step 6: Closure operation with a disk of radius 10.
    # This operation is to keep nodules attached to the lung wall.
    selem = disk(10)  # CHANGE BACK TO 10
    binary = binary_closing(binary, selem)
    # Step 7: Fill in the small holes inside the binary mask of lungs.
    edges = roberts(binary)
    binary = scipy.ndimage.binary_fill_holes(edges)
    # Step 8: Superimpose the binary mask on the input image.
    get_high_vals = binary == 0
    im[get_high_vals] = -2000
    return im, binary


def cv_flip(img, cols, rows, degree):
    M = cv2.getRotationMatrix2D((cols / 2, rows / 2), degree, 1.0)
    dst = cv2.warpAffine(img, M, (cols, rows))
    return dst


def rescale_patient_images(images_zyx, org_spacing_xyz, target_voxel_mm, is_mask_image=False):
    resize_x = 1.0
    resize_y = org_spacing_xyz[2] / target_voxel_mm
    interpolation = cv2.INTER_NEAREST if is_mask_image else cv2.INTER_LINEAR
    res = cv2.resize(images_zyx, dsize=None, fx=resize_x, fy=resize_y,
                     interpolation=interpolation)  # opencv assumes y, x, channels umpy array, so y = z pfff

    res = res.swapaxes(0, 2)
    res = res.swapaxes(0, 1)

    resize_x = org_spacing_xyz[0] / target_voxel_mm
    resize_y = org_spacing_xyz[1] / target_voxel_mm

    # cv2 can handle max 512 channels..
    if res.shape[2] > 512:
        res = res.swapaxes(0, 2)
        res1 = res[:256]
        res2 = res[256:]
        res1 = res1.swapaxes(0, 2)
        res2 = res2.swapaxes(0, 2)
        res1 = cv2.resize(res1, dsize=None, fx=resize_x, fy=resize_y, interpolation=interpolation)
        res2 = cv2.resize(res2, dsize=None, fx=resize_x, fy=resize_y, interpolation=interpolation)
        res1 = res1.swapaxes(0, 2)
        res2 = res2.swapaxes(0, 2)
        res = numpy.vstack([res1, res2])
        res = res.swapaxes(0, 2)
    else:
        res = cv2.resize(res, dsize=None, fx=resize_x, fy=resize_y, interpolation=interpolation)

    res = res.swapaxes(0, 2)
    res = res.swapaxes(2, 1)
    return res
