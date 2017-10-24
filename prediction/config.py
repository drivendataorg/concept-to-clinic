"""
    prediction.config
    ~~~~~~~~~~~~~~~~~

    Provides the flask config options
"""
import os


class Config(object):
    PROD_SERVER = os.getenv('PRODUCTION', False)
    DEBUG = False
    # The following paths are expanded at runtime
    CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
    SEGMENT_ASSETS_DIR = os.path.abspath(os.path.join(CURRENT_DIR, 'src', 'algorithms', 'segment', 'assets'))
    DICOM_PATHS_DOCKER_WILDCARD = os.path.join('/images_full', 'LIDC-IDRI-*', '**', '**')
    DICOM_PATHS_LOCAL_WILDCARD = os.path.join(CURRENT_DIR, 'src', 'tests', 'assets',
                                              'test_image_data', 'full', 'LIDC-IDRI-*', '**', '**')


class Production(Config):
    pass


class Development(Config):
    DEBUG = True


class Test(Config):
    DEBUG = True
