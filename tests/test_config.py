import pytest
from ruamel import yaml

from runthis.server.config import Config, get_config_from_yaml


@pytest.fixture
def config_obj(tmpdir):
    return Config(
        tty_server="ttyd",
        command="xonsh",
        docker=False,
        docker_image="myimage",
        keyfile="/path/to/privkey.pem",
    )


def test_fields(config_obj):
    assert config_obj.tty_server == "ttyd"
    assert config_obj.command == "xonsh"
    assert not config_obj.docker
    assert config_obj.docker_image == "myimage"
    assert config_obj.keyfile == "/path/to/privkey.pem"



DICT_CONFIG_CONTENT = dict(
        tty_server="tty-server",
        command="myshell",
        docker=True,
        docker_image="img",
        host="8.8.8.8",
        certfile="/path/to/cert.pem",
)


@pytest.mark.parametrize(
    "config_content", [DICT_CONFIG_CONTENT, {"runthis": DICT_CONFIG_CONTENT}]
)
def test_populate_config_by_yaml(config_content, tmpdir):
    yaml_path = tmpdir.join("TEST.yaml")
    yaml_path.write(yaml.dump(config_content))
    config_obj = get_config_from_yaml(str(yaml_path))
    assert config_obj.tty_server == "tty-server"
    assert config_obj.command == "myshell"
    assert config_obj.docker
    assert config_obj.docker_image == "img"
    assert config_obj.host == "8.8.8.8"
    assert config_obj.certfile == "/path/to/cert.pem"
