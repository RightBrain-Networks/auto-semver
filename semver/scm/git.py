import re
import subprocess
from typing import Union, List
from functools import lru_cache

import toml

from semver.scm import SCM
from semver.logger import logger
from semver.version_type import VersionType
from semver.exceptions import SemverException
from semver.utils import get_settings


class Git(SCM):
    def __init__(self, global_user: bool = False) -> None:
        self.git_commit_pattern = re.compile(
            r"Merge (branch|pull request) '?([^']+)'? (into|from) (?:'(.+)'|[^\/]+\/([^\n\\]+))"
        )

        self.git_bin = "git"

        self.global_user: bool = global_user
        self.git_email: str = "versioner@semver.com"
        self.git_user: str = "Semantic Versioner"
        self._setup_git_user()

        super().__init__()

    def _run_command(
        self, *args: str, throwExceptions: bool = True
    ) -> subprocess.CompletedProcess:
        return subprocess.run(
            args,
            capture_output=True,
            text=True,
            check=throwExceptions,
        )

    def _setup_git_user(self) -> None:
        self._run_command(
            self.git_bin,
            "config",
            "--global" if self.global_user else "--local",
            "user.email",
            f'"{self.git_email}"',
        )

        self._run_command(
            self.git_bin,
            "config",
            "--global" if self.global_user else "--local",
            "user.name",
            f'"{self.git_user}"',
        )

    def get_tag_version(self) -> str:
        """
        Get the latest tagged version from git tags
        :return: The latest tagged version
        """
        config: dict = get_settings()

        tag_expression: str = config["bumpversion"]["tag_name"].replace(
            "{new_version}", "[0-9]*.[0-9]*.[0-9]*"
        )

        logger.debug(f"Tag expression: {tag_expression}")

        # Default version is `0.0.0` or what is found in
        version = self.get_file_version(config)

        # If a version is found in git tags, use that the latest tagged version
        tagged_versions: Union[List[str], None] = None
        try:
            proc = self._run_command(
                self.git_bin, "tag", "--sort=v:refname", "-l", tag_expression
            )
            tagged_versions = proc.stdout.rstrip().split("\n")
        except subprocess.CalledProcessError as e:
            raise SemverException(
                f"Error getting latest tagged git version: {str(e.stderr).rstrip()}"
            )

        if (
            tagged_versions is not None
            and len(tagged_versions) > 0
            and tagged_versions[-1] != ""
        ):
            version = tagged_versions[-1]

        logger.debug(f"Tag Version: {version}")
        return version

    @lru_cache(maxsize=None)
    def get_branch(self) -> str:
        """
        Get the main branch
        :return: The main branch
        """
        proc = self._run_command(self.git_bin, "rev-parse", "--abbrev-ref", "HEAD")
        return proc.stdout.rstrip()

    @lru_cache(maxsize=None)
    def get_merge_branch(self) -> Union[str, None]:
        """
        Get the branches involved in the merge
        :return: The branch involved in the merge
        """
        proc = self._run_command(self.git_bin, "log", "-1")
        message: str = proc.stdout

        branch: str = self.get_branch()

        matches = self.git_commit_pattern.search(
            message.replace("\\n", "\n").replace("\\", "")
        )
        merged_branch: Union[str, None] = None
        if matches:
            merged_branch = str(
                matches.group(2) if matches.group(4) == branch else matches.group(5)
            )

        return merged_branch

    def commit_and_push(self, branch: str) -> None:
        """
        Commit and push the versioning changes
        :param branch: The branch to push
        """
        proc = self._run_command(
            self.git_bin, "push", "origin", branch, throwExceptions=False
        )
        if proc.returncode != 0:
            raise SemverException(
                f"Error pushing versioning changes to {branch}: {proc.stderr}"
            )
        proc = self._run_command(
            self.git_bin, "push", "origin", "--tags", throwExceptions=False
        )
        if proc.returncode != 0:
            raise SemverException(
                f"Error pushing versioning changes to {branch}: {proc.stderr}"
            )

    def tag_version(self, version: str) -> None:
        """
        Creates a git tag at HEAD with the given version
        :param version: The version to tag
        """
        self._run_command(self.git_bin, "tag", version)

    def get_version_hash(self, version: str) -> str:
        """
        Get the hash of the commit that has the given version
        :param version: The version to get the hash for
        :return: The hash of the commit that has the given version
        """
        proc = self._run_command(self.git_bin, "rev-list", "-n", "1", version)
        return proc.stdout.rstrip()

    def get_hash(self) -> str:
        """
        Get the hash of the current commit
        :return: The hash of the current commit
        """
        proc = self._run_command(self.git_bin, "rev-parse", "HEAD")
        return proc.stdout.rstrip()
