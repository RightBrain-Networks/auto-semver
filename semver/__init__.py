import argparse
import re
import subprocess
import sys
import traceback
from typing import List, Union

import toml

from semver.logger import logging, logger, console_logger
from semver.scm import SCM
from semver.scm.git import Git

from semver.semver import SemVer
from semver.utils import setting_to_array

from semver.exceptions import (
    NoMergeFoundException,
    NotMainBranchException,
    NoGitFlowException,
)

version = "0.0.0"


def main():
    """Main entry point for the application"""
    parser = argparse.ArgumentParser(description="Bump Semantic Version.")
    parser.add_argument(
        "-n", "--no-push", help="Do not try to push", action="store_false", dest="push"
    )
    parser.add_argument(
        "-g",
        "--global-user",
        help="Set git user at a global level, helps in jenkins",
        action="store_true",
        dest="global_user",
    )
    parser.add_argument(
        "-D",
        "--debug",
        help="Sets logging level to DEBUG",
        action="store_true",
        dest="debug",
        default=False,
    )
    args = parser.parse_args()

    scm: SCM = Git(global_user=args.global_user)

    app = SemVer(
        scm=scm,
        main_branches=setting_to_array("main_branches"),
        major_branches=setting_to_array("major_branches"),
        minor_branches=setting_to_array("minor_branches"),
        patch_branches=setting_to_array("patch_branches"),
    )

    if args.debug:
        console_logger.setLevel(logging.DEBUG)
    try:
        app.run(push=args.push)
    except Exception as e:
        logger.error(e)
        if args.debug:
            tb = sys.exc_info()[2]
            traceback.print_tb(tb)
        if e is NoMergeFoundException:
            exit(1)
        elif e == NotMainBranchException:
            exit(2)
        elif e == NoGitFlowException:
            exit(3)
        else:
            exit(128)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        raise
