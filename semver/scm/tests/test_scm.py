import unittest

from semver.version_type import VersionType
from semver.scm import SCM
from semver.scm.mock import MockSCM


class TestSCM(unittest.TestCase):
    def setUp(self):
        self.scm: SCM = MockSCM()

    def test_get_file_version_existing_config(self):
        config = {"bumpversion": {"current_version": "1.2.3"}}
        expected_version = "1.2.3"
        version = self.scm.get_file_version(config)
        self.assertEqual(version, expected_version)

    def test_get_file_version_no_config(self):
        config = {}
        expected_version = "0.0.0"
        version = self.scm.get_file_version(config)
        self.assertEqual(version, expected_version)

    def test_get_file_version_no_version(self):
        config = {"bumpversion": {}}
        expected_version = "0.0.0"
        version = self.scm.get_file_version(config)
        self.assertEqual(version, expected_version)

    def test_get_version_type_major(self):
        merged_branch = "main"
        major_branches = ["main"]
        minor_branches = ["develop"]
        patch_branches = ["hotfix"]
        expected_version_type = VersionType.MAJOR
        version_type = self.scm.get_version_type(
            merged_branch, major_branches, minor_branches, patch_branches
        )
        self.assertEqual(version_type, expected_version_type)

    def test_get_version_type_minor(self):
        merged_branch = "develop"
        major_branches = ["main"]
        minor_branches = ["develop"]
        patch_branches = ["hotfix"]
        expected_version_type = VersionType.MINOR
        version_type = self.scm.get_version_type(
            merged_branch, major_branches, minor_branches, patch_branches
        )
        self.assertEqual(version_type, expected_version_type)

    def test_get_version_type_patch(self):
        merged_branch = "hotfix"
        major_branches = ["main"]
        minor_branches = ["develop"]
        patch_branches = ["hotfix"]
        expected_version_type = VersionType.PATCH
        version_type = self.scm.get_version_type(
            merged_branch, major_branches, minor_branches, patch_branches
        )
        self.assertEqual(version_type, expected_version_type)

    def test_get_version_type_none(self):
        merged_branch = "feature"
        major_branches = ["main"]
        minor_branches = ["develop"]
        patch_branches = ["hotfix"]
        expected_version_type = None
        version_type = self.scm.get_version_type(
            merged_branch, major_branches, minor_branches, patch_branches
        )
        self.assertEqual(version_type, expected_version_type)
