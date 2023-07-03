from typing import List, Union
from pathlib import Path
import re

import toml

from semver.logger import logger
from semver.scm import SCM
from semver.version_type import VersionType
from semver.exceptions import (
    NoMergeFoundException,
    NotMainBranchException,
    NoGitFlowException,
)


class SemVer:
    """Primary class for handling auto-semver processing"""

    def __init__(
        self,
        scm: SCM,
        main_branches: Union[List[str], None] = None,
        major_branches: Union[List[str], None] = None,
        minor_branches: Union[List[str], None] = None,
        patch_branches: Union[List[str], None] = None,
    ):
        """
        Initialize the SemVer object
        :param global_user: Toggles git user at a global level, useful for build servers
        :param scm: The source control manager to use
        :param main_branches: Branches to run versioning on
        :param major_branches: List of prefixes for major branches
        :param minor_branches: List of prefixes for minor branches
        :param patch_branches: List of prefixes for patch branches
        """
        self._merged_branch: Union[str, None] = None
        self._branch: Union[str, None] = None
        self._version_type: Union[VersionType, None] = None

        self._main_branches: List[str] = main_branches if main_branches else []
        self._major_branches: List[str] = major_branches if major_branches else []
        self._minor_branches: List[str] = minor_branches if minor_branches else []
        self._patch_branches: List[str] = patch_branches if patch_branches else []

        self._scm: SCM = scm

    def _version_repo(self) -> str:
        """
        Use bump_version to update the repo version
        :return: The new version
        """
        version = self._scm.get_tag_version()
        if not self._version_type:
            raise NoMergeFoundException()

        logger.debug(f"Running bumpversion of type: {self._version_type.name}")
        return self._bump_version(version, self._version_type)

    def _process_config_string(self, cfg_string, new_version, version):
        return cfg_string.replace("{new_version}", new_version).replace(
            "{current_version}", version
        )

    def _bump_version(
        self,
        version: str,
        index: VersionType = VersionType.MINOR,
        tag_repo: bool = True,
        update_files: bool = True,
    ) -> str:
        """
        Bump the version of the repo
        :param version: The current version
        :param index: The index of the version to bump
        :param tag_repo: Whether or not to tag the repo
        :param update_files: Whether or not to update the files
        :return: The new version
        """
        v: List[str] = version.split(".")

        # Bump version
        v[index] = str(int(v[index]) + 1)

        # Reset subversions
        i = len(v) - 1
        while i > index:
            v[i] = "0"
            i = i - 1

        # Get new version
        new_version = ".".join(v)

        # Tag new version
        if tag_repo and version != new_version:
            self._scm.tag_version(new_version)

        # Update local files
        if update_files:
            self._update_file_version(new_version, version)

        return new_version

    def _update_file_version(self, new_version: str, version: str = "0.0.0"):
        """
        Update the version in the config file
        :param new_version: The new version
        :param version: The current version
        """
        # Open up config file
        config = toml.load("./.bumpversion.cfg")

        bump_version_file_prefix = "bumpversion:file:"
        bump_version_file_prefix_len = len(bump_version_file_prefix)
        for section in config:
            if section.startswith(bump_version_file_prefix):
                file_path = Path(section[bump_version_file_prefix_len:])
                section_data = config[section]
                if file_path.is_file():
                    # Get search val from config
                    search_val = section_data["search"]
                    search_val = self._process_config_string(
                        search_val, new_version, version
                    )

                    # Get replace val from config
                    replace_val = section_data["replace"]
                    replace_val = self._process_config_string(
                        replace_val, new_version, version
                    )

                    # Update replace values in file
                    with open(file_path, "r") as file:
                        filedata = file.read()
                    filedata = filedata.replace(search_val, replace_val)
                    with open(file_path, "w") as file:
                        file.write(filedata)
                else:
                    logger.warning(
                        f"Tried to version file: '{file_path}' but it doesn't exist!"
                    )

    def get_version(
        self, build: int = 0, version_format: Union[str, None] = None, dot: bool = False
    ):
        """
        Get the version of the repo
        :param build: The build number
        :param version_format: The format of the version
        :param dot: Whether or not to replace / with .
        :return: The version
        """
        version = self._scm.get_tag_version()

        # Get the commit hash of the version
        v_hash = self._scm.get_version_hash(version)
        # Get the current commit hash
        c_hash = self._scm.get_hash()

        # If the version commit hash and current commit hash
        # do not match return the branch name else return the version
        if v_hash != c_hash:
            logger.debug("v_hash and c_hash do not match!")
            branch = self._scm.get_branch()
            logger.debug("merged branch is: {}".format(branch))
            version_type = self._scm.get_version_type(
                branch, self._major_branches, self._minor_branches, self._patch_branches
            )
            logger.debug("version type is: {}".format(version_type))
            if version_type:
                next_version = self._bump_version(
                    self._scm.get_tag_version(), version_type, False, False
                )

                if version_format in ("npm", "docker"):
                    return "{}-{}.{}".format(
                        next_version, re.sub(r"[/_]", "-", branch), build
                    )
                if version_format == "maven":
                    qualifier = "SNAPSHOT" if build == 0 else build
                    return "{}-{}-{}".format(
                        next_version, re.sub(r"[/_]", "-", branch), qualifier
                    )
            if dot:
                branch = branch.replace("/", ".")
            return branch
        return version

    def run(self, push=True):
        """
        Run the versioning process
        1) get branches from last commit message
        2) see if we're merging into a main branch
        3) see what type of versioning we should do
        4) version the repo
        :param push: Whether or not to push the changes
        """
        self._branch = self._scm.get_branch()
        self._merged_branch = self._scm.get_merge_branch()

        if not self._merged_branch:
            raise NoMergeFoundException("No merge found")
        if self._branch not in self._main_branches:
            raise NotMainBranchException("Not a main branch")

        self._version_type = self._scm.get_version_type(
            self._branch,
            self._major_branches,
            self._minor_branches,
            self._patch_branches,
        )

        if not self._version_type:
            raise NoGitFlowException("Could not determine version type")

        self._version_repo()
        if push:
            self._scm.commit_and_push(self._branch)
