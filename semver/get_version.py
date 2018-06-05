import subprocess
try:
    from configparser import ConfigParser
except ImportError:
    # Python < 3
    from ConfigParser import ConfigParser


def get_version():
    config = ConfigParser()
    config.read('./.bumpversion.cfg')
    version = config.get('bumpversion', 'current_version')
    # Get the commit hash of the version 
    v_hash = subprocess.Popen(['git', 'rev-list', '-n', '1', version], stdout=subprocess.PIPE,
                             cwd='.').stdout.read().decode('utf-8').rstrip()
    # Get the current commit hash
    c_hash = subprocess.Popen(['git', 'rev-parse', 'HEAD'], stdout=subprocess.PIPE,
                             cwd='.').stdout.read().decode('utf-8').rstrip()
    # If the version commit hash and current commit hash
    # do not match return the branch name else return the version
    if v_hash != c_hash:
        b = subprocess.Popen(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], stdout=subprocess.PIPE,
                            cwd='.').stdout.read().decode('utf-8').rstrip()
        return b
    return version


def main():
    print(get_version())

if __name__ == '__main__':
    try: main()
    except: raise
