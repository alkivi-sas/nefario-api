"""Handle ping functions."""
from flask import jsonify

from ..auth import token_auth
from . import api
from ..salt import ping_one, ping


@api.route('/v1.0/minions/<string:minion>/ping', methods=['POST'])
@api.route('/v1.0/ping/<string:minion>', methods=['POST'])
@token_auth.login_required
def api_ping_one(minion):
    """
    Perform synchronous test.ping on a minion.
    Before performing the task, ensure that the minion is present
    in keys. Return 400 if not.
    ---
    tags:
      - ping
    security:
      - token: []
    parameters:
      - name: minion
        in: path
        description: minion to ping
        required: true
        type: string
    responses:
      200:
        description: Returns the result
        schema:
          id: ping_one
          required:
            - minion1
          properties:
            minion1:
              type: boolean
      400:
        description: When minion is not found
    """
    return jsonify(ping_one(minion))


@api.route('/v1.0/ping', methods=['POST'])
@token_auth.login_required
def api_ping():
    """
    Perform synchronous test.ping on a list of minions.
    Before performing the task, ensure that all the minions are present
    in keys. All minions that are not in the keys are removed.
    ---
    tags:
      - ping
    security:
      - token: []
    parameters:
      - name: target
        in: body
        description: minion to ping
        required: true
        schema:
          id: target_ping
          properties:
            target:
              description: target to ping
              type: array
              items:
                type: string
    responses:
      200:
        description: Returns the result
        schema:
          id: ping
          required:
            - minion1
            - minion2
          properties:
            minion1:
              type: boolean
            minion2:
              type: boolean
      400:
        description: When all minions are not found
    """
    return jsonify(ping())
