import unittest, os, subprocess, re, semver
from semver.logger import logging, logger, console_logger

from semver import bump, get_version, utils, NO_MERGE_FOUND, GET_COMMIT_MESSAGE

config_data = """
[bumpversion]
current_version = 0.0.0
commit = False
tag = True
tag_name = {new_version}

[bumpversion:file:file.txt]
search = 0.0.0
replace = {new_version}

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
        self.assertEqual(semver_object.version_type, semver.VersionType.MAJOR)
    def test_get_version_type_minor_merge(self):
        semver_object = semver.SemVer()
        semver_object.merged_branch = "minor/unittest"
        semver_object.get_version_type()
        self.assertEqual(semver_object.version_type, semver.VersionType.MINOR)
    def test_get_version_type_patch_merge(self):
        semver_object = semver.SemVer()
        semver_object.merged_branch = "patch/unittest"
        semver_object.get_version_type()
        self.assertEqual(semver_object.version_type, semver.VersionType.PATCH)
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
        self.assertEqual(branch, "0.0.1-patch-branch.0")
    def test_branch_docker_pre_release(self):
        create_git_environment()
        subprocess.call(['git', 'checkout', '-b', 'patch/branch'])
        branch = get_version.get_version(build=2,version_format='docker')
        self.assertEqual(branch, "0.0.1-patch-branch.2")
    def test_branch_maven_pre_release(self):
        create_git_environment()
        subprocess.call(['git', 'checkout', '-b', 'minor/branch'])
        branch = get_version.get_version(version_format='maven')
        self.assertEqual(branch, "0.1.0-minor-branch-SNAPSHOT")
    def test_branch_maven_bad_branch(self):
        create_git_environment()
        subprocess.call(['git', 'checkout', '-b', 'test/branch'])
        branch = get_version.get_version(version_format='maven')
        self.assertEqual(branch, "test/branch")
        

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
    def test_branch_in_message(self):
        matches = GET_COMMIT_MESSAGE.search(str(b'commit examplehash\nMerge: example\nAuthor: Test <test@nodomain.rightbrainnetworks.com>\nDate:   Mon Jun 15 18:15:22 2020 -0400\n\n    Merge pull request #45 from user/branch\n    \n    user/branch\n'))
        if matches:
            self.assertEqual(matches.group(4), None)
            self.assertEqual(matches.group(5), "branch")
        else:
            self.assertTrue(False)
    def test_non_merge_message(self):
        matches = GET_COMMIT_MESSAGE.search("Example unrelated commit message that should get 0 matches")
        self.assertEqual(matches, None)
    def test_gitlab_merge_with_double_quotes(self):
        matches = GET_COMMIT_MESSAGE.search("Merge branch 'branch' into 'master'\n\n\"Message in quotes!\"")
        if matches:
            self.assertEqual(matches.group(4), "master")
            self.assertEqual(matches.group(2), "branch")
        else:
            self.assertTrue(False)

class TestVersionBumping(unittest.TestCase):
    def test_patch_bump(self):
        self.assertEqual("0.0.1", bump.bump_version("0.0.0", semver.VersionType.PATCH, False))
        self.assertEqual("0.0.2", bump.bump_version("0.0.1", semver.VersionType.PATCH, False))
        self.assertEqual("0.1.1", bump.bump_version("0.1.0", semver.VersionType.PATCH, False))
        self.assertEqual("1.0.1", bump.bump_version("1.0.0", semver.VersionType.PATCH, False))
        self.assertEqual("1.2.4", bump.bump_version("1.2.3", semver.VersionType.PATCH, False))
        self.assertEqual("0.0.11", bump.bump_version("0.0.10", semver.VersionType.PATCH, False))
        self.assertEqual("0.10.1", bump.bump_version("0.10.0", semver.VersionType.PATCH, False))
        self.assertEqual("10.0.1", bump.bump_version("10.0.0", semver.VersionType.PATCH, False))
    def test_minor_bump(self):
        self.assertEqual("0.1.0", bump.bump_version("0.0.0", semver.VersionType.MINOR, False))
        self.assertEqual("0.1.0", bump.bump_version("0.0.1", semver.VersionType.MINOR, False))
        self.assertEqual("0.2.0", bump.bump_version("0.1.0", semver.VersionType.MINOR, False))
        self.assertEqual("1.1.0", bump.bump_version("1.0.0", semver.VersionType.MINOR, False))
        self.assertEqual("1.3.0", bump.bump_version("1.2.3", semver.VersionType.MINOR, False))
        self.assertEqual("0.1.0", bump.bump_version("0.0.10", semver.VersionType.MINOR, False))
        self.assertEqual("0.11.0", bump.bump_version("0.10.0", semver.VersionType.MINOR, False))
        self.assertEqual("10.1.0", bump.bump_version("10.0.0", semver.VersionType.MINOR, False))
    def test_major_bump(self):
        self.assertEqual("1.0.0", bump.bump_version("0.0.0", semver.VersionType.MAJOR, False))
        self.assertEqual("1.0.0", bump.bump_version("0.0.1", semver.VersionType.MAJOR, False))
        self.assertEqual("1.0.0", bump.bump_version("0.1.0", semver.VersionType.MAJOR, False))
        self.assertEqual("2.0.0", bump.bump_version("1.0.0", semver.VersionType.MAJOR, False))
        self.assertEqual("2.0.0", bump.bump_version("1.2.3", semver.VersionType.MAJOR, False))
        self.assertEqual("1.0.0", bump.bump_version("0.0.10", semver.VersionType.MAJOR, False))
        self.assertEqual("1.0.0", bump.bump_version("0.10.0", semver.VersionType.MAJOR, False))
        self.assertEqual("11.0.0", bump.bump_version("10.0.0", semver.VersionType.MAJOR, False))
class TestFileVersioning(unittest.TestCase):
    def test_file_bump(self):
        with open('file.txt', 'w') as f:
            f.write("0.0.0")
        bump.update_file_version("12.34.56")
        
        file_data = ""
        with open('file.txt', 'r') as f:
            file_data = f.read()

        self.assertEqual("12.34.56", file_data)
    def test_file_bump_with_text(self):
        with open('file.txt', 'w') as f:
            f.write("version = 0.0.0")
        bump.update_file_version("12.34.56")
        
        file_data = ""
        with open('file.txt', 'r') as f:
            file_data = f.read()

        self.assertEqual("version = 12.34.56", file_data)
    def test_file_bump_with_multiline(self):
        with open('file.txt', 'w') as f:
            f.write("version = 0.0.0\n#An example second line\nThird line!")
        bump.update_file_version("12.34.56")
        
        file_data = ""
        with open('file.txt', 'r') as f:
            file_data = f.read()

        self.assertEqual("version = 12.34.56", file_data.split('\n')[0])
    
def create_git_environment():
    subprocess.call(['rm', '-rf', './.git'])
    subprocess.call(['git', 'init'])
    subprocess.call(['touch', 'file.txt'])
    subprocess.call(['git', 'config', '--global', 'user.name', 'unit-test'])
    subprocess.call(['git', 'config', '--global', 'user.email', 'unit-test@rightbrainnetworks.com'])
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
