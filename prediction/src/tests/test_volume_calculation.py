import numpy as np
import pytest

from ..algorithms.segment.trained_model import calculate_volume


@pytest.fixture
def centroids(scope='session'):
    yield [
        {'x': 0, 'y': 0, 'z': 0},
        {'x': 32, 'y': 32, 'z': 28},
        {'x': 45, 'y': 45, 'z': 12}]


@pytest.fixture
def centroids_alt(scope='session'):
    yield [
        {'x': 0, 'y': 0, 'z': 0},
        {'x': 0, 'y': 0, 'z': 0},
        {'x': 45, 'y': 45, 'z': 12}]


@pytest.fixture
def volumes(scope='session'):
    yield [100, 20, 30]


@pytest.fixture
def volumes_alt(scope='session'):
    yield [100, 100, 30]


def get_mask_path(tmpdir, mask):
    path = tmpdir.mkdir('masks').join('mask.npy')
    np.save(str(path), mask)
    return path


def generate_mask(centroids, volumes, shape=(50, 50, 29)):
    mask = np.zeros(shape, dtype=np.bool_)

    for centroid, volume in zip(centroids, volumes):
        centroid_ = np.asarray([centroid['x'], centroid['y'], centroid['z']])
        free_voxels = np.where(mask != -1)
        free_voxels = np.asarray(free_voxels).T
        free_voxels = sorted(free_voxels, key=lambda x: np.linalg.norm(x - centroid_, ord=2))
        free_voxels = np.asarray(free_voxels[:volume]).T
        mask[(free_voxels[0], free_voxels[1], free_voxels[2])] = True

    return mask


def test_volume_calculation(tmpdir, centroids, volumes):
    mask = generate_mask(centroids, volumes)

    # The balls modeled to be not overlapped
    assert mask.sum() == 150

    path = get_mask_path(tmpdir, mask)
    calculated_volumes = calculate_volume(str(path), centroids)

    # Despite they are overlapped, the amount of volumes must have preserved
    assert len(calculated_volumes) == len(volumes)
    assert calculated_volumes == volumes


def test_overlapped_volume_calculation(tmpdir, centroids_alt, volumes_alt):
    mask = generate_mask(centroids_alt, volumes_alt)

    # The balls area must be 100 + 30, since first ball have overlapped with the second one
    assert mask.sum() == 130

    path = get_mask_path(tmpdir, mask)
    calculated_volumes = calculate_volume(str(path), centroids_alt)

    # Despite they are overlapped, the amount of volumes must have preserved
    assert len(calculated_volumes) == len(volumes_alt)
    assert calculated_volumes == volumes_alt


def test_overlapped_dicom_volume_calculation(tmpdir, dicom_path, centroids_alt, volumes_alt):
    mask = generate_mask(centroids_alt, volumes_alt)

    # The balls area must be 100 + 30, since first ball have overlapped with the second one
    assert mask.sum() == 130

    path = get_mask_path(tmpdir, mask)
    calculated_volumes = calculate_volume(str(path), centroids_alt, dicom_path)

    # Despite they are overlapped, the amount of volumes must have preserved
    assert len(calculated_volumes) == len(volumes_alt)
    assert all(1.2360 >= mm / vox >= 1.2358 for vox, mm in zip(volumes_alt, calculated_volumes))
