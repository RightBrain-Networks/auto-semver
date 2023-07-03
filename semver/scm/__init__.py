from abc import ABC, abstractmethod
from typing import Union, List

from semver.version_type import VersionType
from semver.logger import logger


class SCM(ABC):
    @abstractmethod
    def get_tag_version(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def get_branch(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def get_merge_branch(self) -> Union[str, None]:
        raise NotImplementedError()

    @abstractmethod
    def commit_and_push(self, branch: str) -> None:
        raise NotImplementedError()

    @abstractmethod
    def tag_version(self, version: str) -> None:
        raise NotImplementedError()

    @abstractmethod
    def get_version_hash(self, version: str) -> str:
        raise NotImplementedError()

    @abstractmethod
    def get_hash(self) -> str:
        raise NotImplementedError()

    def get_file_version(self, config: dict) -> str:
        """
        :param config: The bumpversion config as a dict
        :return: The current version from the config file
        """
        bump_version: Union[str, None] = config.get("bumpversion", None)
        version: str = (
            bump_version.get("current_version", "0.0.0") if bump_version else "0.0.0"
        )

        return version

    def get_version_type(
        self,
        merged_branch: str,
        major_branches: List[str],
        minor_branches: List[str],
        patch_branches: List[str],
    ) -> Union[VersionType, None]:
        """
        Get the version type based on the branches involved in the merge
        :param merged_branch: The branch that was merged
        :param major_branches: List of prefixes for major branches
        :param minor_branches: List of prefixes for minor branches
        :param patch_branches: List of prefixes for patch branches
        :return: The version type
        """
        logger.info(f"Merged branch is {merged_branch}")

        merged_prefix = merged_branch.split("/")[-1].rstrip("/")

        version_type: Union[VersionType, None] = None
        if merged_prefix:
            if merged_prefix in major_branches:
                version_type = VersionType.MAJOR
            if merged_prefix in minor_branches:
                version_type = VersionType.MINOR
            if merged_prefix in patch_branches:
                version_type = VersionType.PATCH
        return version_type
