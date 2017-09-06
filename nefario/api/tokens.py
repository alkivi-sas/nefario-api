"""Handle tokens endpoints."""
from flask import jsonify, g

from ..auth import basic_auth
from . import api


@api.route('/v1.0/tokens', methods=['POST'])
@basic_auth.login_required
def new_token():
    """
    Request a user token.
    This endpoint requires HTTP Basic authentication with nickname and
    password.
    ---
    tags:
      - tokens
    security:
      - basic: []
    responses:
      200:
        description: Returns a valid token
        schema:
          id: Token
          required:
            - token
          properties:
            token:
              type: string
              description: A valid token for the user

    """
    return jsonify({'token': g.current_user.token})
