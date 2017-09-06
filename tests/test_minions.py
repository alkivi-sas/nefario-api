from .utils import TestAPI


class TestMinions(TestAPI):
    """Test for minions."""

    def test_minions(self):
        """Test basic minions access."""
        token = self.token
        minion = self.minion

        # we test both sync and async
        url = '/api/v1.0/minions'
        r, s, h = self.get(url, token_auth=token)
        assert s == 200
        assert isinstance(r, list)
        assert minion in r
