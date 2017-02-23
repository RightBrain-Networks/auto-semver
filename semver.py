import subprocess


def semver():
    # setup git user
    p = subprocess.Popen(['git', 'config', 'user.email',
                          '"versioner@semver.com"'], cwd='/application_repo')
    p = subprocess.Popen(['git', 'config', 'user.name', '"Semantic Versioner"'],
                          cwd='/application_repo')
    p.wait()

    # version repo
    p = subprocess.Popen(['bumpversion', 'patch'], cwd='/application_repo')
    p.wait()

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
    return None


if __name__ == '__main__':
    semver()
