"""API Exceptions."""


class ApiError(Exception):
    """Base class for exceptions in API."""

    def __init__(self, message, error, status_code):
        """Init."""
        self.message = message
        self.error = error
        self.status_code = status_code
        super(ApiError, self).__init__()

    def to_dict(self):
        """To jsonify after."""
        rv = {}
        rv['error'] = str(self.error)
        rv['message'] = str(self)
        return rv


class SaltError(ApiError):
    """Base class for exceptions on server side."""

    def __init__(self, message, error=None, status_code=500):
        """Init."""
        if not error:
            error = 'wrong return from salt'
        super(SaltError, self).__init__(message, error, status_code)


class ValidationError(ApiError):
    """Base class for exceptions on client side."""

    def __init__(self, message, error=None, status_code=400):
        """Init."""
        if not error:
            error = 'bad request'
        super(ValidationError, self).__init__(message, error, status_code)


class ACLError(ApiError):
    """Base class for exceptions ACL."""

    def __init__(self, message, error=None, status_code=403):
        """Init."""
        if not error:
            error = 'access denied via acl'
        super(ACLError, self).__init__(message, error, status_code)

    def __str__(self):
        """Represent the exception."""
        return 'you are not allowed to perform {0}'.format(self.message)


class RoleError(ApiError):
    """Base class for exceptions ACL."""

    def __init__(self, permission, message=None, error=None, status_code=403):
        """Init."""
        if not error:
            error = 'access denied via roles'
        super(RoleError, self).__init__(message, error, status_code)
        self.permission = permission

    def __str__(self):
        """Represent the exception."""
        return 'you are forbidden to do that'


class SaltMinionError(SaltError):
    """Exception for wrong salt return."""

    def __str__(self):
        """Represent the exception."""
        return 'minion {0} is not in salt return'.format(self.message)


class SaltTaskError(SaltError):
    """Exception for salt task."""

    def __str__(self):
        """Represent the exception."""
        return 'task {0} not in salt return'.format(self.message)


class SaltACLError(ACLError):
    """Exception for salt ACL."""

    def __init__(self, tgt, fun, arg,
                 message=None, error=None, status_code=403):
        """Init."""
        super(SaltACLError, self).__init__(message, error, status_code)
        self.tgt = tgt
        self.fun = fun
        self.arg = arg

    def __str__(self):
        """Represent the exception."""
        return 'you are not allowed to perform {0} on {1}'.format(self.fun,
                                                                  self.tgt)


class RoleACLError(ACLError):
    """Rise on Exception for roles."""

    def __str__(self):
        """Represent the exception."""
        return 'you are not allowed to perform {0}'.format(self.message)
