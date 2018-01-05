import itertools

import numpy as np
import scipy.ndimage
from src.preprocess import load_ct


def mm2voxel(coord, origin=0., spacing=1.):
    """ Transfer coordinates in mm into voxel's location

    Args:
        coord (scalar | list[scalar]): coordinates in mm.
        origin (scalar | list[scalar]): an origin of the CT scan in mm.
        spacing (scalar | list[scalar]): an CT scan's spacing, i.e. the size of one voxel in mm.

    Returns:
        list[int]: the voxel location related to the coord.
    """
    if np.isscalar(coord):
        coord = [coord]

    coord = np.array(coord)
    origin = scipy.ndimage._ni_support._normalize_sequence(origin, len(coord))
    spacing = scipy.ndimage._ni_support._normalize_sequence(spacing, len(coord))
    coord = np.ceil((coord - np.array(origin)) / np.array(spacing))
    return coord.astype(np.int)


def crop_patch(ct_array, meta, patch_shape=None, centroids=None, stride=None, pad_value=0):
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
        meta (src.preprocess.load_ct.MetaData): meta information of the CT scan.
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

    if not isinstance(meta, load_ct.MetaData):
        meta = load_ct.MetaData(meta)

    patch_shape = scipy.ndimage._ni_support._normalize_sequence(patch_shape, len(ct_array.shape))
    patch_shape = np.array(patch_shape)
    init_shape = np.array(ct_array.shape)
    padding = np.ceil(patch_shape / 2.).astype(np.int)
    padding = np.stack([padding, padding], axis=1)
    ct_array = np.pad(ct_array, padding, mode='constant', constant_values=pad_value)

    for centroid in centroids:
        centroid = mm2voxel([centroid[axis] for axis in 'zyx'], meta.origin, meta.spacing)

        patch = ct_array[centroid[0]: centroid[0] + patch_shape[0],
                         centroid[1]: centroid[1] + patch_shape[1],
                         centroid[2]: centroid[2] + patch_shape[2]]

        if stride:
            init_shape += np.clip(patch_shape // 2 - centroid, 0, np.inf).astype(np.int64)
            init_shape += np.clip(centroid + patch_shape // 2 - init_shape, 0, np.inf).astype(np.int64)

            normstart = (np.array(centroid) - patch_shape / 2) / init_shape - 0.5
            normsize = patch_shape / init_shape
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

    patch_generator = crop_patch(ct_array, meta, patch_shape, centroids, stride, pad_value)
    patches = itertools.islice(patch_generator, len(centroids))
    return list(patches)
