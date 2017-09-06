from .utils import TestAPI


class TestErrors(TestAPI):
    """Test for users."""

    def test_404(self):
        """Test unknow path."""

        # we test both sync and async
        url = '/idontexist42'
        r, s, h = self.get(url)
        assert s == 404

    def test_405(self):
        """Test not supported."""
        url = '/api/v1.0/ping'
        r, s, h = self.delete(url)
        assert s == 405
