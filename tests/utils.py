import logging
import base64
import json
import pytest

from requests import Session


def _get_result(rv):
    """Log if error 500."""
    # clean up the database session, since this only occurs when the app
    # context is popped.
    body = rv.text
    if body is not None and body != '':
        try:
            body = json.loads(body)
        except:
            pass

    if rv.status_code == 500:
        logging.warning('headers')
        logging.warning(rv.headers)
        logging.warning('body')
        logging.warning(body)

    return body, rv.status_code, rv.headers


class TestAPI(object):
    """
    Generic class for our tests.
    It use the fixture client_class with allows us to self.client.
    """

    @classmethod
    @pytest.mark.usefixtures('api_url')
    @pytest.fixture(scope="class", autouse=True)
    def setup(self, api_url):
        """Fixture for variable common in tests."""
        self._token = None
        self._minion = None
        self.user = 'test'
        self.password = 'test'
        self.api_url = api_url
        self.client = Session()

    def request(self, method, url, params=None, data=None, headers=None):
        if url.startswith('http'):
            final_url = url
        else:
            final_url = '{0}/{1}'.format(self.api_url, url.lstrip('/'))
        return self.client.request(method, final_url, params, data, headers)

    @property
    def token(self):
        """Get a token we know is valid."""
        if not self._token:
            self._token = self.get_token(user=self.user)
        return self._token

    @property
    def minion(self):
        """Get a minion on the current salt master."""
        if not self._minion:
            r, s, h = self.get('/api/v1.0/minions',
                               token_auth=self.token)
            assert s == 200
            self._minion = r[0]
        return self._minion

    def get_token(self, user, password=None):
        """Return a valid token for a user."""
        if not password:
            password = user
        r, s, h = self.post('/api/v1.0/tokens',
                            basic_auth='{0}:{1}'.format(user, password))
        assert s == 200
        return r['token']

    def get_headers(self, basic_auth=None, token_auth=None):
        """Manage headers for requests."""
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        if basic_auth is not None:
            headers['Authorization'] = 'Basic ' + base64.b64encode(
                basic_auth.encode('utf-8')).decode('utf-8')
        if token_auth is not None:
            headers['Authorization'] = 'Bearer ' + token_auth
        return headers

    def get(self, url, basic_auth=None, token_auth=None):
        """GET method helper."""
        rv = self.request('GET', url,
                          headers=self.get_headers(basic_auth, token_auth))
        return _get_result(rv)

    def post(self, url, data=None, basic_auth=None, token_auth=None):
        """POST method helper."""
        d = data if data is None else json.dumps(data)
        rv = self.request('POST', url, data=d,
                          headers=self.get_headers(basic_auth, token_auth))
        return _get_result(rv)

    def put(self, url, data=None, basic_auth=None, token_auth=None):
        """PUT method helper."""
        d = data if data is None else json.dumps(data)
        rv = self.request('PUT', url, data=d,
                          headers=self.get_headers(basic_auth, token_auth))
        return _get_result(rv)

    def delete(self, url, basic_auth=None, token_auth=None):
        """DELETE method helper."""
        rv = self.request('DELETE', url, headers=self.get_headers(basic_auth,
                                                                  token_auth))
        return _get_result(rv)
