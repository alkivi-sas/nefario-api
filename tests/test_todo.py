import pytest
import requests

from requests.exceptions import (
    ConnectionError,
)


def test_something(wait, nefario, nginx):
    """Sample test."""
    response = requests.get(nginx)
    response.raise_for_status()

