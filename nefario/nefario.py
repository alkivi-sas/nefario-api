import os
import time

from flask import Flask, jsonify, g, request, abort
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flasgger import Swagger
from redis import Redis
from pepper import Pepper, PepperException
from six import string_types

from exceptions import ValidationError, SaltError, ApiError, SaltMinionError

basedir = os.path.abspath(os.path.dirname(__file__))

# App config
app = Flask(__name__)
app.config['SECRET_KEY'] = 'something to change'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 'sqlite:///' + os.path.join(basedir, 'db.sqlite'))
redis = Redis(host='redis', port=6379)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Swagger config

swagger_config = {
    'specs':
    [
        {
            'version': '1.0',
            'title': 'Api v1.0',
            'endpoint': 'api',
            'description': 'This is the version 1 of our API',
            'route': '/api/v1.0/spec',
        },
    ],
    'securityDefinitions': {
        'token': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization'
        },
        'basic': {
            'type': 'basic'
        }
    },
    'headers': [],
}


# Init Extensions
db = SQLAlchemy(app)
CORS(app)
swagger = Swagger(app, config=swagger_config)


# Init Auth
basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth('Bearer')

# Our app cache
minions = {}
functions = {}

from models import User


@basic_auth.verify_password
def verify_password(nickname, password):
    """
    Password verification callback.

    ---
    securityDefinitions:
      UserSecurity:
        type: basic
    """
    if not nickname or not password:
        return False

    api = Pepper('http://master:8080')
    try:
        auth = api.login(nickname, password, 'pam')
    except PepperException:
        return False

    user = User.query.filter_by(nickname=nickname).first()
    if not user:
        user = User.create({'nickname': nickname})

    app.logger.debug('auth')
    app.logger.debug(auth)
    user.token = auth['token']
    db.session.add(user)
    db.session.commit()

    g.current_user = user

    return True


@basic_auth.error_handler
def password_error():
    """Return a 401 error to the client."""
    # To avoid login prompts in the browser, use the "Bearer" realm.
    return (jsonify({'error': 'authentication required'}), 401,
            {'WWW-Authenticate': 'Bearer realm="Authentication Required"'})


@token_auth.verify_token
def verify_token(token):
    """
    Token verification callback.

    ---
    securityDefinitions:
      UserSecurity:
        type: apiKey
        in: header
        name: token
    """
    user = User.query.filter_by(token=token).first()
    if user is None:
        return False
    db.session.add(user)
    db.session.commit()
    g.current_user = user
    return True


@token_auth.error_handler
def token_error():
    """Return a 401 error to the client."""
    return (jsonify({'error': 'authentication required'}), 401,
            {'WWW-Authenticate': 'Bearer realm="Authentication Required"'})


@app.route('/')
def hello():
    count = redis.incr('hits')
    return 'Hello Docker! I have been seen {0} times.\n'.format(count)


@app.route('/api/v1.0/tokens', methods=['POST'])
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


@app.route('/api/v1.0/minions/<string:minion>/ping', methods=['POST'])
@app.route('/api/v1.0/ping/<string:minion>', methods=['POST'])
@token_auth.login_required
def ping_one(minion):
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
    return jsonify(_ping_one(minion))


@app.route('/api/v1.0/ping', methods=['POST'])
@token_auth.login_required
def ping():
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
    return jsonify(_ping())


def _ping_one(minion):
    """Return a simple test.ping."""
    job = Job()
    result = job.run(minion, 'test.ping')
    if not result:
        result = False
    return {minion: result}


def _ping():
    """Return the simple test.ping but can be on a list."""
    data = request.json
    if not data:
        raise ValidationError('no json data in request')

    if 'target' not in data:
        raise ValidationError('no target in parameters')
    targets = data['target']

    to_test = None
    if isinstance(targets, list):
        to_test = targets
    elif isinstance(targets, string_types):
        to_test = [targets]
    else:
        raise ValidationError('target parameter is not an array not a scalar')

    keys = get_minions()
    minions = []
    for m in to_test:
        if m in keys:
            minions.append(m)

    if not minions:
        raise ValidationError('minions list is not valid')

    real_target = ','.join(minions)
    job = Job(only_one=False)
    result = job.run(real_target, 'test.ping', expr_form='list')
    return result


def get_minions(type='minions', use_cache=True):
    """
    Build a cache using minions array.
    By default the type is minions and we use the cache
    """
    global minions
    if use_cache and type in minions:
        return minions[type]

    api = _get_pepper()
    keys = api.wheel('key.list_all')
    keys = keys['return'][0]['data']['return']

    app.logger.debug('test keys')
    app.logger.debug(keys)
    if type not in keys:
        raise SaltError('no key {0} in key.list_all'.format(type))
    minions[type] = keys[type]
    return minions[type]


class Job(object):
    """Represents a Salt Job."""

    def __init__(self, only_one=True, async=False):
        """Keep trace of only_one to automatically raise error."""
        self.only_one = only_one
        self.async = async

    def run(self, tgt, fun, arg=(), timeout=None, expr_form='glob', ret='',
            kwarg=None, **kwargs):
        """
        Run a basic task.
        In only_one mode, we perform some checks :
        - minion should be in the list, raise ValidationError if not
        - result should have a minion entrie, raise SaltMinionError if not
        """
        # Perform additional check
        if self.only_one:
            if tgt not in get_minions():
                msg = 'Minion {0} is not valid'.format(tgt)
                raise ValidationError(msg)

            # We skip check for sys.list_functions to infinite recursion
            if fun not in 'sys.list_functions':
                if fun not in get_minion_functions(tgt):
                    msg = 'Task {0} not valid'.format(fun)
                    raise ValidationError(msg)

        # We might want to run async request
        function = None
        client = _get_pepper()
        if self.async:
            function = client.local_async
        else:
            function = client.local

        info = 'launching {0} on {1}, '.format(fun, tgt) + \
               'using args {0}, '.format(str(arg)) + \
               'targeting using {0}'.format(expr_form)
        app.logger.warning(info)
        app.logger.info(info)
        result = function(tgt, fun,
                          arg=arg,
                          timeout=timeout,
                          expr_form=expr_form,
                          ret=ret,
                          kwarg=kwarg,
                          **kwargs)

        app.logger.debug('result is {0}'.format(result))
        if self.async:
            return result

        # If only one, perform additional check
        if self.only_one:
            result = result['return'][0]
            if tgt not in result:
                raise SaltMinionError(tgt)
            else:
                return result[tgt]
        return result['return'][0]


def get_minion_functions(minion):
    """
    Build a cache using functions array.
    To get this we have to call sys.list_functions.
    And to call sys.list_functions we need a minion.
    We assume that the current machine is a minion, which should be
    the case everytile.
    """
    global functions
    if minion in functions:
        return functions[minion]

    # no functions, build cache
    job = Job()
    result = job.run(minion, 'sys.list_functions')
    functions[minion] = result

    return result


@app.route('/api/v1.0/minions', methods=['GET'])
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


def _get_pepper():
    """Return a pepper object with auth."""
    api = Pepper('http://master:8080', debug_http=True)
    api.auth = {'token': g.current_user.token, 'user': g.current_user.nickname, 'eauth': 'pam'}
    return api


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


@app.errorhandler(ApiError)
def bad_request(e):
    """Send generic error for API."""
    response = jsonify(e.to_dict())
    response.status_code = e.status_code
    return response


# Register errors
app.register_error_handler(404, not_found)
app.register_error_handler(405, method_not_supported)
app.register_error_handler(500, internal_server_error)


if __name__ == "__main__":
    db.create_all()
    app.run(host="0.0.0.0", debug=True)