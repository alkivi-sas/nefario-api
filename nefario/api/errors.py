"""Custom handles of API errors."""
from flask import jsonify
from sqlalchemy.exc import IntegrityError
from ..exceptions import ApiError
from . import api


@api.errorhandler(IntegrityError)
def sql_error(e):
    """Send error 400 for IntegrityError on sqlachemy."""
    response = jsonify({'error': 'SQL Error', 'message': str(e.orig)})
    response.status_code = 500
    return response


@api.errorhandler(ApiError)
def bad_request(e):
    """Send generic error for API."""
    response = jsonify(e.to_dict())
    response.status_code = e.status_code
    return response
