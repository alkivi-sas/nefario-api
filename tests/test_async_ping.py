from .utils import TestAPI


class TestAsyncPing(TestAPI):
    """Test for users."""

    def test_ping_one(self):
        """Test basic ping access."""
        token = self.token
        minion = self.minion

        url = '/api/v1.0/tasks/ping/{0}'.format(minion)

        # ping one minion
        r, s, h = self.post(url, token_auth=token)
        assert s == 202
        url = h['Location']

        while True:
            r, s, h = self.get(url, token_auth=token)
            if s != 202:
                break
        assert s == 200
        assert minion in r

        # now invalid minion
        minion = 'inminion_dzakdazdaz'
        url = '/api/v1.0/tasks/ping/{0}'.format(minion)
        r, s, h = self.post(url, token_auth=token)
        assert s == 202
        url = h['Location']

        while True:
            r, s, h = self.get(url, token_auth=token)
            if s != 202:
                break
        assert s == 400
