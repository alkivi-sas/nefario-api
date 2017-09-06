from flask import g, request, current_app
from pepper import Pepper
from six import string_types

from .exceptions import ValidationError, SaltMinionError, SaltError

# Our app cache
minions = {}
functions = {}


def _get_pepper():
    """Return a pepper object with auth."""
    api = Pepper('http://master:8080', debug_http=True)
    api.auth = {'token': g.current_user.token, 'user': g.current_user.nickname, 'eauth': 'pam'}
    return api


def ping_one(minion):
    """Return a simple test.ping."""
    job = Job()
    result = job.run(minion, 'test.ping')
    if not result:
        result = False
    return {minion: result}


def ping():
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

    current_app.logger.debug('test keys')
    current_app.logger.debug(keys)
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
        current_app.logger.warning(info)
        current_app.logger.info(info)
        result = function(tgt, fun,
                          arg=arg,
                          timeout=timeout,
                          expr_form=expr_form,
                          ret=ret,
                          kwarg=kwarg,
                          **kwargs)

        current_app.logger.debug('result is {0}'.format(result))
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
