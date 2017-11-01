from os import path
from glob import glob

import pytest

from config import Config


@pytest.fixture
def dicom_path(scope='session'):
    dir1 = path.join(Config.SMALL_DICOM_PATHS, 'LIDC-IDRI-0001')
    dir2 = '1.3.6.1.4.1.14519.5.2.1.6279.6001.298806137288633453246975630178'
    dir3 = '1.3.6.1.4.1.14519.5.2.1.6279.6001.179049373636438705059720603192'
    yield '{}/{}/{}'.format(dir1, dir2, dir3)


@pytest.fixture
def dicom_paths(scope='session'):
    yield glob(path.join(Config.FULL_DICOM_PATHS_WILDCARD))


@pytest.fixture
def small_dicom_paths(scope='session'):
    yield glob(path.join(Config.SMALL_DICOM_PATHS_WILDCARD))


@pytest.fixture
def dicom_path_003(scope='session'):
    dir1 = path.join(Config.SMALL_DICOM_PATHS, 'LIDC-IDRI-0003')
    dir2 = '1.3.6.1.4.1.14519.5.2.1.6279.6001.101370605276577556143013894866'
    dir3 = '1.3.6.1.4.1.14519.5.2.1.6279.6001.170706757615202213033480003264'
    yield '{}/{}/{}'.format(dir1, dir2, dir3)


@pytest.fixture
def nodule_locations(scope='session'):
    yield [{'x': 50, 'y': 50, 'z': 21}]


@pytest.fixture
def nodule_001(scope='session'):
    yield {'x': 317, 'y': 367, 'z': 7}


@pytest.fixture
def nodule_003(scope='session'):
    yield {'x': 369, 'y': 347, 'z': 6}


@pytest.fixture
def ct_path(scope='session'):
    dir1 = path.join(Config.SMALL_DICOM_PATHS, 'LUNA-0001')
    dir2 = '1.3.6.1.4.1.14519.5.2.1.6279.6001.102133688497886810253331438797'
    yield '{}/{}'.format(dir1, dir2)


@pytest.fixture
def metaimage_path(ct_path, scope='session'):
    mhd_file = '1.3.6.1.4.1.14519.5.2.1.6279.6001.102133688497886810253331438797.mhd'
    yield '{}/{}'.format(ct_path, mhd_file)


@pytest.fixture
def luna_nodule(scope='session'):
    yield {'x': 0, 'y': 100, 'z': 556}


@pytest.fixture
def luna_nodules(scope='session'):
    yield [
        {'x': -20, 'y': 121, 'z': 556},
        {'x': -70, 'y': 101, 'z': 556},
        {'x': -77, 'y': 221, 'z': 556}]


@pytest.fixture
def model_path(scope='session'):
    yield path.join(Config.ALGOS_DIR, 'classify', 'assets', 'gtr123_model.ckpt')


@pytest.fixture
def content_type(scope='session'):
    yield 'application/json'
