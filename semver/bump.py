from enum import IntEnum
import subprocess, os
from semver.logger import logging, logger, console_logger


try: 
    from configparser import ConfigParser
except ImportError:
    # Python < 3
    from ConfigParser import ConfigParser

def bump_version(version, index=2, tag_repo = True, update_files=True):
    v = version.split('.')

    # Bump version
    v[index] = str(int(v[index]) + 1)

    # Reset subversions
    i = len(v) - 1
    while i > index:
        v[i] = '0'
        i = i - 1

    # Get new version
    new_version = '.'.join(v)
    logger.debug("new_version: {}", new_version)
    # Tag new version
    if tag_repo and version != new_version:
        logger.debug("Tagging repository.")
        p = subprocess.Popen(['git', 'tag', new_version], cwd='.')
        p.wait()
    
    # Update local files
    if update_files:
        update_file_version(new_version, version)

    return new_version

def update_file_version(new_version, version="0.0.0"):
    # Open up config file
    logger.debug("Update file version with {}", new_version)
    config = ConfigParser()
    config.read('./.bumpversion.cfg')

    for section in config.sections():
        if len(section) > 17 and section[0:17] == "bumpversion:file:":
            file_name = section[17:]
            if os.path.isfile(file_name):
                # Get search val from config
                search_val = config.get(section, "search")
                search_val = process_config_string(search_val, new_version, version)

                # Get replace val from config
                replace_val = config.get(section, "replace")
                replace_val = process_config_string(replace_val, new_version, version)

                # Update replace values in file
                with open(file_name, 'r') as file:
                    filedata = file.read()
                filedata =filedata.replace(search_val,replace_val)
                with open(file_name, 'w') as file:
                    file.write(filedata)                
            else:
                logger.warning("Tried to version file: `" + file_name + "` but it doesn't exist!")

def process_config_string(cfg_string, new_version, version):
    return cfg_string.replace("{new_version}", new_version).replace("{current_version}", version)