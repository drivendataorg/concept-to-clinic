import numpy as np
import warnings
from scipy.ndimage import zoom

"""
Preprocessing tools used by the gtr123_models
Code adapted from https://github.com/lfz/DSB2017
"""


def lum_trans(img):
    """

    Args:
      img:  Input image in Hu units

    Returns: Image windowed to [-1200; 600] and scaled to 0-255

    """
    lungwin = np.array([-1200., 600.])
    newimg = (img - lungwin[0]) / (lungwin[1] - lungwin[0])
    newimg[newimg < 0] = 0
    newimg[newimg > 1] = 1
    return (newimg * 255).astype('uint8')


def resample(imgs, spacing, new_spacing, order=2):
    """

    Args:
      imgs:
      spacing: Input image voxel size
      new_spacing: Output image voxel size
      order:  (Default value = 2)

    Returns:

    """
    if len(imgs.shape) == 3:
        new_shape = np.round(imgs.shape * spacing / new_spacing)
        true_spacing = spacing * imgs.shape / new_shape
        resize_factor = new_shape / imgs.shape

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            imgs = zoom(imgs, resize_factor, mode='nearest', order=order)

        return imgs, true_spacing
    elif len(imgs.shape) == 4:
        n = imgs.shape[-1]
        newimg = []

        for i in range(n):
            slice = imgs[:, :, :, i]
            newslice, true_spacing = resample(slice, spacing, new_spacing)
            newimg.append(newslice)

        newimg = np.transpose(np.array(newimg), [1, 2, 3, 0])
        return newimg, true_spacing
    else:
        raise ValueError('wrong shape')
