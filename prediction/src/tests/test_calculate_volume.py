import numpy as np
import pytest

from ..algorithms.segment import trained_model


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


def test_calculate_volume_over_unconnected_components(tmpdir):
    centroids = [[0, 0, 0], [32, 32, 28], [45, 45, 12]]
    centroids = [{'x': centroid[0], 'y': centroid[1], 'z': centroid[2]} for centroid in centroids]
    mask = generate_mask(shape=[50, 50, 29], centroids=centroids, volumes=[100, 20, 30])
    # The balls modelled to be not overlapped
    assert mask.sum() == 150

    path = tmpdir.mkdir("masks").join("mask.npy")
    np.save(str(path), mask)

    volumes_calculated = trained_model.calculate_volume(str(path), centroids)
    assert len(volumes_calculated) == 3
    assert volumes_calculated == [100, 20, 30]


@pytest.fixture(scope='session')
def get_mask_connected(tmpdir_factory):
    centroids = [[0, 0, 0], [0, 0, 0], [45, 45, 12]]
    centroids = [{'x': centroid[0], 'y': centroid[1], 'z': centroid[2]} for centroid in centroids]
    mask = generate_mask(shape=[50, 50, 29], centroids=centroids, volumes=[100, 20, 30])
    #   The balls area must be 100 + 30, since first ball have overlapped with the second one
    assert mask.sum() == 130

    path = tmpdir_factory.mktemp("masks").join("mask.npy")
    np.save(str(path), mask)
    return path, centroids


def test_calculate_volume_over_connected_components(get_mask_connected):
    path, centroids = get_mask_connected
    volumes_calculated = trained_model.calculate_volume(str(path), centroids)
    #   Despite they are overlapped, the amount of volumes must have preserved
    assert len(volumes_calculated) == 3
    assert volumes_calculated == [100, 100, 30]


def test_calculate_volume_over_connected_components_with_dicom_path(get_mask_connected):
    path, centroids = get_mask_connected
    voxels_volumes = [100, 100, 30]
    dicom_path = '../images/LIDC-IDRI-0001/1.3.6.1.4.1.14519.5.2.1.6279.6001.298806137288633453246975630178/' \
                 '1.3.6.1.4.1.14519.5.2.1.6279.6001.179049373636438705059720603192'
    real_volumes = trained_model.calculate_volume(str(path), centroids, dicom_path)

    #   Despite they are overlapped, the amount of volumes must have preserved
    assert len(real_volumes) == len(voxels_volumes)
    assert all([1.2360 >= mm / vox >= 1.2358
                for vox, mm in zip(voxels_volumes, real_volumes)])
