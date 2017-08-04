"""
    prediction.config
    ~~~~~~~~~~~~~~~~~

    Provides the flask config options
"""
from os import getenv


class Config(object):
    PROD_SERVER = getenv('PRODUCTION', False)
    DEBUG = False


class Production(Config):
    pass


class Development(Config):
    DEBUG = True


class Test(Config):
    DEBUG = True
