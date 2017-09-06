"""API only package."""

from flask import Blueprint

api = Blueprint('api', __name__)

from . import errors, minions, ping, tasks, tokens  # noqa
