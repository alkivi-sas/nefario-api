from flask import jsonify

from ..auth import token_auth
from . import api
from ..salt import get_minions


@api.route('/v1.0/minions', methods=['GET'])
@token_auth.login_required
def api_get_minions():
    """
    Return the list of salt keys.
    ---
    tags:
      - minions
    security:
      - token: []
    responses:
      200:
        description: Returns the lists of keys
        schema:
          id: keys
          type: array
          items:
            type: string
      500:
        description: Error in salt return
    """
    return jsonify(get_minions(use_cache=False))
