import numpy as np
import scipy.ndimage


class Params:
    """Params for DICOM data preprocessing.

    To enshure parametrs integrity for a preprocessing class.

    Args:
        clip_lower (int | float): clip the voxels' value to be greater or equal to clip_lower.
            If None is set, then no lower bound will applied.
        clip_upper (int | float): clip the voxels' value to be less or equal to clip_upper. 
            If None is set, then no upper bound will applied.   
        voxel_shape (float | sequence[float]): The voxel size along the axes. 
            If a float, `voxel_shape` is the same for each axis. 
            If a sequence, `voxel_shape` should contain one value for each axis.
        min_max_normalize (bool): If True, use min_max magnitude normalization. 
            So that the voxels' values will lie inside [0, 1].

    Returns:
        preprocess.preprocess_dicom.Params
    """

    def __init__ (self, clip_lower=None, clip_upper=None, 
                  voxel_shape=None, ndim=3, min_max_normalize=False): 
        if not isinstance(clip_lower, (int, float)) and (clip_lower is not None):
            raise ValueError('The clip_lower should be int or float')
        if not isinstance(clip_upper, (int, float)) and (clip_upper is not None):
            raise ValueError('The clip_upper should be int or float')
        if (clip_lower is not None) and (clip_upper is not None):
            if clip_lower > clip_upper:
                raise ValueError('The clip_upper should be grater or equal to clip_lower')
        self.clip_lower = clip_lower
        self.clip_upper = clip_upper 

        if not isinstance(ndim, int):
            raise ValueError('The ndim should be int')
        if ndim <= 0:
            raise ValueError('The ndim should be greater than 0')
        self.ndim = ndim 

        self.voxel_shape = None
        if voxel_shape is not None:
            self.voxel_shape = scipy.ndimage._ni_support._normalize_sequence(voxel_shape, 
                                                                             self.ndim)

        if not isinstance(min_max_normalize, (bool, int)) and (min_max_normalize is not None):
            raise ValueError('The min_max_normalize should be bool or int')
        self.min_max_normalize = min_max_normalize


class PreprocessDicom:
    """Preprocess the DICOM data.

    To enshure parametrs integrity for a preprocessing function.

    Args:
        clip_lower (int | float): clip the voxels' value to be grater or equal to clip_lower.
            If None is set, then no lower bound will applied.
        clip_upper (int | float): clip the voxels' value to be less or equal to clip_upper. 
            If None is set, then no upper bound will applied.   
        voxel_shape (float | sequence[float]): The voxel size along the axes. 
            If a float, `voxel_shape` is the same for each axis. 
            If a sequence, `voxel_shape` should contain one value for each axis.
        min_max_normalize (bool): If True, use min_max magnitude normalization. 
            So that the voxels' values will lie inside [0, 1].

    Returns:
        preprocess.preprocess_dicom.Params
    """


    def __init__(self, params=None):
        self.params = None
        if params is not None:
            if not isinstance(params, Params):
                raise ValueError('The params should be an instance of %s.' % str(Params))
        self.params = params


    def __call__(self, dicom_files, voxel_data):
        if (self.params is None) or not len(dicom_files):
            return voxel_data

        # Instead of np.clip usage in order to avoid np.max | np.min calculation in case of None
        if self.params.clip_lower is not None:
            voxel_data[voxel_data < self.params.clip_lower] = self.params.clip_lower
            
        if self.params.clip_upper is not None:
            voxel_data[voxel_data > self.params.clip_upper] = self.params.clip_upper

        if self.params.min_max_normalize:
            data_max = self.params.clip_upper
            data_min = self.params.clip_lower
            if data_max is None:
                data_max = voxel_data.max()
            if data_min is None:
                data_min = voxel_data.min()

            voxel_data = (voxel_data - data_min) / float(data_max - data_min) 

        if self.params.voxel_shape is not None:
            slice_locations = [dcm_file.SliceLocation for dcm_file in dicom_files]
            slice_thikness = np.diff(slice_locations).mean()
            # Every DICOM file have the same PixelSpacing
            current_shape = dicom_files[0].PixelSpacing
            # Taking into account ijk -> xyz transformation
            current_shape = np.asarray([current_shape[1], current_shape[0], slice_thikness])
            zoom_fctr = current_shape / np.asarray(self.params.voxel_shape)
            voxel_data = scipy.ndimage.interpolation.zoom(voxel_data, zoom_fctr)

        return voxel_data
