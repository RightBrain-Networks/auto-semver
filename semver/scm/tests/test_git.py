import unittest
from unittest import mock
import subprocess

from semver.version_type import VersionType
from semver.exceptions import SemverException
from semver.scm import SCM
from semver.scm.git import Git


class TestMockSCM(unittest.TestCase):
    @mock.patch("subprocess.run")
    def setUp(self, mock_subprocess_run: mock.Mock):
        # Mock the subprocess.run function to avoid
        # running actual git commands
        mock_subprocess_run.return_value.returncode = 0
        mock_subprocess_run.return_value.stdout = ""

        self.scm = Git()

    def test_run_command(self):
        proc: subprocess.CompletedProcess[str] = self.scm._run_command("echo", "hello")
        self.assertEqual(proc.stdout, "hello\n")

    @mock.patch("toml.load")
    @mock.patch("subprocess.run")
    def test_get_tag_version(
        self, mock_subprocess_run: mock.Mock, mock_toml_load: mock.Mock
    ):
        mock_toml_load.return_value = {"bumpversion": {"tag_name": "v{new_version}"}}
        mock_subprocess_run.return_value.stdout = "v1.0.0\n"

        expected_version = "v1.0.0"
        version = self.scm.get_tag_version()
        self.assertEqual(version, expected_version)

    @mock.patch("toml.load")
    @mock.patch("subprocess.run")
    def test_get_tag_version_git_fail(
        self, mock_subprocess_run: mock.Mock, mock_toml_load: mock.Mock
    ):
        mock_toml_load.return_value = {"bumpversion": {"tag_name": "v{new_version}"}}
        mock_subprocess_run.return_value.returncode = 1
        mock_subprocess_run.side_effect = subprocess.CalledProcessError(
            1, "git", "git error"
        )

        with self.assertRaises(SemverException):
            self.scm.get_tag_version()

    @mock.patch("subprocess.run")
    def test_get_branch(self, mock_subprocess_run: mock.Mock):
        mock_subprocess_run.return_value.stdout = "main\n"

        expected_branch = "main"
        branch = self.scm.get_branch()
        self.assertEqual(branch, expected_branch)

    @mock.patch("subprocess.run")
    def test_get_merge_branch(self, mock_subprocess_run: mock.Mock):
        mock_subprocess_run.return_value.stdout = (
            "Merge pull request #1 from RightBrain-Networks/feature/example\n"
        )

        expected_merge_branch = "feature/example"
        merge_branch = self.scm.get_merge_branch()
        self.assertEqual(merge_branch, expected_merge_branch)

    @mock.patch("subprocess.run")
    def test_commit_and_push(self, mock_subprocess_run: mock.Mock):
        mock_subprocess_run.return_value.returncode = 0

        branch = "main"
        self.scm.commit_and_push(branch)

    @mock.patch("subprocess.run")
    def test_commit_and_push_git_fail(self, mock_subprocess_run: mock.Mock):
        mock_subprocess_run.return_value.returncode = 1

        branch = "main"
        with self.assertRaises(SemverException):
            self.scm.commit_and_push(branch)

    @mock.patch("subprocess.run")
    def test_commit_and_push_git_fail_tags(self, mock_subprocess_run: mock.Mock):
        mock_subprocess_run.side_effect = [
            mock.Mock(returncode=0),
            mock.Mock(returncode=1),
        ]

        branch = "main"
        with self.assertRaises(SemverException):
            self.scm.commit_and_push(branch)

    @mock.patch("subprocess.run")
    def test_tag_version(self, mock_subprocess_run: mock.Mock):
        mock_subprocess_run.return_value.returncode = 0

        version = "1.0.0"
        self.scm.tag_version(version)

    @mock.patch("subprocess.run")
    def test_get_version_hash(self, mock_subprocess_run: mock.Mock):
        mock_subprocess_run.return_value.stdout = "HASH\n"

        version = "1.0.0"
        expected_hash = "HASH"
        version_hash = self.scm.get_version_hash(version)
        self.assertEqual(version_hash, expected_hash)

    @mock.patch("subprocess.run")
    def test_get_hash(self, mock_subprocess_run: mock.Mock):
        mock_subprocess_run.return_value.stdout = "HASH\n"

        expected_hash = "HASH"
        version_hash = self.scm.get_hash()
        self.assertEqual(version_hash, expected_hash)
