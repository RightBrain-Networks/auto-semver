import unittest
from unittest import mock

from semver.version_type import VersionType
from semver.scm import SCM
from semver.scm.mock import MockSCM
from semver.semver import SemVer
from semver.exceptions import (
    NoMergeFoundException,
    NoGitFlowException,
    NotMainBranchException,
)


class TestSemVer(unittest.TestCase):
    def setUp(self):
        scm = mock.MagicMock(MockSCM())
        self.semver: SemVer = SemVer(scm=scm)

    @mock.patch("semver.semver.SemVer._bump_version")
    def test_version_repo(self, mock_bump_version: mock.Mock):
        self.semver._scm.get_tag_version.return_value = "1.0.0"
        self.semver._version_type = VersionType.PATCH

        expected_version = "1.0.1"
        mock_bump_version.return_value = expected_version
        version = self.semver._version_repo()
        self.assertEqual(version, expected_version)

    @mock.patch("semver.semver.SemVer._bump_version")
    def test_version_repo_no_tag(self, mock_bump_version: mock.Mock):
        self.semver._scm.get_tag_version.return_value = "1.0.0"
        self.semver._version_type = None

        with self.assertRaises(NoMergeFoundException):
            self.semver._version_repo()

    def test_process_config_string(self):
        expected_version = "v1.0.0"
        version = self.semver._process_config_string("v{new_version}", "1.0.0", "1.0.1")
        self.assertEqual(version, expected_version)

        expected_version = "v1.0.1"
        version = self.semver._process_config_string(
            "v{current_version}", "1.0.0", "1.0.1"
        )
        self.assertEqual(version, expected_version)

    @mock.patch("semver.semver.SemVer._update_file_version")
    def test_bump_version_major(self, mock_update_file_version: mock.Mock):
        expected_version = "2.0.0"
        version = self.semver._bump_version("1.0.0", VersionType.MAJOR)
        self.assertEqual(version, expected_version)

    @mock.patch("semver.semver.SemVer._update_file_version")
    def test_bump_version_minor(self, mock_update_file_version: mock.Mock):
        expected_version = "1.1.0"
        version = self.semver._bump_version("1.0.0", VersionType.MINOR)
        self.assertEqual(version, expected_version)

    @mock.patch("semver.semver.SemVer._update_file_version")
    def test_bump_version_patch(self, mock_update_file_version: mock.Mock):
        expected_version = "1.0.1"
        version = self.semver._bump_version("1.0.0", VersionType.PATCH)
        self.assertEqual(version, expected_version)

    @mock.patch("toml.load")
    @mock.patch("pathlib.Path.is_file")
    @mock.patch("builtins.open", mock.mock_open())
    def test_update_file_version(
        self,
        mock_path_is_file: mock.Mock,
        mock_toml_load: mock.Mock,
    ):
        mock_toml_load.return_value = {
            "bumpversion": {"current_version": "1.0.0"},
            "bumpversion:file:VERSION": {
                "search": "0.0.0",
                "replace": "{new_version}",
            },
        }
        mock_path_is_file.return_value = True
        self.semver._update_file_version("1.0.1", "1.0.0")

        mock_path_is_file.return_value = False
        self.semver._update_file_version("1.0.1", "1.0.0")

    @mock.patch("semver.semver.SemVer._version_repo", mock.MagicMock())
    def test_run_ok(self):
        self.semver._version_repo = mock.MagicMock()
        self.semver._version_repo.return_value = "1.0.1"
        self.semver._scm.get_branch.return_value = "main"
        self.semver._scm.get_merge_branch.return_value = "main"
        self.semver._scm.get_version_type.return_value = VersionType.MINOR
        self.semver._scm.commit_and_push.return_value = None

        self.semver._main_branches = ["main"]
        self.semver.run()

    @mock.patch("semver.semver.SemVer._version_repo", mock.MagicMock())
    def test_run_not_merge(self):
        self.semver._version_repo = mock.MagicMock()
        self.semver._version_repo.return_value = "1.0.1"
        self.semver._scm.get_branch.return_value = "main"
        self.semver._scm.get_merge_branch.return_value = None
        self.semver._scm.get_version_type.return_value = VersionType.MINOR
        self.semver._scm.commit_and_push.return_value = None

        self.semver._main_branches = ["main"]

        with self.assertRaises(NoMergeFoundException):
            self.semver.run()

    @mock.patch("semver.semver.SemVer._version_repo", mock.MagicMock())
    def test_run_not_version_type(self):
        self.semver._version_repo = mock.MagicMock()
        self.semver._version_repo.return_value = "1.0.1"
        self.semver._scm.get_branch.return_value = "feature/example"
        self.semver._scm.get_merge_branch.return_value = "main"
        self.semver._scm.get_version_type.return_value = VersionType.MINOR
        self.semver._scm.commit_and_push.return_value = None

        self.semver._main_branches = ["main"]

        with self.assertRaises(NotMainBranchException):
            self.semver.run()

    @mock.patch("semver.semver.SemVer._version_repo", mock.MagicMock())
    def test_run_not_main_branch(self):
        self.semver._version_repo = mock.MagicMock()
        self.semver._version_repo.return_value = "1.0.1"
        self.semver._scm.get_branch.return_value = "main"
        self.semver._scm.get_merge_branch.return_value = "main"
        self.semver._scm.get_version_type.return_value = None
        self.semver._scm.commit_and_push.return_value = None

        self.semver._main_branches = ["main"]

        with self.assertRaises(NoGitFlowException):
            self.semver.run()

    @mock.patch("semver.semver.SemVer._bump_version")
    def test_get_version(self, mock_bump_version: mock.Mock):
        self.semver._scm.get_branch.return_value = "feature/example"
        self.semver._scm.get_tag_version.return_value = "1.0.0"
        self.semver._scm.get_version_hash.return_value = "HASH"
        self.semver._scm.get_hash.return_value = "ALT_HASH"

        mock_bump_version.return_value = "1.0.1"

        expected_version = "1.0.0+HASH"
        version = self.semver.get_version(dot=True)
        self.assertEqual(version, "feature.example")

    @mock.patch("semver.semver.SemVer._bump_version")
    def test_get_version_docker(self, mock_bump_version: mock.Mock):
        self.semver._scm.get_branch.return_value = "feature/example"
        self.semver._scm.get_tag_version.return_value = "1.0.0"
        self.semver._scm.get_version_hash.return_value = "HASH"
        self.semver._scm.get_hash.return_value = "ALT_HASH"

        mock_bump_version.return_value = "1.0.1"

        expected_version = "1.0.0+HASH"
        version = self.semver.get_version(version_format="docker")
        self.assertEqual(version, "1.0.1-feature-example.0")

    @mock.patch("semver.semver.SemVer._bump_version")
    def test_get_version_maven(self, mock_bump_version: mock.Mock):
        self.semver._scm.get_branch.return_value = "feature/example"
        self.semver._scm.get_tag_version.return_value = "1.0.0"
        self.semver._scm.get_version_hash.return_value = "HASH"
        self.semver._scm.get_hash.return_value = "ALT_HASH"

        mock_bump_version.return_value = "1.0.1"

        expected_version = "1.0.1-feature-example-SNAPSHOT"
        version = self.semver.get_version(version_format="maven")
        self.assertEqual(version, expected_version)

    def test_get_version_no_hash(self):
        self.semver._scm.get_branch.return_value = "main"
        self.semver._scm.get_tag_version.return_value = "1.0.0"
        self.semver._scm.get_version_hash.return_value = "HASH"
        self.semver._scm.get_hash.return_value = "HASH"

        expected_version = "1.0.0"
        version = self.semver.get_version()
        self.assertEqual(version, expected_version)
