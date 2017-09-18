import pytest

from src.preprocess import load_ct, crop_patches


@pytest.fixture
def ct_path():
    return '../images/LUNA-0001/'\
           + '1.3.6.1.4.1.14519.5.2.1.6279.6001.102133688497886810253331438797'


def test_patches_from_ct(ct_path):
    ct_array, meta = load_ct.load_ct(ct_path)
    meta = load_ct.MetaData(meta)
    centroids = [[507, -21, -177], [547, -121, -220], [530, -221, -277]]
    centroids = [{'x': centroid[0], 'y': centroid[1], 'z': centroid[2]} for centroid in centroids]
    patches = crop_patches.patches_from_ct(ct_array, patch_shape=12, centroids=centroids, meta=meta)
    assert isinstance(patches, list)
    assert len(patches) == 3
    assert all([patch.shape == (12, 12, 12) for patch in patches])
