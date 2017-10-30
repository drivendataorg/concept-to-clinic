"""
    prediction.config
    ~~~~~~~~~~~~~~~~~

    Provides the flask config options
"""
import os

LIDC_WILDCARD = ['LIDC-IDRI-*', '**', '**']


class Config(object):
    PROD_SERVER = os.getenv('PRODUCTION', False)
    DEBUG = False
    # The following paths are expanded at runtime
    CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
    PARENT_DIR = os.path.dirname(CURRENT_DIR)
    SEGMENT_ASSETS_DIR = os.path.abspath(os.path.join(CURRENT_DIR, 'src', 'algorithms', 'segment', 'assets'))
    DICOM_PATHS_DOCKER_WILDCARD = os.path.join(PARENT_DIR, 'images_full', *LIDC_WILDCARD)
    DICOM_PATHS_LOCAL_WILDCARD = os.path.join(PARENT_DIR, 'tests', 'assets', 'test_image_data', 'full',
                                              *LIDC_WILDCARD)


class Production(Config):
    pass


class Development(Config):
    DEBUG = True


class Test(Config):
    DEBUG = True
