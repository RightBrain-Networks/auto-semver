import argparse

from semver.logger import logging, console_logger
from semver import SemVer
from semver.utils import setting_to_array
from semver.scm.git import Git


def main():
    parser = argparse.ArgumentParser(description="Get Version or Branch.")
    parser.add_argument(
        "-d",
        "--dot",
        help="Switch out / for . to be used in docker tag",
        action="store_true",
        dest="dot",
    )
    parser.add_argument(
        "-D",
        "--debug",
        help="Sets logging level to DEBUG",
        action="store_true",
        dest="debug",
        default=False,
    )
    parser.add_argument(
        "-f",
        "--format",
        help="Format for pre-release version syntax",
        choices=["npm", "maven", "docker"],
        default=None,
    )
    parser.add_argument(
        "-b", "--build-number", help="Build number, used in pre-releases", default=0
    )

    args = parser.parse_args()

    if args.debug:
        console_logger.setLevel(logging.DEBUG)

    semver = SemVer(
        scm=Git(),
        main_branches=setting_to_array("main_branches"),
        major_branches=setting_to_array("major_branches"),
        minor_branches=setting_to_array("minor_branches"),
        patch_branches=setting_to_array("patch_branches"),
    )

    print(semver.get_version(args.build_number, args.format, args.dot))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        raise e
