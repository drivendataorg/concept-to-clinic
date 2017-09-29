import numpy as np
import scipy.ndimage
from scipy.ndimage.morphology import binary_dilation, generate_binary_structure
from skimage import measure
from skimage.morphology import convex_hull_image


def binarize_per_slice(image, spacing, intensity_th=-600, sigma=1, area_th=30, eccen_th=0.99, bg_patch_size=10):
    """

    :param image:
    :param spacing:
    :param intensity_th: Anything below this threshold is considered air or lung
    :param sigma:
    :param area_th:
    :param eccen_th:
    :param bg_patch_size:
    :return:
    """
    bw = np.zeros(image.shape, dtype=bool)

    # prepare a mask, with all corner values set to nan
    image_size = image.shape[1]
    grid_axis = np.linspace(-image_size / 2 + 0.5, image_size / 2 - 0.5, image_size)
    x, y = np.meshgrid(grid_axis, grid_axis)
    d = (x ** 2 + y ** 2) ** 0.5
    nan_mask = (d < image_size / 2).astype(float)
    nan_mask[nan_mask == 0] = np.nan

    for i in range(image.shape[0]):
        # Check if corner pixels are identical, if so the slice  before Gaussian filtering
        if len(np.unique(image[i, 0:bg_patch_size, 0:bg_patch_size])) == 1:
            current_bw = scipy.ndimage.filters.gaussian_filter(np.multiply(image[i].astype('float32'), nan_mask), sigma,
                                                               truncate=2.0) < intensity_th
        else:
            current_bw = scipy.ndimage.filters.gaussian_filter(image[i].astype('float32'), sigma,
                                                               truncate=2.0) < intensity_th

        # select proper components
        label = measure.label(current_bw)
        properties = measure.regionprops(label)
        valid_label = set()

        for prop in properties:
            if prop.area * spacing[1] * spacing[2] > area_th and prop.eccentricity < eccen_th:
                valid_label.add(prop.label)

        current_bw = np.in1d(label, list(valid_label)).reshape(label.shape)
        bw[i] = current_bw

    return bw


def _fill_hole(bw):
    label = measure.label(~bw)
    bg_labels = {label[0, 0, 0], label[0, 0, -1], label[0, -1, 0], label[0, -1, -1],
                 label[-1, 0, 0], label[-1, 0, -1], label[-1, -1, 0], label[-1, -1, -1]}
    bw = ~np.in1d(label, list(bg_labels)).reshape(label.shape)

    return bw


def _merge_background_labels(label, cut_num):
    mid = int(label.shape[2] / 2)
    bg_label = {label[0, 0, 0], label[0, 0, -1], label[0, -1, 0], label[0, -1, -1],
                label[-1 - cut_num, 0, 0], label[-1 - cut_num, 0, -1], label[-1 - cut_num, -1, 0],
                label[-1 - cut_num, -1, -1],
                label[0, 0, mid], label[0, -1, mid], label[-1 - cut_num, 0, mid], label[-1 - cut_num, -1, mid]}
    for l in bg_label:
        label[label == l] = 0
    return label


def _remove_large_objects(label, spacing, area_th, dist_th):
    # prepare a distance map for further analysis
    x_axis = np.linspace(-label.shape[1] / 2 + 0.5, label.shape[1] / 2 - 0.5, label.shape[1]) * spacing[1]
    y_axis = np.linspace(-label.shape[2] / 2 + 0.5, label.shape[2] / 2 - 0.5, label.shape[2]) * spacing[2]
    x, y = np.meshgrid(x_axis, y_axis)
    d = (x ** 2 + y ** 2) ** 0.5
    vols = measure.regionprops(label)
    valid_label = set()
    # select components based on their area and distance to center axis on all slices
    for vol in vols:
        single_vol = label == vol.label
        slice_area = np.zeros(label.shape[0])
        min_distance = np.zeros(label.shape[0])
        for i in range(label.shape[0]):
            slice_area[i] = np.sum(single_vol[i]) * np.prod(spacing[1:3])
            min_distance[i] = np.min(single_vol[i] * d + (1 - single_vol[i]) * np.max(d))

        if np.average([min_distance[i] for i in range(label.shape[0]) if slice_area[i] > area_th]) < dist_th:
            valid_label.add(vol.label)
    return valid_label


def all_slice_analysis(bw, spacing, cut_num=0, vol_limit=[0.68, 8.2], area_th=6e3, dist_th=62):
    """

    Args:
        bw: Binary volume, created on a per-slice basis
        spacing: Image spacing
        cut_num: Number of top layers to be removed
        vol_limit:
        area_th:
        dist_th:

    Returns:

    """
    # in some cases, several top layers need to be removed first
    if cut_num > 0:
        bw0 = np.copy(bw)
        bw[-cut_num:] = False

    label = measure.label(bw, connectivity=1)

    # remove components access to corners
    label = _merge_background_labels(label, cut_num)

    # select components based on volume
    properties = measure.regionprops(label)
    for prop in properties:
        if prop.area * spacing.prod() < vol_limit[0] * 1e6 or prop.area * spacing.prod() > vol_limit[1] * 1e6:
            label[label == prop.label] = 0

    if len(np.unique(label)) == 1:
        return bw, 0

    valid_label = _remove_large_objects(label, spacing, area_th=area_th, dist_th=dist_th)

    bw = np.in1d(label, list(valid_label)).reshape(label.shape)

    # fill back the parts removed earlier
    if cut_num > 0:
        # bw1 is bw with removed slices, bw2 is a dilated version of bw, part of their intersection is returned as
        # final mask
        bw1 = np.copy(bw)
        bw1[-cut_num:] = bw0[-cut_num:]
        bw2 = np.copy(bw)
        bw2 = scipy.ndimage.binary_dilation(bw2, iterations=cut_num)
        bw3 = bw1 & bw2
        label = measure.label(bw, connectivity=1)
        label3 = measure.label(bw3, connectivity=1)
        l_list = set(np.unique(label)) - {0}
        valid_l3 = set()
        for l in l_list:
            indices = np.nonzero(label == l)
            l3 = label3[indices[0][0], indices[1][0], indices[2][0]]
            if l3 > 0:
                valid_l3.add(l3)
        bw = np.in1d(label3, list(valid_l3)).reshape(label3.shape)

    return bw, len(valid_label)


def _extract_main(bw, cover=0.95):
    for i in range(bw.shape[0]):
        current_slice = bw[i]
        label = measure.label(current_slice)
        properties = measure.regionprops(label)
        properties.sort(key=lambda x: x.area, reverse=True)
        area = [prop.area for prop in properties]
        count = 0
        sum = 0
        while sum < np.sum(area) * cover:
            sum += area[count]
            count += 1
        filter = np.zeros(current_slice.shape, dtype=bool)
        for j in range(count):
            bb = properties[j].bbox
            filter[bb[0]:bb[2], bb[1]:bb[3]] = filter[bb[0]:bb[2], bb[1]:bb[3]] | properties[j].convex_image
        bw[i] = bw[i] & filter

    label = measure.label(bw)
    properties = measure.regionprops(label)
    properties.sort(key=lambda x: x.area, reverse=True)
    bw = label == properties[0].label

    return bw


def _fill_2d_hole(bw):
    for i in range(bw.shape[0]):
        current_slice = bw[i]
        label = measure.label(current_slice)
        properties = measure.regionprops(label)
        for prop in properties:
            bb = prop.bbox
            current_slice[bb[0]:bb[2], bb[1]:bb[3]] = current_slice[bb[0]:bb[2], bb[1]:bb[3]] | prop.filled_image
        bw[i] = current_slice

    return bw


def two_lung_only(bw, spacing, max_iter=22, max_ratio=4.8):
    found_flag = False
    iter_count = 0
    bw0 = np.copy(bw)
    # Erodes until the two lungs are seperate.
    while not found_flag and iter_count < max_iter:
        label = measure.label(bw, connectivity=2)
        properties = measure.regionprops(label)
        properties.sort(key=lambda x: x.area, reverse=True)
        if len(properties) > 1 and properties[0].area / properties[1].area < max_ratio:
            found_flag = True
            bw1 = label == properties[0].label
            bw2 = label == properties[1].label
        else:
            bw = scipy.ndimage.binary_erosion(bw)
            iter_count = iter_count + 1

    if found_flag:
        d1 = scipy.ndimage.morphology.distance_transform_edt(np.logical_not(bw1), sampling=spacing)
        d2 = scipy.ndimage.morphology.distance_transform_edt(np.logical_not(bw2), sampling=spacing)
        bw1 = bw0 & (d1 < d2)
        bw2 = bw0 & (d1 > d2)

        bw1 = _extract_main(bw1)
        bw2 = _extract_main(bw2)

    else:
        bw1 = bw0
        bw2 = np.zeros(bw.shape).astype('bool')

    bw1 = _fill_2d_hole(bw1)
    bw2 = _fill_2d_hole(bw2)
    bw = bw1 | bw2

    return bw1, bw2, bw


def extract_lungs(image, spacing):
    """

    :param image: Dicom image loaded as numpy array
    :param spacing: Pixel spacing
    :return: Dicom image numpy
    """

    spacing = np.array(spacing)

    bw = binarize_per_slice(image, spacing)
    flag = 0
    cut_num = 0
    cut_step = 2
    bw0 = np.copy(bw)
    while flag == 0 and cut_num < bw.shape[0]:
        bw = np.copy(bw0)
        bw, flag = all_slice_analysis(bw, spacing, cut_num=cut_num, vol_limit=[0.68, 7.5])
        cut_num = cut_num + cut_step

    bw = _fill_hole(bw)
    bw1, bw2, bw = two_lung_only(bw, spacing)
    return bw


def process_mask(mask):
    convex_mask = np.copy(mask)
    for i_layer in range(convex_mask.shape[0]):
        mask1 = np.ascontiguousarray(mask[i_layer])
        if np.sum(mask1) > 0:
            mask2 = convex_hull_image(mask1)
            if np.sum(mask2) > 2 * np.sum(mask1):
                mask2 = mask1
        else:
            mask2 = mask1
        convex_mask[i_layer] = mask2
    struct = generate_binary_structure(3, 1)
    dilatedMask = binary_dilation(convex_mask, structure=struct, iterations=10)
    return dilatedMask
