import itertools

import numpy as np
import scipy.ndimage


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
    coord = np.ceil(coord - np.array(origin)) / np.array(spacing)
    print(coord)
    print(origin)
    return coord.astype(np.int).tolist()


def crop_patch(ct_array, meta, patch_shape=None, centroids=None):
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

    Yields:
        np.ndarray: a cropped patch from the CT scan.
    """
    if centroids is None:
        centroids = []
    if patch_shape is None:
        patch_shape = []

    patch_shape = scipy.ndimage._ni_support._normalize_sequence(patch_shape, len(ct_array.shape))
    padding = np.ceil(np.array(patch_shape) / 2.).astype(np.int)
    padding = np.stack([padding, padding], axis=1)
    ct_array = np.pad(ct_array, padding, mode='edge')
    for centroid in centroids:
        centroid = mm2voxel([centroid[axis] for axis in 'zyx'], meta.origin, meta.spacing)
        yield ct_array[centroid[0]: centroid[0] + patch_shape[0],
                       centroid[1]: centroid[1] + patch_shape[1],
                       centroid[2]: centroid[2] + patch_shape[2]]


def patches_from_ct(ct_array, meta, patch_shape=None, centroids=None):
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

    Yields:
        np.ndarray: a cropped patch from the CT scan.
    """
    if patch_shape is None:
        patch_shape = []
    if centroids is None:
        centroids = []
    patch_generator = crop_patch(ct_array, meta, patch_shape, centroids)
    patches = itertools.islice(patch_generator, len(centroids))
    return list(patches)
