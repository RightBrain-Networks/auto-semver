import subprocess
from typing import Union, List

import toml

from semver.scm import SCM
from semver.logger import logger


class Perforce(SCM):
    def __init__(self) -> None:
        super().__init__()

    def get_tag_version(self) -> str:
        """
        Get the latest tagged version from Perforce labels
        :return: The latest tagged version
        """
        config: dict = toml.load("./.bumpversion.cfg")

        tag_expression: str = config["bumpversion"]["tag_name"].replace(
            "{new_version}", "[0-9]*.[0-9]*.[0-9]*"
        )

        logger.debug("Tag expression: " + str(tag_expression))

        # Default version is `0.0.0` or what is found in
        version = self.get_file_version(config)

        # If a version is found in Perforce labels, use that the latest labeled version
        labeled_versions: Union[List[str], None] = None
        try:
            proc = subprocess.run(
                ["p4", "labels", "-e", tag_expression, "-m1"],
                capture_output=True,
                text=True,
                check=True,
            )
            labeled_versions = proc.stdout.rstrip().split("\n")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"Error getting latest labeled Perforce version: {str(e.stderr).rstrip()}"
            )

        if len(labeled_versions) > 0 and labeled_versions[-1] != "":
            version = labeled_versions[-1]

        logger.debug("Label Version: " + str(version))
        return version
