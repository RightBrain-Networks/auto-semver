import argparse
import re
import subprocess
from semver.logger import logging, logger, console_logger
from semver.utils import get_tag_version, get_file_version, DEVNULL
from semver import SemVer

def get_version(build=0,version_format=None,dot=False):
    version = get_tag_version()

    # Get the commit hash of the version 
    v_hash = subprocess.Popen(['git', 'rev-list', '-n', '1', version], stdout=subprocess.PIPE,
                             stderr=DEVNULL, cwd='.').stdout.read().decode('utf-8').rstrip()
    # Get the current commit hash
    c_hash = subprocess.Popen(['git', 'rev-parse', 'HEAD'], stdout=subprocess.PIPE,
                             stderr=DEVNULL, cwd='.').stdout.read().decode('utf-8').rstrip()

    # If the version commit hash and current commit hash
    # do not match return the branch name else return the version
    if v_hash != c_hash:
        logger.debug("v_hash and c_hash do not match!")
        branch = subprocess.Popen(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], stdout=subprocess.PIPE,
                            stderr=DEVNULL, cwd='.').stdout.read().decode('utf-8').rstrip()
        if version_format:
            semver = SemVer()
            semver.merged_branch = branch
            version_type = semver.get_version_type()
            p = subprocess.Popen(['bumpversion', '--dry-run', '--verbose', '--current-version', get_tag_version(), version_type], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd='.')
            bump_output = p.stderr.read().decode()
            next_version = match = re.search("New version will be '([0-9]*.[0-9]*.[0-9]*)'", bump_output).group(1)
    
            if version_format == 'npm':
                return "{}-{}.{}".format(next_version,branch.replace('/','-'),build)
            if version_format == 'maven':
                qualifier = 'SNAPSHOT' if build == 0 else build
                return "{}-{}-{}".format(next_version,branch.replace('/','-'),qualifier)
        if dot:
            branch = branch.replace('/','.')
        return branch
    return version


def main():
    parser = argparse.ArgumentParser(description='Get Version or Branch.')
    parser.add_argument('-d', '--dot', help='Switch out / for . to be used in docker tag', action='store_true', dest='dot')
    parser.add_argument('-D', '--debug', help='Sets logging level to DEBUG', action='store_true', dest='debug', default=False)
    parser.add_argument('-f', '--format', help='Format for pre-release version syntax', choices=['npm','maven'], default=None)
    parser.add_argument('-b', '--build-number', help='Build number, used in pre-releases', default=0)
   
    args = parser.parse_args()

    if args.debug:
        console_logger.setLevel(logging.DEBUG)

    print(get_version(args.build_number,args.format,args.dot))

if __name__ == '__main__':
    try: main()
    except: raise

