import argparse
import re
import subprocess
from semver.get_version import get_tag_version

try: 
    from configparser import ConfigParser
except ImportError:
    # Python < 3
    from ConfigParser import ConfigParser

version = 'develop'


# Define common exceptions;
NO_MERGE_FOUND = Exception('No merge found')
NOT_MAIN_BRANCH = Exception('Not merging into a main branch')
NO_GIT_FLOW = Exception('No git flow branch found')

class SemVer(object):

    GET_COMMIT_MESSAGE = re.compile(r"Merge (branch|pull request) '?(.+)'? (into|from) ([\w/-]+)")
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
        print('Main branch is ' + branch)
        matches = self.GET_COMMIT_MESSAGE.search(message)
        if matches:
            if str(matches.group(4)) == branch:
                self.merged_branch = matches.group(2)
            else:
                self.merged_branch = matches.group(4)
            self.main_branch = branch
        return bool(matches)

    # based on branches involved see what type of versioning should be done
    def get_version_type(self):
        print('Merged branch is ' + self.merged_branch)

 
        #Get GitHub repo's owner from url
        repoOwner = None
        remoteUrl = subprocess.Popen(['git', 'config', '--get', 'remote.origin.url'], stdout=subprocess.PIPE).stdout.read().decode('utf-8').rstrip()
        if "github.com" in remoteUrl:
            repoOwner = re.search("(?<=github.com(:|\/))(.*)(?=\/.*.git)", remoteUrl).group(0)

        for prefix in self.major_branches:
            if self.merged_branch.startswith(prefix + '/') or self.merged_branch.startswith(str(repoOwner) + '/' + prefix + '/'):
                self.version_type = 'major'
                return True
        for prefix in self.minor_branches:
            if self.merged_branch.startswith(prefix + '/') or self.merged_branch.startswith(str(repoOwner) + '/' + prefix + '/'):
                self.version_type = 'minor'
                return True
        for prefix in self.patch_branches:
            if self.merged_branch.startswith(prefix + '/') or self.merged_branch.startswith(str(repoOwner) + '/' + prefix + '/'):
                self.version_type = 'patch'
                return True
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
        # Update .bumpconfig
        pattern = re.compile("current_version = [0-9.]*")
        current_config = re.search(pattern, config_file)
        if current_config:
            config_file.replace(current_config.group(0), "current_version = " + get_tag_version())
        else:
            config_file.replace("[bumpversion]","[bumpversion]\ncurrent_version = " + get_tag_version())
        with open(".bumpversion.cfg", "w") as file:
            file.write(config_file)

        # version repo
        p = subprocess.Popen(['bumpversion', self.version_type],
                             cwd='.')
        p.wait()
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
        args = parser.parse_args()
        SemVer(global_user=args.global_user).run(push=args.push)
    except Exception as e:
        print(e)
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
