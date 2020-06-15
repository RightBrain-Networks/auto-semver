import subprocess
from semver.logger import logging, logger, console_logger

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

