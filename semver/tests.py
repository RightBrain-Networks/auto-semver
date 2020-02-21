import unittest, os, subprocess, semver
from semver.logger import logging, logger, console_logger

from semver import get_version

config_data = """
[bumpversion]
current_version = 0.0.0
commit = False
tag = True
tag_name = {new_version}

[semver]
main_branches = master
major_branches = major
minor_branches = minor
patch_branches = patch
"""

test_directory = "test"


class TestSemverObject(unittest.TestCase):
    def test_get_version_type_major_merge(self):
        semver_object = semver.SemVer()
        semver_object.merged_branch = "major/unittest"
        semver_object.get_version_type()
        self.assertEqual(semver_object.version_type, "major")
    def test_get_version_type_minor_merge(self):
        semver_object = semver.SemVer()
        semver_object.merged_branch = "minor/unittest"
        semver_object.get_version_type()
        self.assertEqual(semver_object.version_type, "minor")
    def test_get_version_type_patch_merge(self):
        semver_object = semver.SemVer()
        semver_object.merged_branch = "patch/unittest"
        semver_object.get_version_type()
        self.assertEqual(semver_object.version_type, "patch")

class TestGetVersion(unittest.TestCase):
    def test_get_branch_version(self):
        create_git_environment()
        branch = get_version.get_version()
        self.assertEqual(branch, "master")
    def test_branch_dotting(self):
        create_git_environment()
        subprocess.run(['git', 'checkout', '-b', 'test/branch'])
        branch = get_version.get_version(True)
        self.assertEqual(branch, "test.branch")
    def test_branch_dotting_false(self):
        create_git_environment()
        subprocess.run(['git', 'checkout', '-b', 'test/branch'])
        branch = get_version.get_version(False)
        self.assertEqual(branch, "test/branch")

class TestGetTagVersion(unittest.TestCase):
    def test_get_version_tag(self):
        create_git_environment()
        subprocess.run(['git', 'tag', '1.0.0'])
        tag = get_version.get_tag_version()
        self.assertEqual(tag, "1.0.0")
    def test_default_get_version_tag(self):
        create_git_environment()
        tag = get_version.get_tag_version()
        self.assertEqual(tag, "0.0.0")

def create_git_environment():
    subprocess.run(['rm', '-rf', './.git'])
    subprocess.run(['git', 'init'])
    subprocess.run(['touch', 'file.txt'])
    subprocess.run(['git', 'add', 'file.txt'])
    subprocess.run(['git', 'commit', '-m', 'file.txt'])
    subprocess.run(['git', 'remote', 'add', 'origin', os.getcwd()+'/.git'])

if __name__ == "__main__":
    console_logger.setLevel(logging.DEBUG)

    subprocess.run(['rm', '-rf', test_directory])
    subprocess.run(['mkdir', test_directory])
    os.chdir(test_directory)
    with open('.bumpversion.cfg', "w") as config:
        config.write(config_data)
    unittest.main()
    os.chdir("..")