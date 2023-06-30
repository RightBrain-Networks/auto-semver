import subprocess
from typing import Union, List

try:
    from subprocess import DEVNULL  # py3k
except ImportError:
    import os

    DEVNULL = open(os.devnull, "wb")

import toml

from semver.logger import logging, logger, console_logger


def get_tag_version() -> str:
    """
    Get the latest tagged version from git tags
    :return: The latest tagged version
    """
    config: dict = toml.load("./.bumpversion.cfg")

    tag_expression: str = config["bumpversion"]["tag_name"].replace(
        "{new_version}", "[0-9]*.[0-9]*.[0-9]*"
    )

    logger.debug("Tag expression: " + str(tag_expression))

    # Default version is `0.0.0` or what is found in
    version = get_file_version(config)

    # If a version is found in git tags, use that the latest tagged version
    tagged_versions: Union[List[str], None] = None
    try:
        proc = subprocess.run(
            ["git", "tag", "--sort=v:refname", "-l", tag_expression],
            capture_output=True,
            text=True,
            check=True,
        )
        tagged_versions = proc.stdout.rstrip().split("\n")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"Error getting latest tagged git version: {str(e.stderr).rstrip()}"
        )

    if len(tagged_versions) > 0 and tagged_versions[-1] != "":
        version = tagged_versions[-1]

    logger.debug("Tag Version: " + str(version))
    return version


def get_file_version(config: dict) -> str:
    """
    :param config: The bumpversion config as a dict
    :return: The current version from the config file
    """
    bumpversion: Union[str, None] = config.get("bumpversion", None)
    version: Union[str, None] = (
        bumpversion.get("current_version", None) if bumpversion else None
    )

    if not bumpversion:
        config["bumpversion"] = {}
        version = "0.0.0"

    if not version:
        config["bumpversion"]["current_version"] = "0.0.0"
        version = "0.0.0"

    return version
