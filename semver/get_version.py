import argparse
import subprocess
try:
    from configparser import ConfigParser
except ImportError:
    # Python < 3
    from ConfigParser import ConfigParser
try:
    from subprocess import DEVNULL # py3k
except ImportError:
    import os
    DEVNULL = open(os.devnull, 'wb')


def get_version(dot=False):
    config = ConfigParser()
    config.read('./.bumpversion.cfg')
    version = config.get('bumpversion', 'current_version')
    # Get the commit hash of the version 
    v_hash = subprocess.Popen(['git', 'rev-list', '-n', '1', version], stdout=subprocess.PIPE,
                             stderr=DEVNULL, cwd='.').stdout.read().decode('utf-8').rstrip()
    # Get the current commit hash
    c_hash = subprocess.Popen(['git', 'rev-parse', 'HEAD'], stdout=subprocess.PIPE,
                             stderr=DEVNULL, cwd='.').stdout.read().decode('utf-8').rstrip()
    # If the version commit hash and current commit hash
    # do not match return the branch name else return the version
    if v_hash != c_hash:
        b = subprocess.Popen(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], stdout=subprocess.PIPE,
                            stderr=DEVNULL, cwd='.').stdout.read().decode('utf-8').rstrip()
        if dot:
            b = b.replace('/','.')
        return b
    return version


def main():
    parser = argparse.ArgumentParser(description='Get Version or Branch.')
    parser.add_argument('-d','--dot', help='Switch out / for . to be used in docker tag', action='store_true', dest='dot')
    args = parser.parse_args()

    print(get_version(args.dot))

if __name__ == '__main__':
    try: main()
    except: raise
