import re
from pathlib import Path, StrPath

# To use a consistent encoding
from codecs import open

# Always prefer setuptools over distutils
from setuptools import setup, find_packages


here = Path(__file__).resolve().parent

# Get the long description from the README file
with open(Path(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()


def find_version(*file_path: StrPath) -> str:
    """
    Searches for the semantic version within the given path
    :param file_path: Path to the file to search
    :return: Semantic version as string
    """
    version_file: str = open(Path(here, *file_path), "r").read()
    version_match = re.search(r"^version = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if not version_match:
        raise RuntimeError("Unable to find version string.")

    return version_match.group(1)


setup(
    name="semver",
    version=find_version("semver", "__init__.py"),
    description="Automatic Semantic Versioner",
    long_description=long_description,
    url="https://github.com/RightBrain-Networks/auto-semver",
    # Author details
    author="RightBrain Networks",
    author_email="cloud@rightbrainnetworks.com",
    # Choose your license
    license="Apache2.0",
    # ======== #
    # Metadata #
    # ======== #
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        # Development Status
        "Development Status :: 3 - Alpha",
        # Audience
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: Software Development :: Build Tools",
        # Supported Python Versions
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    keywords=["Semantic", "Version", "Git", "Auto-Versioning"],
    # ======= #
    # Package #
    # ======= #
    packages=find_packages(exclude=["contrib", "docs", "tests"]),
    install_requires=["argparse>=1.4.0"],
    package_data={},
    entry_points={
        "console_scripts": [
            "semver = semver:main",
            "semver_get_version = semver.get_version:main",
        ],
    },
)
