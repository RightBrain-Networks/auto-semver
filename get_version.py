from ConfigParser import ConfigParser


def get_version():
    config = ConfigParser()
    config.read('.bumpversion.cfg')
    version = config.get('bumpversion', 'current_version')
    return version


if __name__ == '__main__':
    print get_version()
