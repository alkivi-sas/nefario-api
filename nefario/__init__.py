"""
Application factory.

Use to return a flask app configured.
"""
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flasgger import Swagger

from config import config

# Flask extensions
db = SQLAlchemy()
cors = CORS()
swagger = Swagger()

# Import models so that they are registered with SQLAlchemy
from . import models  # noqa


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

    # Register API routes
    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    # Register handlers
    from .errors import not_found, method_not_supported, internal_server_error
    app.register_error_handler(404, not_found)
    app.register_error_handler(405, method_not_supported)
    app.register_error_handler(500, internal_server_error)

    return app
