"""Handle nice json response for error."""

from flask import jsonify


def not_found(e):
    """Send a correct json for 404."""
    response = jsonify({'status': 404, 'error': 'Not found',
                        'message': 'Invalid resource URI'})
    response.status_code = 404
    return response


def method_not_supported(e):
    """Send a correct json for 405."""
    response = jsonify({'status': 405, 'error': 'Method not supported',
                        'message': 'This method is not supported'})
    response.status_code = 405
    return response


def internal_server_error(e):
    """Send a correct json for 500."""
    response = jsonify({'status': 500, 'error': 'Internal server error',
                        'message': e.args[0]})
    response.status_code = 500
    return response
