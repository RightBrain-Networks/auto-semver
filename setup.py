import re
from pathlib import Path
from typing import List

# To use a consistent encoding
from codecs import open

# Always prefer setuptools over distutils
from setuptools import setup


here = Path(__file__).resolve().parent

# Get the long description from the README file
with open(Path(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()


def find_version(*file_path: List[str]) -> str:
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


setup(version=find_version("semver", "__init__.py"))
