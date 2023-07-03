import unittest


from semver.version_type import VersionType
from semver.scm import SCM
from semver.scm.mock import MockSCM


class TestMockSCM(unittest.TestCase):
    def setUp(self):
        self.scm: SCM = MockSCM()

    def test_get_tag_version(self):
        expected_version = "1.0.0"
        version = self.scm.get_tag_version()
        self.assertEqual(version, expected_version)

    def test_get_branch(self):
        expected_branch = "main"
        branch = self.scm.get_branch()
        self.assertEqual(branch, expected_branch)

    def test_get_merge_branch(self):
        expected_merge_branch = "main"
        merge_branch = self.scm.get_merge_branch()
        self.assertEqual(merge_branch, expected_merge_branch)

    def test_commit_and_push(self):
        branch = "main"
        self.scm.commit_and_push(branch)

    def test_tag_version(self):
        version = "1.0.0"
        self.scm.tag_version(version)

    def test_get_version_hash(self):
        version = "1.0.0"
        expected_hash = "HASH"
        version_hash = self.scm.get_version_hash(version)
        self.assertEqual(version_hash, expected_hash)

    def test_get_hash(self):
        expected_hash = "HASH"
        version_hash = self.scm.get_hash()
        self.assertEqual(version_hash, expected_hash)
