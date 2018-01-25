"""
    prediction.config
    ~~~~~~~~~~~~~~~~~

    Provides the flask config options
"""
import os

from os import path

LIDC_WILDCARD = ['LIDC-IDRI-*', '**', '**']


class Config(object):
    PROD_SERVER = os.getenv('PRODUCTION', False)
    DEBUG = False
    CURRENT_DIR = path.dirname(path.realpath(__file__))
    PARENT_DIR = path.dirname(CURRENT_DIR)
    ALGOS_DIR = path.abspath(path.join(CURRENT_DIR, 'src', 'algorithms'))
    ALGO_CLASSIFY_GTR123_PATH = os.path.join(ALGOS_DIR, 'classify', 'assets', 'gtr123_model.ckpt')
    SEGMENT_ASSETS_DIR = path.abspath(path.join(ALGOS_DIR, 'segment', 'assets'))
    ALGO_SEGMENT_PATH = os.path.join(SEGMENT_ASSETS_DIR, 'best_model.hdf5')
    FULL_DICOM_PATHS = path.join(PARENT_DIR, 'images_full')
    SMALL_DICOM_PATHS = path.join(PARENT_DIR, 'images')
    FULL_DICOM_PATHS_WILDCARD = path.join(FULL_DICOM_PATHS, *LIDC_WILDCARD)
    SMALL_DICOM_PATHS_WILDCARD = path.join(FULL_DICOM_PATHS, *LIDC_WILDCARD)
    DATA_DIR = path.abspath(path.join(CURRENT_DIR, 'data'))
    EXTRACTED_IMAGE_DIR = path.abspath(path.join(CURRENT_DIR, 'extracted'))


class Production(Config):
    pass


class Development(Config):
    DEBUG = True


class Test(Config):
    DEBUG = True
