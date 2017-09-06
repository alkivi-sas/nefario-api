import pytest
import docker


def _docker_client():
    return docker.from_env()


@pytest.fixture(scope='session')
def api_url():
    """Ensure that "some service" is up and responsive."""
    client = _docker_client()
    web = client.containers.get('web')
    web.attrs['NetworkSettings']

    port = None
    for k, v in web.attrs['NetworkSettings']['Ports'].items():
        if len(v) == 1:
            port = v[0]['HostPort']

    ip = None
    for k, v in web.attrs['NetworkSettings']['Networks'].items():
        ip = v['IPAddress']

    return 'http://{0}:{1}'.format(ip, port)
