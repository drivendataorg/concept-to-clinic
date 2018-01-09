import warnings

import numpy as np
import scipy.ndimage

from . import load_ct


class Params:
    """Params for CT scan pre-processing.

    To ensure parameters integrity for a pre-processing class.

    Args:
        clip_lower (int | float): clip the voxels' value to be greater or equal to clip_lower.
            If None is set (default), then no lower bound will applied.
        clip_upper (int | float): clip the voxels' value to be less or equal to clip_upper.
            If None is set (default), then no upper bound will applied.
        spacing (boolean): If True, resample CT array according to the meta.spacing.
        order ({0, 1, 2, 3, 4}): the order of the spline interpolation used by re-sampling.
            The default value is 0.
        ndim (int): the dimension of CT array, should be greater than 1. The default value is 3.
        min_max_normalize (bool): If True, use min_max magnitude normalization.
            So that the voxels' values will lie inside [0, 1]. The default value is False.
        scale (float): the value by which will magnitude be scaled.
            If None is set (default), then no scaling will applied.
        dtype (str): the desired data-type of a returned array. Should be a valid key from `np.typeDict`
            If None is set (default), then no casting will applied.

    Returns:
        preprocess.preprocess_dicom.Params
    """

    def __init__(self, clip_lower=None, clip_upper=None, spacing=False, order=0,  # noqa: C901
                 ndim=3, min_max_normalize=False, scale=None, dtype=None, to_hu=False):
        if not isinstance(clip_lower, (int, float)) and (clip_lower is not None):
            raise TypeError('The clip_lower should be int or float')
        if not isinstance(clip_upper, (int, float)) and (clip_upper is not None):
            raise TypeError('The clip_upper should be int or float')
        if (clip_lower is not None) and (clip_upper is not None):
            if clip_lower > clip_upper:
                raise ValueError('The clip_upper should be grater or equal to clip_lower')
        self.clip_lower = clip_lower
        self.clip_upper = clip_upper

        if not isinstance(ndim, int):
            raise TypeError('The ndim should be int')
        if ndim <= 1:
            raise ValueError('The ndim should be greater than 0')
        self.ndim = ndim

        self.spacing = spacing

        if not isinstance(min_max_normalize, (bool, int)) and (min_max_normalize is not None):
            raise TypeError('The min_max_normalize should be bool or int')
        self.min_max_normalize = min_max_normalize

        if not isinstance(scale, (int, float)) and (scale is not None):
            raise TypeError('The scale should be float or int')
        self.scale = scale

        if not isinstance(order, int) or not (4 >= order >= 0):
            raise ValueError('The order should be int and lie in interval [0, 4]')
        self.order = order

        if dtype not in np.typeDict.keys() and (dtype is not None):
            raise ValueError('The dtype should be a valid key from `np.typeDict`')
        self.dtype = dtype

        if not isinstance(to_hu, (bool, int)) and (to_hu is not None):
            raise TypeError('The to_hu should be bool or int')
        self.to_hu = to_hu


class PreprocessCT(Params):
    """Pre-process the CT data.

    To ensure parameters integrity for a pre-processing function.

    Args:
        clip_lower (int | float): clip the voxels' value to be greater or equal to clip_lower.
            If None is set (default), then no lower bound will applied.
        clip_upper (int | float): clip the voxels' value to be less or equal to clip_upper.
            If None is set (default), then no upper bound will applied.
        spacing (float | sequence[float]): re-sample CT array in order to satisfy
            the desired spacing (voxel size along the axes).
            If a float, `voxel_shape` is the same for each axis.
            If a sequence, `voxel_shape` should contain one value for each axis.
            If None is set (default), then no re-sampling will applied.
        order ({0, 1, 2, 3, 4}): the order of the spline interpolation used by re-sampling.
            The default value is 0.
        ndim (int): the dimension of CT array, should be greater than 1. The default value is 3.
        min_max_normalize (bool): If True, use min_max magnitude normalization.
            So that the voxels' values will lie inside [0, 1].
        scale (float): the value by which will magnitude be scaled.
            If None is set (default), then no scaling will applied.
        dtype (str): the desired data-type of a returned array. Should be from `np.typeDict.keys()`
            If None is set (default), then no casting will applied.

    Returns:
        preprocess.preprocess_dicom.PreprocessCT
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __call__(self, voxel_data, meta):  # noqa: C901
        if not isinstance(meta, load_ct.MetaData):
            meta = load_ct.MetaData(meta)

        if self.to_hu:
            voxel_data[voxel_data == voxel_data[0, 0, 0]] = 0

            if meta.slope != 1:
                voxel_data = meta.slope * voxel_data.astype(np.float64)
                voxel_data = voxel_data.astype(np.int16)

            voxel_data += np.int16(meta.intercept)

        # Instead of np.clip usage in order to avoid np.max | np.min calculation in case of None
        if self.clip_lower is not None:
            voxel_data[voxel_data < self.clip_lower] = self.clip_lower
        if self.clip_upper is not None:
            voxel_data[voxel_data > self.clip_upper] = self.clip_upper

        if self.min_max_normalize:
            data_max = self.clip_upper
            data_min = self.clip_lower
            if data_max is None:
                data_max = voxel_data.max()
            if data_min is None:
                data_min = voxel_data.min()
            voxel_data = (voxel_data - data_min) / float(data_max - data_min)

        if self.scale is not None:
            voxel_data *= self.scale

        if self.spacing:
            zoom_fctr = meta.spacing / np.asarray(self.spacing)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                voxel_data = scipy.ndimage.interpolation.zoom(voxel_data, zoom_fctr, order=self.order)

        if self.dtype:
            voxel_data = voxel_data.astype(dtype=self.dtype, copy=False)

        return voxel_data, meta


def mm_coordinates_to_voxel(coord, meta):
    """ Transfer coordinates in mm into voxel's location

    Args:
        coord (scalar | list[scalar]): coordinates in mm.
        meta (src.preprocess.load_ct.MetaData): meta information of the CT scan.

    Returns:
        list[int]: the voxel location related to the coord.
    """

    if np.isscalar(coord):
        coord = [coord]

    coord = np.array(coord)
    origin = scipy.ndimage._ni_support._normalize_sequence(meta.origin, len(coord))
    spacing = scipy.ndimage._ni_support._normalize_sequence(meta.spacing, len(coord))
    coord = np.rint((coord - np.array(origin)) * np.array(spacing))

    return coord.astype(np.int)
