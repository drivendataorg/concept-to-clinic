"""
    prediction.factory
    ~~~~~~~~~~~~~~~~~~

    Provides the flask application
"""

from flask import Flask

try:
    from .. import config
except ValueError:
    import config


def create_app(config_mode='Production', config_file=None):
    """Flask app creator that accepts configuration modes

    Kwargs:
        config_mode (str): Configuration mode. Must be one of 'Production',
            'Development', or 'Test'. Default: 'Production'. Overridden if
            `config_file` is given.

        config_file (str): Path to a Python configuration file. Overrides
            `config_mode`.

    Returns:
        (obj): A Flask app

    Examples:
        >>> from src.factory import create_app
        >>> app = create_app(config_mode='Test')
    """
    app = Flask('prediction')

    from .views import blueprint

    app.register_blueprint(blueprint)

    if config_file:
        app.config.from_pyfile(config_file)
    elif config_mode:
        try:
            app.config.from_object(getattr(config, config_mode))
        except AttributeError:
            pass
    else:
        app.config.from_envvar('APP_SETTINGS', silent=True)

    return app


app = create_app()
