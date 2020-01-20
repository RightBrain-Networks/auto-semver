"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""


import re 
from os import path

from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open



here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

def read(*parts):
    # intentionally *not* adding an encoding option to open
    # see here: https://github.com/pypa/virtualenv/issues/201#issuecomment-3145690
    return open(path.join(here, *parts), 'r').read()

def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^version = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

setup(
    name='semver-by-branch',
    version=find_version('semver','__init__.py'),
    description='Automatic Semantic Versioner',
    long_description=long_description,
    long_description_content_type="text/markdown",

    # The project's main homepage.
    url='https://github.com/RightBrain-Networks/auto-semver',

    # Author details
    author='RightBrain Networks',
    author_email='cloud@rightbrainnetworks.com',

    # Choose your license
    license='Apache2.0',

    # See https://pypi.org/classifiers/
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Build Tools'
    ],
    keywords='Semantic,Version,CICD,Pipeline,Versioning',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=[
        'bump2version>=0.5.11',
        'argparse>=1.2.1'
    ],
    package_data={},
    entry_points={
        'console_scripts': [
            'semver = semver:main',
            'semver_get_version = semver.get_version:main'
        ],
    },
)
