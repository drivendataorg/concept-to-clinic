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


def generate_motes(mask, centroid, volume):
    centroid_ = np.asarray([centroid['x'], centroid['y'], centroid['z']])
    free_voxels = np.where(mask != -1)
    free_voxels = np.asarray(free_voxels).T
    free_voxels = sorted(free_voxels, key=lambda x: np.linalg.norm(x - centroid_, ord=2))
    free_voxels = np.asarray(free_voxels[:volume]).T
    mask[(free_voxels[0], free_voxels[1], free_voxels[2])] = True


def generate_mask(shape, centroids, volumes):
    mask = np.zeros(shape, dtype=np.bool_)

    for centroid, volume in zip(centroids, volumes):
        generate_motes(mask, centroid, volume)

    return mask


def test_calculate_volume_over_unconnected_components(tmpdir, centroids):
    mask = generate_mask(shape=[50, 50, 29], centroids=centroids, volumes=[100, 20, 30])

    # The balls modeled to be not overlapped
    assert mask.sum() == 150

    path = tmpdir.mkdir("masks").join("mask.npy")
    np.save(str(path), mask)

    volumes_calculated = calculate_volume(str(path), centroids)
    assert len(volumes_calculated) == 3
    assert volumes_calculated == [100, 20, 30]


@pytest.fixture(scope='session')
def get_mask_connected(tmpdir_factory, centroids_alt):
    mask = generate_mask(shape=[50, 50, 29], centroids=centroids_alt, volumes=[100, 20, 30])

    # The balls area must be 100 + 30, since first ball have overlapped with the second one
    assert mask.sum() == 130

    path = tmpdir_factory.mktemp("masks").join("mask.npy")
    np.save(str(path), mask)
    return path, centroids_alt


def test_calculate_volume_over_connected_components(get_mask_connected):
    path, centroids = get_mask_connected
    volumes_calculated = calculate_volume(str(path), centroids)

    # Despite they are overlapped, the amount of volumes must have preserved
    assert len(volumes_calculated) == 3
    assert volumes_calculated == [100, 100, 30]


def test_calculate_volume_over_connected_components_with_dicom_path(dicom_path, get_mask_connected):
    path, centroids = get_mask_connected
    voxels_volumes = [100, 100, 30]
    real_volumes = calculate_volume(str(path), centroids, dicom_path)

    # Despite they are overlapped, the amount of volumes must have preserved
    assert len(real_volumes) == len(voxels_volumes)
    assert all([1.2360 >= mm / vox >= 1.2358
                for vox, mm in zip(voxels_volumes, real_volumes)])
