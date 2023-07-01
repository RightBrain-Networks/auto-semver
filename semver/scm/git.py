import re
import subprocess
from typing import Union, List
from functools import cache

import toml

from semver.scm import SCM
from semver.logger import logger
from semver.version_type import VersionType
from semver.exceptions import SemverException


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

    def _run_command(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            args,
            capture_output=True,
            text=True,
            check=True,
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
        config: dict = toml.load("./.bumpversion.cfg")

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
            raise RuntimeError(
                f"Error getting latest tagged git version: {str(e.stderr).rstrip()}"
            )

        if len(tagged_versions) > 0 and tagged_versions[-1] != "":
            version = tagged_versions[-1]

        logger.debug(f"Tag Version: {version}")
        return version

    @cache
    def get_branch(self) -> str:
        """
        Get the main branch
        """
        proc = self._run_command(self.git_bin, "rev-parse", "--abbrev-ref", "HEAD")
        return proc.stdout.rstrip()

    @cache
    def get_merge_branch(self) -> Union[str, None]:
        """
        Get the branches involved in the merge
        :return: The branch involved in the merge
        """
        proc = self._run_command(self.git_bin, "log", "-1")
        message: str = proc.stdout

        branch: str = self.get_branch()

        logger.info(f"Main branch is {branch}")

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
        proc = self._run_command(self.git_bin, "push", "origin", branch)
        if proc.returncode != 0:
            raise SemverException(
                f"Error pushing versioning changes to {branch}: {proc.stderr}"
            )
        proc = self._run_command(self.git_bin, "push", "origin", "--tags")
        if proc.returncode != 0:
            raise SemverException(
                f"Error pushing versioning changes to {branch}: {proc.stderr}"
            )

    def tag_version(self, version: str) -> None:
        self._run_command(self.git_bin, "tag", version)