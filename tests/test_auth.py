from .utils import TestAPI


class TestAuth(TestAPI):
    """Test for minions."""

    def test_password(self):
        """Test password responses."""
        user = self.user
        password = self.password

        # we test both sync and async
        url = '/api/v1.0/tokens'
        r, s, h = self.post(url, basic_auth='{0}:{1}'.format(user, password))
        assert s == 200

        password = 'wrong_password'
        r, s, h = self.post(url, basic_auth='{0}:{1}'.format(user, password))
        assert s == 401

    def test_token(self):
        """Test token responses."""
        token = self.token

        url = '/api/v1.0/minions'
        r, s, h = self.get(url, token_auth=token)
        assert s == 200

        token = 'fake'
        r, s, h = self.get(url, token_auth=token)
        assert s == 401
