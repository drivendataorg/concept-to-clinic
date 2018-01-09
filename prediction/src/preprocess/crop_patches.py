import itertools

import numpy as np
import scipy.ndimage
from src.preprocess.preprocess_ct import mm_coordinates_to_voxel


def crop_patch(ct_array, patch_shape=None, centroids=None, stride=None, pad_value=0):
    """ Generator yield a patch of a desired shape for each centroid
    from a given a CT scan.

    Args:
        ct_array (np.ndarray): a numpy ndarray representation of a CT scan
        patch_shape (int, list[int]): a desired shape of a patch. If int will be provided,
            then patch will be a cube-shaped.
        centroids (list[dict]): A list of centroids of the form::
            {'x': int,
             'y': int,
             'z': int}
        stride (int): stride for patch coordinates meshgrid.
            If None is set (default), then no meshgrid will be returned.
        pad_value (int): value with which an array padding will be performed.
    Yields:
        np.ndarray: cropped patch from a CT scan.
        np.ndarray | None: meshgrid of a patch.
    """
    if centroids is None:
        centroids = []

    if patch_shape is None:
        patch_shape = []

    patch_shape = scipy.ndimage._ni_support._normalize_sequence(patch_shape, len(ct_array.shape))
    patch_shape = np.array(patch_shape)

    # array with padding size for each dimension
    padding_size = np.ceil(patch_shape / 2.).astype(np.int)

    # array with left and right padding for each dimension
    padding_array = np.stack([padding_size, padding_size], axis=1)

    # adding paddings at both ends of all dimensions
    ct_array = np.pad(ct_array, padding_array, mode='constant', constant_values=pad_value)

    for centroid in centroids:
        # cropping a patch with selected centroid in the center of it
        patch = ct_array[centroid[0]: centroid[0] + patch_shape[0],
                         centroid[1]: centroid[1] + patch_shape[1],
                         centroid[2]: centroid[2] + patch_shape[2]]

        if stride:
            normstart = np.array(centroid) / np.array(ct_array.shape) - 0.5
            normsize = np.array(patch_shape) / np.array(ct_array.shape)

            xx, yy, zz = np.meshgrid(np.linspace(normstart[0], normstart[0] + normsize[0], patch_shape[0] // stride),
                                     np.linspace(normstart[1], normstart[1] + normsize[1], patch_shape[1] // stride),
                                     np.linspace(normstart[2], normstart[2] + normsize[2], patch_shape[2] // stride),
                                     indexing='ij')
            coord = np.concatenate([xx[np.newaxis, ...], yy[np.newaxis, ...], zz[np.newaxis, :]], 0).astype('float32')
            yield patch, coord
        else:
            yield patch


def patches_from_ct(ct_array, meta, patch_shape=None, centroids=None, stride=None, pad_value=0):
    """ Given a CT scan, and a list of centroids return the list of patches
    of the desired patch shape.

    This is just a wrapper over crop_patch generator.

    Args:
        ct_array (np.ndarray): a numpy ndarray representation of a CT scan
        patch_shape (int | list[int]): the size of
            If int will be provided, then patch will be a cube.
        centroids (list[dict]): A list of centroids of the form::
            {'x': int,
             'y': int,
             'z': int}
        meta (src.preprocess.load_ct.MetaData): meta information of the CT scan.
        stride (int): stride for patches' coordinates meshgrids.
            If None is set (default), then no meshgrid will be returned.
        pad_value (int): value with which an array padding will be performed.

    Yields:
        np.ndarray: a cropped patch from the CT scan.
    """
    if patch_shape is None:
        patch_shape = []

    if centroids is None:
        centroids = []

    centroids = [[centroid[axis] for axis in 'zyx'] for centroid in centroids]

    # scale the coordinates according to spacing
    centroids = [mm_coordinates_to_voxel(centroid, meta) for centroid in centroids]

    patch_generator = crop_patch(ct_array, patch_shape, centroids, stride, pad_value)
    patches = itertools.islice(patch_generator, len(centroids))
    return list(patches)
