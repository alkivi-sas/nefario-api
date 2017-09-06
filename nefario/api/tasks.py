"""Handles /tasks endpoints."""
from celery import states

from ..auth import token_auth
from ..utils import url_for
from . import api
from .async import run_flask_request


@api.route('/v1.0/tasks/status/<string:id>', methods=['GET'])
@token_auth.login_required
def get_status(id):
    """
    Return the status of a request.
    Return status about an asynchronous task. If this request returns a 202
    status code, it means that task hasn't finished yet. Else, the response
    from the task is returned.
    ---
    tags:
      - tasks
    security:
      - token: []
    parameters:
      - name: id
        in: path
        description: id of the task
        required: true
        type: string
    responses:
      202:
        description: The tasks in the finished yet
        headers:
          Location:
            description: The location to get final result
            type: string
      200:
        description: Real result of the task
    """
    task = run_flask_request.AsyncResult(id)
    if task.state in [states.PENDING, states.RECEIVED, states.STARTED]:
        return '', 202, {'Location': url_for('api.get_status', id=id),
                         'Access-Control-Expose-Headers': 'Location'}
    return task.info
