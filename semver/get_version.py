import argparse
from semver.logger import logging, logger, console_logger
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

def get_tag_version():
    config = ConfigParser()
    config.read('./.bumpversion.cfg')
    tag_expression = config.get('bumpversion','tag_name').replace('{new_version}','[0-9]*.[0-9]*.[0-9]*')

    logger.debug("Tag expression: " + str(tag_expression))

    # Default version is `0.0.0` or what is found in 
    version = get_file_version(config)
    
    # If a version is found in tags, use that the lastest tagged version
    tagged_versions = subprocess.Popen(['git','tag','--sort=v:refname', '-l',tag_expression],
        stdout=subprocess.PIPE, stderr=DEVNULL, cwd=".").stdout.read().decode('utf-8').rstrip().split('\n')
    if len(tagged_versions) > 0 and tagged_versions[-1] != "":
        version = tagged_versions[-1]
        
    logger.debug("Tag Version: " + str(version))
    return version

def get_file_version(config):
    version = config.get('bumpversion','current_version')
    if not version:
        config.set('bumpversion', 'current_version', '0.0.0')
        version = '0.0.0'
    return version

def get_version(dot=False):
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
        b = subprocess.Popen(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], stdout=subprocess.PIPE,
                            stderr=DEVNULL, cwd='.').stdout.read().decode('utf-8').rstrip()
        if dot:
            b = b.replace('/','.')
        return b
    return version


def main():
    parser = argparse.ArgumentParser(description='Get Version or Branch.')
    parser.add_argument('-d','--dot', help='Switch out / for . to be used in docker tag', action='store_true', dest='dot')
    parser.add_argument('-D', '--debug', help='Sets logging level to DEBUG', action='store_true', dest='debug', default=False)
    args = parser.parse_args()

    if args.debug:
        console_logger.setLevel(logging.DEBUG)

    print(get_version(args.dot))

if __name__ == '__main__':
    try: main()
    except: raise
