import argparse
import re
import subprocess
from enum import IntEnum
from semver.utils import get_tag_version
from semver.logger import logging, logger, console_logger
from semver.bump import bump_version

try: 
    from configparser import ConfigParser
except ImportError:
    # Python < 3
    from ConfigParser import ConfigParser

version = '0.0.0'

class VersionType(IntEnum):
    MAJOR = 0
    MINOR = 1
    PATCH = 2

# Define common exceptions;
NO_MERGE_FOUND = Exception('No merge found')
NOT_MAIN_BRANCH = Exception('Not merging into a main branch')
NO_GIT_FLOW = Exception('No git flow branch found')

# Important regex
GET_COMMIT_MESSAGE = re.compile(r"Merge (branch|pull request) '?([^']+)'? (into|from) (?:'(.+)'|[^\/]+\/([^\n\\]+))")

class SemVer(object):

    # Merge pull request #1 from RightBrain-Networks/feature/PLAT-185-versioning

    def __init__(self,global_user=False):
        self.global_user = '--local' if global_user else '--global'
        self.merged_branch = None
        self.main_branch = None
        self.version_type = None

        self.main_branches = self._setting_to_array('main_branches')
        self.major_branches = self._setting_to_array('major_branches')
        self.minor_branches = self._setting_to_array('minor_branches')
        self.patch_branches = self._setting_to_array('patch_branches')

    def _setting_to_array(self, setting):
        config = ConfigParser()
        config.read('./.bumpversion.cfg')
        value = config.get('semver', setting)
        # filter() removes empty string which is what we get if setting is blank
        return list(filter(bool, [v.strip() for v in value.split(',')]))

    # based on commit message see what branches are involved in the merge
    def get_branches(self):
        p = subprocess.Popen(['git', 'log', '-1'], stdout=subprocess.PIPE,
                             cwd='.')
        #check current branch
        b = subprocess.Popen(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], stdout=subprocess.PIPE,
                             cwd='.')
        message = str(p.stdout.read())
        branch = b.stdout.read().decode('utf-8').rstrip()
        logger.info('Main branch is ' + branch)
        matches = GET_COMMIT_MESSAGE.search(message)
        if matches:
            if str(matches.group(4)) == branch:
                self.merged_branch = matches.group(2)
            else:
                self.merged_branch = matches.group(5)
            self.main_branch = branch
        return bool(matches)

    # based on branches involved see what type of versioning should be done
    def get_version_type(self):
        logger.info('Merged branch is ' + self.merged_branch)

        merged_prefix = None
        matches = re.findall("[^\/]*/", self.merged_branch)
        if len(matches) >= 1:
            merged_prefix = matches[-1][0:-1]

        if merged_prefix:
            for prefix in self.major_branches:
                if prefix == merged_prefix:
                    self.version_type = VersionType.MAJOR
                    return self.version_type
            for prefix in self.minor_branches:
                if prefix == merged_prefix:
                    self.version_type = VersionType.MINOR
                    return self.version_type
            for prefix in self.patch_branches:
                if prefix == merged_prefix:
                    self.version_type = VersionType.PATCH
                    return self.version_type
        return False

    # setup git settings so we can commit and tag
    def setup_git_user(self):
        # setup git user
        p = subprocess.Popen(['git', 'config', self.global_user, 'user.email',
                              '"versioner@semver.com"'],
                             cwd='.')
        p = subprocess.Popen(['git', 'config', self.global_user, 'user.name',
                              '"Semantic Versioner"'],
                             cwd='.')
        p.wait()
        return self

    # use bumpversion to increment the appropriate version type
    def version_repo(self):
        config_file = ""
        with open(".bumpversion.cfg", "r") as file:
            config_file = file.read()

        # version repo
        logger.debug("Running bumpversion of type: " + self.version_type)
        bump_version(get_tag_version(), self.version_type)
        return self

    def commit_and_push(self):
        # push versioning commit
        p = subprocess.Popen(['git', 'push', 'origin', self.main_branch],
                             cwd='.')
        p.wait()

        # push versioning tag
        p = subprocess.Popen(['git', 'push', 'origin', '--tags'],
                             cwd='.')
        p.wait()
        return self

    # 1) get branches from last commit message
    # 2) see if we're merging into a main branch
    # 3) see what type of versioning we should do
    # 4) version the repo
    def run(self,push=True):
        if not self.get_branches():
            raise NO_MERGE_FOUND
        if self.main_branch not in self.main_branches:
            raise NOT_MAIN_BRANCH
        if not self.get_version_type():
            raise NO_GIT_FLOW
        if push:
            self.setup_git_user()
        self.version_repo()
        if push:
            self.commit_and_push()
        return self

def main():
    try:
        parser = argparse.ArgumentParser(description='Bump Semantic Version.')
        parser.add_argument('-n','--no-push', help='Do not try to push', action='store_false', dest='push')
        parser.add_argument('-g','--global-user', help='Set git user at a global level, helps in jenkins', action='store_true', dest='global_user')
        parser.add_argument('-D', '--debug', help='Sets logging level to DEBUG', action='store_true', dest='debug', default=False)
        args = parser.parse_args()


        if args.debug:
            console_logger.setLevel(logging.DEBUG)

        SemVer(global_user=args.global_user).run(push=args.push)
    except Exception as e:
        logger.error(e)
        if e == NO_MERGE_FOUND:
            exit(1)
        elif e == NOT_MAIN_BRANCH:
            exit(2)
        elif e == NO_GIT_FLOW:
            exit(3)
        else:
            exit(128)

if __name__ == '__main__':
    try: main()
    except: raise
