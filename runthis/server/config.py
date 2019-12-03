"""Config specification for runthis-server"""
import os
import platform
import tempfile
from dataclasses import asdict, dataclass, field
from typing import List, Set, Union


@dataclass(init=True, repr=True, eq=True, order=False)
class Config:
    command: str = "python3"
    docker: bool = True
    docker_image: str = "ubuntu:latest"
    gotty_path: str = "gotty"
    port: int = 5000
    tty_server: str = "gotty"
    tty_server_port_start: int = 8080
    ttyd_path: str = "ttyd"


def ensure_list(var):
    """Converts to a list, safely"""
    if isinstance(var, str):
        return [var]
    return var


def ensure_set(var):
    """Converts to a set, safely"""
    if isinstance(var, str):
        return {var}
    if isinstance(var, list):
        return set(var)
    return var


def get_config_from_yaml(yaml_path, config=None):
    """Free function responsible to create or fill a `Config` object
    with the content of a yaml file.

    Parameters
    ----------
    yaml_path : str
        Path to the YAML file
    config : Config, optional
        If it is received a Config object it will be filled otherwise
        this function will create a new Config object.

    Returns
    -------
    Config
        Config object with the yaml configuration

    """
    from ruamel.yaml import YAML

    if config is None:
        config = Config()

    with open(yaml_path, "r") as config_file:
        yaml = YAML(typ="safe").load(config_file)

    if yaml is None:
        yaml = {}

    if "runthis" in yaml:
        yaml = yaml["runthis"]

    def yaml_attr(attr):
        if yaml.get(attr) is not None:
            return yaml.get(attr)
        return asdict(config)[attr]

    config.command = yaml_attr("command")
    config.docker = yaml_attr("docker")
    config.docker_image = yaml_attr("docker_image")
    config.gotty_path = yaml_attr("gotty_path")
    config.port = yaml_attr("port")
    config.tty_server = yaml_attr("tty_server")
    config.tty_server_port_start = yaml_attr("tty_server_port_start")
    config.ttyd_path = yaml_attr("ttyd_path")
    return config
