from typing import List
from pathlib import Path
from functools import cache
import configparser

import toml

from semver.exceptions import SemverException


@cache
def get_settings() -> dict:
    """
    Get the settings from the config file
    :return: The settings from the config file
    """
    if Path("./.bumpversion.toml").is_file():
        return toml.load("./.bumpversion.toml")
    if Path("./.bumpversion.cfg").is_file():
        config = configparser.ConfigParser()
        config.read("./.bumpversion.cfg")

        return {section: dict(config.items(section)) for section in config.sections()}

    raise SemverException("No config file found")


def setting_to_array(setting) -> List[str]:
    """
    Get a setting from the config file and return it as a list
    :param setting: The setting to get from the config file
    :return: The setting as a list
    """
    config: dict = get_settings()
    semver: dict = config.get("semver", {})
    value: str = semver.get(setting, "")

    return [v.strip() for v in value.split(",") if v.strip()]
