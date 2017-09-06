from swagger_spec_validator import validate_spec_url


def test_swagger(api_url):
    """Test for swagger doc."""
    assert not validate_spec_url('{0}/api/v1.0/spec'.format(api_url))
