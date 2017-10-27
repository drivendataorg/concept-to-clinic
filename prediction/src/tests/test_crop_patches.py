import pytest

from ..preprocess.load_ct import load_ct
from ..preprocess.crop_patches import patches_from_ct


def test_patches_from_ct(ct_path, luna_nodules):
    patches = patches_from_ct(*load_ct(ct_path), patch_shape=12, centroids=luna_nodules)
    assert isinstance(patches, list)
    assert len(patches) == 3
    assert all(patch.shape == (12, 12, 12) for patch in patches)
