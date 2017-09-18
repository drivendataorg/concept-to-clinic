"""
Based on the https://github.com/fchollet/keras/blob/master/keras/preprocessing/image.py

Fairly basic set of tools for real-time data augmentation on the volumetric data.
Extended for 3D objects augmentation.
"""
import os
import threading
import warnings

import keras.backend as K
import numpy as np
import scipy.ndimage
from keras.utils.data_utils import Sequence
from scipy import linalg
from six.moves import range


def random_rotation(x, rgs, channel_axis=0,
                    fill_mode='nearest', cval=0., order=0):
    """Performs a random rotation of a Numpy image tensor.

    # Arguments
        x: Input tensor. Must be 4D.
        rg: Rotation range, in degrees.
        channel_axis: Index of axis for channels in the input tensor.
        fill_mode: Points outside the boundaries of the input
            are filled according to the given mode
            (one of `{'constant', 'nearest', 'reflect', 'wrap'}`).
        cval: Value used for points outside the boundaries
            of the input if `mode='constant'`.

    # Returns
        Rotated Numpy image tensor.
    """
    rgs = scipy.ndimage._ni_support._normalize_sequence(rgs, 3)
    theta = [np.random.uniform(-rg, rg) * np.pi / 180. for rg in rgs]

    rotation_matrix_x = np.array([[1, 0, 0, 0],
                                  [0, np.cos(theta[0]), -np.sin(theta[0]), 0],
                                  [0, np.sin(theta[0]), np.cos(theta[0]), 0],
                                  [0, 0, 0, 1]])

    rotation_matrix_y = np.array([[np.cos(theta[1]), 0, np.sin(theta[1]), 0],
                                  [0, 1, 0, 0],
                                  [-np.sin(theta[1]), 0, np.cos(theta[1]), 0],
                                  [0, 0, 0, 1]])

    rotation_matrix_z = np.array([[np.cos(theta[2]), -np.sin(theta[2]), 0, 0],
                                  [np.sin(theta[2]), np.cos(theta[2]), 0, 0],
                                  [0, 0, 1, 0],
                                  [0, 0, 0, 1]])

    transform_matrix = np.dot(rotation_matrix_x, np.dot(rotation_matrix_y, rotation_matrix_z))
    axes = [i for i in range(len(x.shape)) if i != channel_axis]
    sides = [x.shape[i] for i in axes]
    transform_matrix = transform_matrix_offset_center(transform_matrix, sides)
    x = apply_transform(x, transform_matrix, channel_axis, fill_mode, cval, order)
    return x


def random_shift(x, rgs, channel_axis=0,
                 fill_mode='nearest', cval=0.):
    """Performs a random spatial shift of a Numpy image tensor.

    # Arguments
        x: Input tensor. Must be 4D.
        rgs: shift range, as a float fraction of the size.
        channel_axis: Index of axis for channels in the input tensor.
        fill_mode: Points outside the boundaries of the input
            are filled according to the given mode
            (one of `{'constant', 'nearest', 'reflect', 'wrap'}`).
        cval: Value used for points outside the boundaries
            of the input if `mode='constant'`.

    # Returns
        Shifted Numpy image tensor.
    """
    rgs = scipy.ndimage._ni_support._normalize_sequence(rgs, 3)
    axes = [i for i in range(4) if i != channel_axis]
    sides = [x.shape[i] for i in axes]
    translations = [np.random.uniform(-rg, rg) * side for rg, side in zip(rgs, sides)]
    translation_matrix = np.array([[1, 0, 0, translations[0]],
                                   [0, 1, 0, translations[1]],
                                   [0, 0, 1, translations[2]],
                                   [0, 0, 0, 1]])

    x = apply_transform(x, translation_matrix, channel_axis, fill_mode, cval)
    return x


def random_shear(x, intensity, channel_axis=0,
                 fill_mode='nearest', cval=0.):
    """Performs a random spatial shear of a Numpy image tensor.

    # Arguments
        x: Input tensor. Must be 4D.
        intensity: Transformation intensity.
        channel_axis: Index of axis for channels in the input tensor.
        fill_mode: Points outside the boundaries of the input
            are filled according to the given mode
            (one of `{'constant', 'nearest', 'reflect', 'wrap'}`).
        cval: Value used for points outside the boundaries
            of the input if `mode='constant'`.

    # Returns
        Sheared Numpy image tensor.
    """
    rgs = scipy.ndimage._ni_support._normalize_sequence(intensity, 3)
    shear = [np.random.uniform(-rg, rg) * np.pi / 180 for rg in rgs]
    shear_matrix = np.array([[1, -np.sin(shear[0]), np.cos(shear[1]), 0],
                             [np.cos(shear[0]), 1, -np.sin(shear[2]), 0],
                             [-np.sin(shear[1]), np.cos(shear[2]), 1, 0],
                             [0, 0, 0, 1]])

    axes = [i for i in range(4) if i != channel_axis]
    sides = [x.shape[i] for i in axes]
    transform_matrix = transform_matrix_offset_center(shear_matrix, sides)
    x = apply_transform(x, transform_matrix, channel_axis, fill_mode, cval)
    return x


def random_zoom(x, zoom_lower, zoom_upper, independent, channel_axis=0,
                fill_mode='nearest', cval=0.):
    """Performs a random spatial zoom of a Numpy image tensor.

    # Arguments
        x: Input tensor. Must be 4D.
        zoom_lower: Float or Tuple of floats; zoom range lower bound.
            If scalar, then the same lower bound value will be set
            for each axis.
        zoom_upper: Float or Tuple of floats; zoom range upper bound.
            If scalar, then the same upper bound value will be set
            for each axis.
        independent: Boolean, whether to zoom each axis independently
            or with the same convex-combination coefficient `fctr`, ranged
            from 0 up to 1, so thar  `fctr` * lower + (1 - `fctr`) * upper.
        channel_axis: Index of axis for channels in the input tensor.
        fill_mode: Points outside the boundaries of the input
            are filled according to the given mode
            (one of `{'constant', 'nearest', 'reflect', 'wrap'}`).
        cval: Value used for points outside the boundaries
            of the input if `mode='constant'`.

    # Returns
        Zoomed Numpy image tensor.

    # Raises
        ValueError: if `zoom_range` isn't a tuple.
    """
    axes = [i for i in range(4) if i != channel_axis]
    zoom_lower = scipy.ndimage._ni_support._normalize_sequence(zoom_lower, len(axes))
    zoom_upper = scipy.ndimage._ni_support._normalize_sequence(zoom_upper, len(axes))

    if independent:
        zoom_fctr = [np.random.uniform(l, u) for l, u in zip(zoom_lower, zoom_upper)]
    else:
        fctr = np.random.uniform(0, 1)
        zoom_fctr = [fctr * l + (1 - fctr) * u for l, u in zip(zoom_lower, zoom_upper)]

    zoom_fctr = [1. / zf for zf in zoom_fctr]
    zoom_matrix = np.array([[zoom_fctr[0], 0, 0, 0],
                            [0, zoom_fctr[1], 0, 0],
                            [0, 0, zoom_fctr[2], 0],
                            [0, 0, 0, 1]])

    sides = [x.shape[i] for i in axes]
    transform_matrix = transform_matrix_offset_center(zoom_matrix, sides)
    x = apply_transform(x, transform_matrix, channel_axis, fill_mode, cval)
    return x


def random_channel_shift(x, intensity, channel_axis=0):
    x = np.rollaxis(x, channel_axis, 0)
    min_x, max_x = np.min(x), np.max(x)
    channel_images = [np.clip(x_channel + np.random.uniform(-intensity, intensity), min_x, max_x)
                      for x_channel in x]
    x = np.stack(channel_images, axis=0)
    x = np.rollaxis(x, 0, channel_axis + 1)
    return x


def transform_matrix_offset_center(matrix, sides):
    sides = [float(side) / 2 - 0.5 for side in sides]
    offset_matrix = np.array([[1, 0, 0, sides[0]], [0, 1, 0, sides[1]], [0, 0, 1, sides[2]], [0, 0, 0, 1]])
    reset_matrix = np.array([[1, 0, 0, -sides[0]], [0, 1, 0, -sides[1]], [0, 0, 1, -sides[2]], [0, 0, 0, 1]])
    transform_matrix = np.dot(np.dot(offset_matrix, matrix), reset_matrix)
    return transform_matrix


def apply_transform(x, transform_matrix,
                    channel_axis=0,
                    fill_mode='nearest',
                    cval=0., order=0):
    """Apply the image transformation specified by a matrix.

    # Arguments
        x: 4D numpy array, single patch.
        transform_matrix: Numpy array specifying the geometric transformation.
        channel_axis: Index of axis for channels in the input tensor.
        fill_mode: Points outside the boundaries of the input
            are filled according to the given mode
            (one of `{'constant', 'nearest', 'reflect', 'wrap'}`).
        cval: Value used for points outside the boundaries
            of the input if `mode='constant'`.

    # Returns
        The transformed version of the input.
    """
    x = np.rollaxis(x, channel_axis, 0)
    final_affine_matrix = transform_matrix[:3, :3]
    final_offset = transform_matrix[:3, 3]
    channel_images = [scipy.ndimage.interpolation.affine_transform(
        x_channel,
        final_affine_matrix,
        final_offset,
        order=order,
        mode=fill_mode,
        cval=cval) for x_channel in x]
    x = np.stack(channel_images, axis=0)
    x = np.rollaxis(x, 0, channel_axis + 1)
    return x


def flip_axis(x, axis):
    x = np.asarray(x).swapaxes(axis, 0)
    x = x[::-1, ...]
    x = x.swapaxes(0, axis)
    return x


class DataGenerator(object):
    """Generate minibatches of image data with real-time data augmentation.

    # Arguments
        featurewise_center: set input mean to 0 over the dataset.
        samplewise_center: set each sample mean to 0.
        featurewise_std_normalization: divide inputs by std of the dataset.
        samplewise_std_normalization: divide each input by its std.
        zca_whitening: apply ZCA whitening.
        zca_epsilon: epsilon for ZCA whitening. Default is 1e-6.
        rotation_range: degrees (0 to 180), if scalar, then the same for each axis.
        shift_range: fraction of total length of the axes, if scalar, then the same for each axis.
        shear_range: shear intensity (shear angle in radians).
        zoom_lower: Float or Tuple of floats; zoom range lower bound.
            If scalar, then the same lower bound value will be set
            for each axis.
        zoom_upper: Float or Tuple of floats; zoom range upper bound.
            If scalar, then the same upper bound value will be set
            for each axis.
        zoom_independent: Boolean, whether to zoom each axis independently
            or with the same convex-combination coefficient `fctr`, ranged
            from 0 up to 1, so thar  `fctr` * lower + (1 - `fctr`) * upper.
        channel_shift_range: shift range for each channel.
        fill_mode: points outside the boundaries are filled according to the
            given mode ('constant', 'nearest', 'reflect' or 'wrap'). Default
            is 'nearest'.
        cval: value used for points outside the boundaries when fill_mode is
            'constant'. Default is 0.
        flip_axes: whether to randomly flip images through the axis from flip_axes.
        rescale: rescaling factor. If None or 0, no rescaling is applied,
            otherwise we multiply the data by the value provided. This is
            applied after the `preprocessing_function` (if any provided)
            but before any other transformation.
        preprocessing_function: function that will be implied on each input.
            The function will run before any other modification on it.
            The function should take one argument:
            one image (Numpy tensor with rank 3),
            and should output a Numpy tensor with the same shape.
        data_format: 'channels_first' or 'channels_last'. In 'channels_first' mode, the channels dimension
            (the depth) is at index 1, in 'channels_last' mode it is at index 3.
            It defaults to the `image_data_format` value found in your
            Keras config file at `~/.keras/keras.json`.
            If you never set it, then it will be "channels_last".
    """

    def __init__(self,
                 featurewise_center=False,
                 samplewise_center=False,
                 featurewise_std_normalization=False,
                 samplewise_std_normalization=False,
                 zca_whitening=False,
                 zca_epsilon=1e-6,
                 rotation_range=0.,
                 shift_range=0.,
                 shear_range=0.,
                 zoom_lower=0.,
                 zoom_upper=0.,
                 zoom_independent=True,
                 channel_shift_range=0.,
                 fill_mode='nearest',
                 cval=0.,
                 flip_axes=None,
                 rescale=None,
                 preprocessing_function=None,
                 data_format=None):
        if data_format is None:
            data_format = K.image_data_format()
        self.featurewise_center = featurewise_center
        self.samplewise_center = samplewise_center
        self.featurewise_std_normalization = featurewise_std_normalization
        self.samplewise_std_normalization = samplewise_std_normalization
        self.zca_whitening = zca_whitening
        self.zca_epsilon = zca_epsilon
        self.rotation_range = rotation_range
        self.shift_range = shift_range
        self.shear_range = shear_range
        self.zoom_lower = zoom_lower
        self.zoom_upper = zoom_upper
        self.zoom_independent = zoom_independent
        self.channel_shift_range = channel_shift_range
        self.fill_mode = fill_mode
        self.cval = cval
        self.flip_axis = flip_axes
        self.rescale = rescale
        self.preprocessing_function = preprocessing_function

        if data_format not in {'channels_last', 'channels_first'}:
            raise ValueError('`data_format` should be `"channels_last"` (channel after row and '
                             'column) or `"channels_first"` (channel before row and column). '
                             'Received arg: ', data_format)
        self.data_format = data_format
        if self.data_format is None:
            self.data_format = K.image_data_format()
        if data_format == 'channels_first':
            self.channel_axis = 1
        if data_format == 'channels_last':
            self.channel_axis = 4

        self.mean = None
        self.std = None
        self.principal_components = None

        self.axes = [i for i in range(4) if i != self.channel_axis - 1]
        if self.rotation_range:
            self.rotation_range = scipy.ndimage._ni_support._normalize_sequence(self.rotation_range, 3)

        if self.shift_range:
            self.shift_range = scipy.ndimage._ni_support._normalize_sequence(self.shift_range, 3)

        if self.shear_range:
            self.shear_range = scipy.ndimage._ni_support._normalize_sequence(self.shear_range, 3)

        if self.zoom_lower and self.zoom_upper:
            self.zoom_lower = scipy.ndimage._ni_support._normalize_sequence(zoom_lower, len(self.axes))
            self.zoom_upper = scipy.ndimage._ni_support._normalize_sequence(zoom_upper, len(self.axes))

    def flow(self, x, y=None, batch_size=32, shuffle=True, seed=None,
             save_to_dir=None, save_prefix=''):
        return NumpyArrayIterator(
            x, y, self,
            batch_size=batch_size,
            shuffle=shuffle,
            seed=seed,
            data_format=self.data_format,
            save_to_dir=save_to_dir,
            save_prefix=save_prefix)

    def standardize(self, x):  # noqa: C901
        """Apply the normalization configuration to a batch of inputs.

        # Arguments
            x: batch of inputs to be normalized.

        # Returns
            The inputs, normalized.
        """
        if self.preprocessing_function:
            x = self.preprocessing_function(x)
        if self.rescale:
            x *= self.rescale
        # x is a single patch, so it doesn't have image number at index 0
        img_channel_axis = self.channel_axis - 1
        if self.samplewise_center:
            x -= np.mean(x, axis=img_channel_axis, keepdims=True)
        if self.samplewise_std_normalization:
            x /= (np.std(x, axis=img_channel_axis, keepdims=True) + 1e-7)

        if self.featurewise_center:
            if self.mean is not None:
                x -= self.mean
            else:
                warnings.warn('This ImageDataGenerator specifies '
                              '`featurewise_center`, but it hasn\'t'
                              'been fit on any training data. Fit it '
                              'first by calling `.fit(numpy_data)`.')
        if self.featurewise_std_normalization:
            if self.std is not None:
                x /= (self.std + 1e-7)
            else:
                warnings.warn('This ImageDataGenerator specifies '
                              '`featurewise_std_normalization`, but it hasn\'t'
                              'been fit on any training data. Fit it '
                              'first by calling `.fit(numpy_data)`.')
        if self.zca_whitening:
            if self.principal_components is not None:
                flatx = np.reshape(x, (-1, np.prod(x.shape[-3:])))
                whitex = np.dot(flatx, self.principal_components)
                x = np.reshape(whitex, x.shape)
            else:
                warnings.warn('This ImageDataGenerator specifies '
                              '`zca_whitening`, but it hasn\'t'
                              'been fit on any training data. Fit it '
                              'first by calling `.fit(numpy_data)`.')
        return x

    def random_transform(self, x, seed=None):  # noqa: C901
        """Randomly augment a single image tensor.

        # Arguments
            x: 4D tensor, single patch.
            seed: random seed.

        # Returns
            A randomly transformed version of the input (same shape).
        """
        # x is a single image, so it doesn't have image number at index 0
        channel_axis = self.channel_axis - 1
        sides = [x.shape[i] for i in self.axes]

        if seed is not None:
            np.random.seed(seed)

        # use composition of homographies
        # to generate final transform that needs to be applied
        if self.rotation_range:
            theta = [np.random.uniform(-rg, rg) * np.pi / 180 for rg in self.rotation_range]
        else:
            theta = 0

        if self.shift_range:
            shift = [np.random.uniform(-rg, rg) * side for rg, side in zip(self.shift_range, sides)]
        else:
            shift = 0

        if self.shear_range:
            shear = [np.random.uniform(-rg, rg) * np.pi / 180 for rg in self.shear_range]
        else:
            shear = 0

        if self.zoom_lower and self.zoom_upper:
            if self.zoom_independent:
                zoom_fctr = [np.random.uniform(l, u) for l, u in zip(self.zoom_lower, self.zoom_upper)]
            else:
                fctr = np.random.uniform(0, 1)
                zoom_fctr = [fctr * l + (1 - fctr) * u for l, u in zip(self.zoom_lower, self.zoom_upper)]
            zoom_fctr = [1. / zf for zf in zoom_fctr]
        else:
            zoom_fctr = 0

        transform_matrix = None
        if theta != 0:
            rotation_matrix_x = np.array([[1, 0, 0, 0],
                                          [0, np.cos(theta[0]), -np.sin(theta[0]), 0],
                                          [0, np.sin(theta[0]), np.cos(theta[0]), 0],
                                          [0, 0, 0, 1]])

            rotation_matrix_y = np.array([[np.cos(theta[1]), 0, np.sin(theta[1]), 0],
                                          [0, 1, 0, 0],
                                          [-np.sin(theta[1]), 0, np.cos(theta[1]), 0],
                                          [0, 0, 0, 1]])

            rotation_matrix_z = np.array([[np.cos(theta[2]), -np.sin(theta[2]), 0, 0],
                                          [np.sin(theta[2]), np.cos(theta[2]), 0, 0],
                                          [0, 0, 1, 0],
                                          [0, 0, 0, 1]])
            transform_matrix = np.dot(rotation_matrix_x, np.dot(rotation_matrix_y, rotation_matrix_z))

        if shift != 0:
            shift_matrix = np.array([[1, 0, 0, shift[0]],
                                     [0, 1, 0, shift[1]],
                                     [0, 0, 1, shift[2]],
                                     [0, 0, 0, 1]])
            transform_matrix = shift_matrix if transform_matrix is None else np.dot(transform_matrix, shift_matrix)

        if shear != 0:
            shear_matrix = np.array([[1, -np.sin(shear[0]), np.cos(shear[1]), 0],
                                     [np.cos(shear[0]), 1, -np.sin(shear[2]), 0],
                                     [-np.sin(shear[1]), np.cos(shear[2]), 1, 0],
                                     [0, 0, 0, 1]])

            transform_matrix = shear_matrix if transform_matrix is None else np.dot(transform_matrix, shear_matrix)

        if zoom_fctr != 0:
            zoom_matrix = np.array([[zoom_fctr[0], 0, 0, 0],
                                    [0, zoom_fctr[1], 0, 0],
                                    [0, 0, zoom_fctr[2], 0],
                                    [0, 0, 0, 1]])
            transform_matrix = zoom_matrix if transform_matrix is None else np.dot(transform_matrix, zoom_matrix)

        if transform_matrix is not None:
            axes = [i for i in range(4) if i != channel_axis]
            sides = [x.shape[i] for i in axes]
            transform_matrix = transform_matrix_offset_center(transform_matrix, sides)
            x = apply_transform(x, transform_matrix, channel_axis,
                                fill_mode=self.fill_mode, cval=self.cval)

        if self.channel_shift_range != 0:
            x = random_channel_shift(x, self.channel_shift_range, channel_axis)
        if self.flip_axis is not None:
            for axis in self.flip_axis:
                if np.random.random() < .5:
                    x = flip_axis(x, axis)
        return x

    def fit(self, x, augment=False, rounds=1, seed=None):
        """Fits internal statistics to some sample data.

        Required for featurewise_center, featurewise_std_normalization
        and zca_whitening.

        # Arguments
            x: Numpy array, the data to fit on. Should have rank 5.
                In case of grayscale data,
                the channels axis should have value 1, and in case
                of RGB data, it should have value 3.
            augment: Whether to fit on randomly augmented samples
            rounds: If `augment`,
                how many augmentation passes to do over the data
            seed: random seed.

        # Raises
            ValueError: in case of invalid input `x`.
        """
        x = np.asarray(x, dtype=K.floatx())
        if x.ndim != 5:
            raise ValueError('Input to `.fit()` should have rank 5. '
                             'Got array with shape: ' + str(x.shape))

        if seed is not None:
            np.random.seed(seed)

        x = np.copy(x)
        if augment:
            ax = np.zeros(tuple([rounds * x.shape[0]] + list(x.shape)[1:]), dtype=K.floatx())
            for r in range(rounds):
                for i in range(x.shape[0]):
                    ax[i + r * x.shape[0]] = self.random_transform(x[i])
            x = ax

        axis = tuple(i for i in range(len(x.shape)) if i != self.channel_axis)
        if self.featurewise_center:
            self.mean = np.mean(x, axis=axis)
            broadcast_shape = [1, 1, 1, 1]
            broadcast_shape[self.channel_axis - 1] = x.shape[self.channel_axis]
            self.mean = np.reshape(self.mean, broadcast_shape)
            x -= self.mean

        if self.featurewise_std_normalization:
            self.std = np.std(x, axis=axis)
            broadcast_shape = [1, 1, 1, 1]
            broadcast_shape[self.channel_axis - 1] = x.shape[self.channel_axis]
            self.std = np.reshape(self.std, broadcast_shape)
            x /= (self.std + K.epsilon())

        if self.zca_whitening:
            flat_x = np.reshape(x, (x.shape[0], -1))
            sigma = np.dot(flat_x.T, flat_x) / flat_x.shape[0]
            u, s, _ = linalg.svd(sigma)
            self.principal_components = np.dot(np.dot(u, np.diag(1. / np.sqrt(s + self.zca_epsilon))), u.T)


class Iterator(Sequence):
    """Abstract base class for image data iterators.

    # Arguments
        n: Integer, total number of samples in the dataset to loop over.
        batch_size: Integer, size of a batch.
        shuffle: Boolean, whether to shuffle the data between epochs.
        seed: Random seeding for data shuffling.
    """

    def __init__(self, n, batch_size, shuffle, seed):
        self.n = n
        self.batch_size = batch_size
        self.seed = seed
        self.shuffle = shuffle
        self.batch_index = 0
        self.total_batches_seen = 0
        self.lock = threading.Lock()
        self.index_array = None
        self.index_generator = self._flow_index()

    def _set_index_array(self):
        self.index_array = np.arange(self.n)
        if self.shuffle:
            self.index_array = np.random.permutation(self.n)

    def __getitem__(self, idx):
        if idx >= len(self):
            raise ValueError('Asked to retrieve element {idx}, '
                             'but the Sequence '
                             'has length {length}'.format(idx=idx,
                                                          length=len(self)))
        if self.seed is not None:
            np.random.seed(self.seed + self.total_batches_seen)
        self.total_batches_seen += 1
        if self.index_array is None:
            self._set_index_array()
        index_array = self.index_array[self.batch_size * idx: self.batch_size * (idx + 1)]
        return self._get_batches_of_transformed_samples(index_array)

    def __len__(self):
        return int(np.ceil(self.n / float(self.batch_size)))

    def on_epoch_end(self):
        self._set_index_array()

    def reset(self):
        self.batch_index = 0

    def _flow_index(self):
        # Ensure self.batch_index is 0.
        self.reset()
        while 1:
            if self.seed is not None:
                np.random.seed(self.seed + self.total_batches_seen)
            if self.batch_index == 0:
                self._set_index_array()

            current_index = (self.batch_index * self.batch_size) % self.n
            if self.n > current_index + self.batch_size:
                self.batch_index += 1
            else:
                self.batch_index = 0
            self.total_batches_seen += 1
            yield self.index_array[current_index: current_index + self.batch_size]

    def __iter__(self):
        # Needed if we want to do something like:
        # for x, y in data_gen.flow(...):
        return self

    def __next__(self, *args, **kwargs):
        return self.next(*args, **kwargs)


class NumpyArrayIterator(Iterator):
    """Iterator yielding data from a Numpy array.

    # Arguments
        x: Numpy array of input data.
        y: Numpy array of targets data.
        image_data_generator: Instance of `ImageDataGenerator`
            to use for random transformations and normalization.
        batch_size: Integer, size of a batch.
        shuffle: Boolean, whether to shuffle the data between epochs.
        seed: Random seed for data shuffling.
        data_format: String, one of `channels_first`, `channels_last`.
        save_to_dir: Optional directory where to save the pictures
            being yielded, in a viewable format. This is useful
            for visualizing the random transformations being
            applied, for debugging purposes.
        save_prefix: String prefix to use for saving sample
            images (if `save_to_dir` is set).
        save_format: Format to use for saving sample images
            (if `save_to_dir` is set).
    """

    def __init__(self, x, y, image_data_generator,
                 batch_size=32, shuffle=False, seed=None,
                 data_format=None,
                 save_to_dir=None, save_prefix=''):
        if y is not None and len(x) != len(y):
            raise ValueError('X (images tensor) and y (labels) '
                             'should have the same length. '
                             'Found: X.shape = %s, y.shape = %s' %
                             (np.asarray(x).shape, np.asarray(y).shape))

        if data_format is None:
            data_format = K.image_data_format()
        self.x = np.asarray(x, dtype=K.floatx())

        if self.x.ndim != 5:
            raise ValueError('Input data in `NumpyArrayIterator` '
                             'should have rank 5. You passed an array '
                             'with shape', self.x.shape)
        self.channels_axis = 3 if data_format == 'channels_last' else 1

        if y is not None:
            self.y = np.asarray(y)
        else:
            self.y = None
        self.image_data_generator = image_data_generator
        self.data_format = data_format
        self.save_to_dir = save_to_dir
        self.save_prefix = save_prefix
        super(NumpyArrayIterator, self).__init__(x.shape[0], batch_size, shuffle, seed)

    def _get_batches_of_transformed_samples(self, index_array):
        batch_x = np.zeros(tuple([len(index_array)] + list(self.x.shape)[1:]),
                           dtype=K.floatx())
        for i, j in enumerate(index_array):
            x = self.x[j]
            x = self.image_data_generator.random_transform(x.astype(K.floatx()))
            x = self.image_data_generator.standardize(x)
            batch_x[i] = x
        if self.save_to_dir:
            for i, j in enumerate(index_array):
                fname = '{prefix}_{index}_{hash}'.format(prefix=self.save_prefix,
                                                         index=j,
                                                         hash=np.random.randint(1e4))
                np.save(os.path.join(self.save_to_dir, fname), batch_x[i])
        if self.y is None:
            return batch_x
        batch_y = self.y[index_array]
        return batch_x, batch_y

    def next(self):
        """For python 2.x.

        # Returns
            The next batch.
        """
        # Keeps under lock only the mechanism which advances
        # the indexing of each batch.
        with self.lock:
            index_array = next(self.index_generator)
        # The transformation of images is not under thread lock
        # so it can be done in parallel
        return self._get_batches_of_transformed_samples(index_array)
