import docker
import pytest

def test_docker_connectivity():
    try:
        client = docker.from_env()
        info = client.info()
        assert "ID" in info
    except Exception as e:
        pytest.fail(f"Docker is not reachable: {e}")