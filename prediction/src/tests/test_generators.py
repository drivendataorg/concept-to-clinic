import os
import warnings
import numpy as np
import scipy.ndimage

from src.preprocess import load_ct, generators


def test_generators_shift(ct_path):
    ct_array, meta = load_ct.load_ct(ct_path)
    patch = np.expand_dims(ct_array[45:90], 0)
    np.random.seed(1)
    translations = [-np.random.uniform(-rg, rg) * side for rg, side in zip([.1, .4, .4], patch.shape[1:])]
    shifted = scipy.ndimage.interpolation.shift(patch[0], translations, order=0, mode='nearest')

    np.random.seed(1)
    augmented = generators.random_shift(patch, (.1, .4, .4))
    assert len(augmented.shape) == 4
    assert augmented.shape == patch.shape
    assert not np.abs(shifted - augmented).sum()


def test_generators_rotate(ct_path):
    ct_array, meta = load_ct.load_ct(ct_path)
    patch = np.expand_dims(ct_array[45:90], 0)
    np.random.seed(1)
    theta = np.random.uniform(-45, 45)
    rotated = scipy.ndimage.rotate(patch[0], -theta, axes=(1, 2), order=0, mode='nearest', reshape=False)

    np.random.seed(1)
    augmented = generators.random_rotation(patch, (45, 0, 0))
    assert len(augmented.shape) == 4
    assert augmented.shape == patch.shape
    assert not np.abs(rotated - augmented).sum()


def test_generators_zoom(ct_path):
    ct_array, meta = load_ct.load_ct(ct_path)
    patch = np.expand_dims(ct_array[45:90], 0)
    zoomed = scipy.ndimage.interpolation.zoom(patch[0], [1, 1.2, 1.2], order=0, mode='nearest')
    augmented = generators.random_zoom(patch, [1, 1.2, 1.2], [1, 1.2, 1.2], True)
    offsets = [(i - j) for i, j in zip(zoomed.shape, patch[0].shape)]
    offsets = [[i // 2, j - (i - (i // 2))] for i, j in zip(offsets, zoomed.shape)]
    assert len(augmented.shape) == 4
    assert augmented.shape == patch.shape
    assert not np.abs(zoomed[offsets[0][0]: offsets[0][1],
                             offsets[1][0]: offsets[1][1],
                             offsets[2][0]: offsets[2][1]] - augmented).sum()


def test_generators_rotate_in_flow(ct_path):
    ct_array, meta = load_ct.load_ct(ct_path)
    batch = np.expand_dims(np.expand_dims(ct_array[45:90], 0), 0)
    dg = generators.DataGenerator(rotation_range=[45, 45, 45], data_format='channels_first')
    augmented = next(dg.flow(batch, batch_size=1, seed=21))
    assert len(augmented.shape) == 5
    assert augmented.shape == batch.shape

    np.random.seed(21)
    rotated = generators.random_rotation(batch[0], (45, 45, 45))
    assert not np.abs(rotated - augmented).sum()


def test_generators_shift_in_flow(ct_path):
    ct_array, meta = load_ct.load_ct(ct_path)
    batch = np.expand_dims(np.expand_dims(ct_array[45:90], 0), 0)
    dg = generators.DataGenerator(shift_range=[.1, .4, .4], data_format='channels_first')
    augmented = next(dg.flow(batch, batch_size=1, seed=21))
    assert len(augmented.shape) == 5
    assert augmented.shape == batch.shape

    np.random.seed(21)
    shifted = generators.random_shift(batch[0], (.1, .4, .4))
    assert not np.abs(shifted - augmented).sum()


def test_generators_zoom_in_flow(ct_path):
    ct_array, meta = load_ct.load_ct(ct_path)
    batch = np.expand_dims(np.expand_dims(ct_array[45:90], 0), 0)
    dg = generators.DataGenerator(zoom_lower=[1, .8, .8], zoom_upper=[1, 1.2, 1.2],
                                  zoom_independent=True, data_format='channels_first')
    augmented = next(dg.flow(batch, batch_size=1, seed=21))
    assert len(augmented.shape) == 5
    assert augmented.shape == batch.shape

    np.random.seed(21)
    zoomed = generators.random_zoom(batch[0], zoom_lower=[1, .8, .8], zoom_upper=[1, 1.2, 1.2], independent=True)
    assert not np.abs(zoomed - augmented).sum()


def test_generators_shear_in_flow(ct_path):
    ct_array, meta = load_ct.load_ct(ct_path)
    batch = np.expand_dims(np.expand_dims(ct_array[45:90], 0), 0)
    dg = generators.DataGenerator(shear_range=[10, 10, 10], data_format='channels_first')
    augmented = next(dg.flow(batch, batch_size=1, seed=21))
    assert len(augmented.shape) == 5
    assert augmented.shape == batch.shape

    np.random.seed(21)
    sheared = generators.random_shear(batch[0], (10, 10, 10))
    assert not np.abs(sheared - augmented).sum()


def test_generators_standardization(ct_path):
    ct_array, meta = load_ct.load_ct(ct_path)
    batch = np.expand_dims(np.expand_dims(ct_array[45:90], 0), 0)
    dg = generators.DataGenerator(featurewise_center=True,
                                  featurewise_std_normalization=True,
                                  samplewise_center=True,
                                  samplewise_std_normalization=True)

    with warnings.catch_warnings():
        warnings.filterwarnings('error')
        try:
            next(dg.flow(batch, batch_size=1))
        except Warning as w:
            assert "Fit it first by calling `.fit(numpy_data)`" in str(w)

    dg.fit(batch)
    normalized = next(dg.flow(batch, batch_size=1))
    assert len(normalized.shape) == 5
    assert normalized.shape == batch.shape


def test_generators_save_to_dir(ct_path, tmpdir):
    ct_array, meta = load_ct.load_ct(ct_path)
    batch = np.expand_dims(np.expand_dims(ct_array[45:90], 0), 0)
    dg = generators.DataGenerator()
    np.random.seed(1)
    save_prefix = 'test'
    fname = '{prefix}_{index}_{hash}.{format}'.format(prefix=save_prefix,
                                                      index=0,
                                                      hash=np.random.randint(1e4),
                                                      format='npy')

    fname = str(tmpdir.mkdir("processed").join(fname))
    batch = next(dg.flow(batch,
                         seed=1,
                         batch_size=1,
                         save_to_dir=os.path.dirname(fname),
                         save_prefix=save_prefix))

    saved = np.load(fname)
    assert len(saved.shape) == 4
    assert saved.shape == batch[0].shape
    assert not np.abs(saved - batch[0]).sum()
