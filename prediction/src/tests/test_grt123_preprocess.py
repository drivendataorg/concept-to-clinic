import warnings
import SimpleITK as sitk
import numpy as np

from scipy.ndimage import zoom
from src.preprocess import load_ct, preprocess_ct, crop_patches

"""
Preprocessing tools used by the gtr123_models
Code adapted from https://github.com/lfz/DSB2017
"""


class SimpleCrop(object):
    """ """

    def __init__(self):
        self.crop_size = [96, 96, 96]
        self.scaleLim = [0.85, 1.15]
        self.radiusLim = [6, 100]
        self.stride = 4
        self.filling_value = 160

    def __call__(self, imgs, target):
        crop_size = np.array(self.crop_size).astype('int')

        start = (target[:3] - crop_size / 2).astype('int')
        pad = [[0, 0]]

        for i in range(3):
            if start[i] < 0:
                leftpad = -start[i]
                start[i] = 0
            else:
                leftpad = 0
            if start[i] + crop_size[i] > imgs.shape[i + 1]:
                rightpad = start[i] + crop_size[i] - imgs.shape[i + 1]
            else:
                rightpad = 0

            pad.append([leftpad, rightpad])

        imgs = np.pad(imgs, pad, 'constant', constant_values=self.filling_value)
        crop = imgs[:, start[0]:start[0] + crop_size[0], start[1]:start[1] + crop_size[1],
                    start[2]:start[2] + crop_size[2]]
        normstart = np.array(start).astype('float32') / np.array(imgs.shape[1:]) - 0.5
        normsize = np.array(crop_size).astype('float32') / np.array(imgs.shape[1:])
        xx, yy, zz = np.meshgrid(np.linspace(normstart[0],
                                             normstart[0] + normsize[0],
                                             self.crop_size[0] // self.stride),
                                 np.linspace(normstart[1],
                                             normstart[1] + normsize[1],
                                             self.crop_size[1] // self.stride),
                                 np.linspace(normstart[2],
                                             normstart[2] + normsize[2],
                                             self.crop_size[2] // self.stride),
                                 indexing='ij')
        coord = np.concatenate([xx[np.newaxis, ...], yy[np.newaxis, ...], zz[np.newaxis, :]], 0).astype('float32')

        return crop, coord


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


def test_lum_trans(metaimage_path):
    ct_array, meta = load_ct.load_ct(metaimage_path)
    lumed = lum_trans(ct_array)
    functional = preprocess_ct.PreprocessCT(clip_lower=-1200., clip_upper=600.,
                                            min_max_normalize=True, scale=255, dtype='uint8')

    processed, _ = functional(ct_array, meta)
    assert np.abs(lumed - processed).sum() == 0


def test_resample(metaimage_path):
    ct_array, meta = load_ct.load_ct(metaimage_path)
    resampled, _ = resample(ct_array, np.array(load_ct.MetaData(meta).spacing), np.array([1, 1, 1]), order=1)
    preprocess = preprocess_ct.PreprocessCT(spacing=1., order=1)
    processed, _ = preprocess(ct_array, meta)
    assert np.abs(resampled - processed).sum() == 0


def test_preprocess(metaimage_path):
    nodule_list = [{"z": 556, "y": 100, "x": 0}]
    image_itk = sitk.ReadImage(metaimage_path)

    image = sitk.GetArrayFromImage(image_itk)
    spacing = np.array(image_itk.GetSpacing())[::-1]
    origin = np.array(image_itk.GetOrigin())[::-1]
    image = lum_trans(image)
    image = resample(image, spacing, np.array([1, 1, 1]), order=1)[0]

    crop = SimpleCrop()

    for nodule in nodule_list:
        nod_location = np.array([np.float32(nodule[s]) for s in ["z", "y", "x"]])
        nod_location = np.ceil((nod_location - origin) / 1.)
        cropped_image, coords = crop(image[np.newaxis], nod_location)

    # New style
    ct_array, meta = load_ct.load_ct(metaimage_path)

    preprocess = preprocess_ct.PreprocessCT(clip_lower=-1200., clip_upper=600.,
                                            min_max_normalize=True, scale=255, dtype='uint8')

    ct_array, meta = preprocess(ct_array, meta)
    preprocess = preprocess_ct.PreprocessCT(spacing=1., order=1)
    ct_array, meta = preprocess(ct_array, meta)

    cropped_image_new, coords_new = crop_patches.patches_from_ct(ct_array, meta, 96, nodule_list,
                                                                 stride=4, pad_value=160)[0]

    assert np.abs(cropped_image_new - cropped_image).sum() == 0
    assert np.abs(coords_new - coords).sum() == 0
