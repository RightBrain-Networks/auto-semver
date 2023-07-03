from typing import Union

from semver.scm import SCM


class MockSCM(SCM):
    def get_tag_version(self) -> str:
        return "1.0.0"

    def get_branch(self) -> str:
        return "main"

    def get_merge_branch(self) -> Union[str, None]:
        return "main"

    def commit_and_push(self, branch: str) -> None:
        pass

    def tag_version(self, version: str) -> None:
        pass

    def get_version_hash(self, version: str) -> str:
        return "HASH"

    def get_hash(self) -> str:
        return "HASH"
