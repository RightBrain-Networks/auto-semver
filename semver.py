import re
import subprocess


class SemVer(object):

    GET_COMMIT_MESSAGE = re.compile(r"Merge branch '(.+)' into ([^\n]+)")

    def __init__(self):
        self.merged_branch = None
        self.main_branch = None
        self.version_type = None

    def get_branches(self):
        p = subprocess.Popen(['git', 'log', '-1'], stdout=subprocess.PIPE,
                             cwd='/application_repo')
        message = p.stdout.read()
        matches = self.GET_COMMIT_MESSAGE.search(message)
        if matches:
            self.merged_branch = matches.group(1)
            self.main_branch = matches.group(2)
        return bool(matches)

    def get_version_type(self):
        if self.merged_branch.startswith('feature/'):
            self.version_type = 'minor'
        elif self.merged_branch.startswith('hotfix/'):
            self.version_type = 'patch'
        return bool(self.version_type)

    def setup_git_user(self):
        # setup git user
        p = subprocess.Popen(['git', 'config', 'user.email',
                              '"versioner@semver.com"'],
                             cwd='/application_repo')
        p = subprocess.Popen(['git', 'config', 'user.name',
                              '"Semantic Versioner"'],
                             cwd='/application_repo')
        p.wait()
        return self

    def version_repo(self):
        # version repo
        p = subprocess.Popen(['bumpversion', self.version_type],
                             cwd='/application_repo')
        p.wait()
        return self

    def commit_and_push(self):
        '''
        ' this will be difficult to do because we'd need to setup credentials in
        '  docker container for git remote repo access
        '
        # push versioning commit
        p = subprocess.Popen(['git', 'push', 'origin', 'develop'],
                             cwd='/application_repo')
        p.wait()

        # push versioning tag
        p = subprocess.Popen(['git', 'push', 'origin', '--tags'],
                             cwd='/application_repo')
        p.wait()
        '''
        return self

    def run(self):
        if not self.get_branches():
            raise Exception('No merge found')
        if self.main_branch not in \
         ['develop', 'env-test', 'env-stage', 'env-prod']:
            raise Exception('Not merging into a main branch')
        if not self.get_version_type():
            raise Exception('No git flow branch found')
        self.setup_git_user()
        self.version_repo()
        return self


if __name__ == '__main__':
    SemVer().run()
