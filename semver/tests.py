import unittest, os, subprocess, re, semver
from semver.logger import logging, logger, console_logger

from semver import get_version, utils, NO_MERGE_FOUND, GET_COMMIT_MESSAGE

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
    def test_run_no_merge(self):
        semver_object = semver.SemVer()
        try:
            result = semver_object.run(False)
        except Exception as e:
            if e == NO_MERGE_FOUND:
                self.assertTrue(True)
            else:
                self.assertTrue(False)

class TestGetVersion(unittest.TestCase):
    def test_get_branch_version(self):
        create_git_environment()
        branch = get_version.get_version()
        self.assertEqual(branch, "master")
    def test_branch_dotting(self):
        create_git_environment()
        subprocess.call(['git', 'checkout', '-b', 'test/branch'])
        branch = get_version.get_version(dot=True)
        self.assertEqual(branch, "test.branch")
    def test_branch_dotting_false(self):
        create_git_environment()
        subprocess.call(['git', 'checkout', '-b', 'test/branch'])
        branch = get_version.get_version(dot=False)
        self.assertEqual(branch, "test/branch")
    def test_branch_npm_pre_release(self):
        create_git_environment()
        subprocess.call(['git', 'checkout', '-b', 'patch/branch'])
        branch = get_version.get_version(version_format='npm')
        self.assertEqual(branch, "0.0.0-patch-branch.0")
    def test_branch_maven_pre_release(self):
        create_git_environment()
        subprocess.call(['git', 'checkout', '-b', 'minor/branch'])
        branch = get_version.get_version(version_format='maven')
        self.assertEqual(branch, "0.0.0-minor-branch-SNAPSHOT")
    def test_branch_maven_bad_branch(self):
        create_git_environment()
        subprocess.call(['git', 'checkout', '-b', 'test/branch'])
        branch = get_version.get_version(version_format='maven')
        self.assertEqual(branch, "test/branch")
    def test_get_version_run(self):
        create_git_environment()
        val = subprocess.Popen(['python', '../get_version.py', '-d'], stdout=subprocess.PIPE,
                            stderr=open(os.devnull, 'wb'), cwd='.').stdout.read().decode('utf-8').rstrip()
        self.assertEqual(val, "master")
        

class TestGetTagVersion(unittest.TestCase):
    def test_get_version_tag(self):
        create_git_environment()
        subprocess.call(['git', 'tag', '1.0.0'])
        tag = utils.get_tag_version()
        self.assertEqual(tag, "1.0.0")
    def test_get_version_multiple(self):
        create_git_environment()
        subprocess.call(['git', 'tag', '0.1.0'])
        subprocess.call(['git', 'tag', '0.1.1'])
        subprocess.call(['git', 'tag', '0.1.2'])
        subprocess.call(['git', 'tag', '0.1.3'])
        subprocess.call(['git', 'tag', '0.2.0'])
        subprocess.call(['git', 'tag', '0.3.0'])
        subprocess.call(['git', 'tag', '0.3.1'])
        subprocess.call(['git', 'tag', '1.0.0'])
        subprocess.call(['git', 'tag', '1.1.0'])
        subprocess.call(['git', 'tag', '1.2.0'])
        subprocess.call(['git', 'tag', '1.2.1'])
        tag = utils.get_tag_version()
        self.assertEqual(tag, "1.2.1")
    def test_get_version_out_of_order(self):
        subprocess.call(['git', 'tag', '0.1.0'])
        subprocess.call(['git', 'tag', '0.1.1'])
        subprocess.call(['git', 'tag', '0.5.2'])
        subprocess.call(['git', 'tag', '0.1.3'])
        subprocess.call(['git', 'tag', '8.1.0'])
        subprocess.call(['git', 'tag', '0.3.8'])
        subprocess.call(['git', 'tag', '3.3.1'])
        subprocess.call(['git', 'tag', '1.4.0'])
        subprocess.call(['git', 'tag', '1.1.7'])
        subprocess.call(['git', 'tag', '1.2.0'])
        subprocess.call(['git', 'tag', '0.2.1'])
        tag = utils.get_tag_version()
        self.assertEqual(tag, "8.1.0")
    def test_default_get_version_tag(self):
        create_git_environment()
        tag = utils.get_tag_version()
        self.assertEqual(tag, "0.0.0")
        
class TestGetCommitMessageRegex(unittest.TestCase):
    def test_github_message(self):
        matches = GET_COMMIT_MESSAGE.search("Merge pull request #1 from user/branch")
        if matches:
            self.assertEqual(matches.group(4), None)
            self.assertEqual(matches.group(5), "branch")
        else:
            self.assertTrue(False)
        pass
    def test_gitlab_message(self):
        matches = GET_COMMIT_MESSAGE.search("Merge branch 'branch' into 'master'")
        if matches:
            self.assertEqual(matches.group(4), "master")
            self.assertEqual(matches.group(2), "branch")
        else:
            self.assertTrue(False)
    def test_non_merge_message(self):
        matches = GET_COMMIT_MESSAGE.search("Example unrelated commit message that should get 0 matches")
        self.assertEqual(matches, None)

def create_git_environment():
    subprocess.call(['rm', '-rf', './.git'])
    subprocess.call(['git', 'init'])
    subprocess.call(['touch', 'file.txt'])
    subprocess.call(['git', 'add', 'file.txt'])
    subprocess.call(['git', 'commit', '-m', 'file.txt'])
    subprocess.call(['git', 'remote', 'add', 'origin', os.getcwd()+'/.git'])

if __name__ == "__main__":
    console_logger.setLevel(logging.DEBUG)

    subprocess.call(['rm', '-rf', test_directory])
    subprocess.call(['mkdir', test_directory])
    os.chdir(test_directory)
    with open('.bumpversion.cfg', "w") as config:
        config.write(config_data)
    unittest.main()
    os.chdir("..")
