import pytest
import os
import requests

def is_responsive(url):
    """Check if something responds to ``url``."""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return True
    except ConnectionError:
        return False

@pytest.fixture(scope='session')
def nginx(docker_ip, docker_services):
    """Ensure that "some service" is up and responsive."""
    url = 'http://%s:%d' % (
        docker_ip,
        docker_services.port_for('nginx', 80),
    )
    docker_services.wait_until_responsive(
       timeout=30.0, pause=0.1,
       check=lambda: is_responsive(url)
    )
    return url


@pytest.fixture(scope='session')
def nefario(docker_ip, docker_services):
    """Ensure that "some service" is up and responsive."""
    url = 'http://%s:%d' % (
        docker_ip,
        docker_services.port_for('nefario', 5000),
    )
    docker_services.wait_until_responsive(
       timeout=30.0, pause=0.1,
       check=lambda: is_responsive(url)
    )
    return url


@pytest.fixture(scope='session')
def wait(docker_ip, docker_services):
    """Ensure that "some service" is up and responsive."""
    return ''
    url = 'http://%s:%d/login' % (
        docker_ip,
        docker_services.port_for('master', 8080),
    )
    docker_services.wait_until_responsive(
       timeout=30.0, pause=0.1,
       check=lambda: is_responsive(url)
    )
    return url

@pytest.fixture(scope='session')
def docker_compose_file(pytestconfig):
    return os.path.join(
        str(pytestconfig.rootdir),
        'docker-compose.yml'
    )

