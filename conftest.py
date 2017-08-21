import pytest
import os

@pytest.fixture(scope='session')
def docker_compose_file(pytestconfig):
    return os.path.join(
        str(pytestconfig.rootdir),
        'docker-compose.yml'
    )

