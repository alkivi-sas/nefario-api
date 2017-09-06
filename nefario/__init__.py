"""
Application factory.

Use to return a flask app configured.
"""
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flasgger import Swagger
from celery import Celery

from config import config

# Flask extensions
db = SQLAlchemy()
cors = CORS()
swagger = Swagger()
celery = Celery(__name__,
                broker=os.environ.get('CELERY_BROKER_URL', 'redis://'),
                backend=os.environ.get('CELERY_BROKER_URL', 'redis://'))
celery.config_from_object('nefario.celeryconfig')


# Import models so that they are registered with SQLAlchemy
from . import models  # noqa

# Import celery task so that it is registered with the Celery workers
from .api.async import run_flask_request  # noqa


def create_app(config_name=None, main=True):
    """Return a flask app."""
    if config_name is None:
        config_name = os.environ.get('NEFARIO_CONFIG', 'development')
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize flask extensions
    db.init_app(app)
    cors.init_app(app)
    swagger.init_app(app)
    celery.conf.update(config[config_name].CELERY_CONFIG)

    # Register API routes
    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    # Register handlers
    from .errors import not_found, method_not_supported, internal_server_error
    app.register_error_handler(404, not_found)
    app.register_error_handler(405, method_not_supported)
    app.register_error_handler(500, internal_server_error)

    return app
