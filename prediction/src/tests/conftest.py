import signal
from glob import glob
from os import path

import pytest
from config import Config

from . import get_timeout


@pytest.fixture
def dicom_path(scope='session'):
    dir1 = path.join(Config.SMALL_DICOM_PATHS, 'LIDC-IDRI-0001')
    dir2 = '1.3.6.1.4.1.14519.5.2.1.6279.6001.298806137288633453246975630178'
    dir3 = '1.3.6.1.4.1.14519.5.2.1.6279.6001.179049373636438705059720603192'
    yield path.join(dir1, dir2, dir3)


@pytest.fixture
def mhd_path(scope='session'):
    dir1 = path.join(Config.SMALL_DICOM_PATHS, 'LUNA-0001')
    dir2 = '1.3.6.1.4.1.14519.5.2.1.6279.6001.102133688497886810253331438797'
    yield path.join(dir1, dir2)


@pytest.fixture
def full_dicom_path(scope='session'):
    dir1 = path.join(Config.FULL_DICOM_PATHS, 'LIDC-IDRI-0001')
    dir2 = '1.3.6.1.4.1.14519.5.2.1.6279.6001.298806137288633453246975630178'
    dir3 = '1.3.6.1.4.1.14519.5.2.1.6279.6001.179049373636438705059720603192'
    yield path.join(dir1, dir2, dir3)


@pytest.fixture
def full_mhd_path(scope='session'):
    dir1 = path.join(Config.FULL_DICOM_PATHS, 'LUNA-0001')
    dir2 = '1.3.6.1.4.1.14519.5.2.1.6279.6001.102133688497886810253331438797'
    yield path.join(dir1, dir2)


@pytest.fixture
def dicom_paths(scope='session'):
    yield sorted(glob(path.join(Config.FULL_DICOM_PATHS_WILDCARD)))


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


"""Adapted from https://stackoverflow.com/questions/46766899/pytest-timeout-fail-test-instead-killing-whole-test-run"""


class TimeoutExit(BaseException):
    pass


def _timeout(signum, frame):
    raise TimeoutExit("Runner timeout is reached, runner is terminating.")


@pytest.hookimpl
def pytest_configure(config):
    # Install the signal handlers that we want to process.
    signal.signal(signal.SIGTERM, _timeout)
    signal.signal(signal.SIGALRM, _timeout)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_protocol(item, nextitem):
    timeout = get_timeout()
    found_timeout_marker = False

    for k in item.keywords:
        found_timeout_marker |= (k == "stop_timeout")

    if timeout == 0 or not found_timeout_marker:
        # All slow tests should be run or the test does not have a stop_timeout marker
        # The hook needs to yield exactly once, otherwise there'll be an error. Without the return it would yield twice,
        # without the yield it wouldn't yield at all.
        yield
        return

    signal.alarm(timeout)
    item.add_marker(pytest.mark.xfail(raises=TimeoutExit, reason="Test was stopped after timeout"))

    try:
        # Run the setup, test body, and teardown stages.
        yield
    finally:
        # Disable the alarm when the test passes or fails.
        # I.e. when we get into the framework's body.
        signal.alarm(0)
