class SemverException(Exception):
    """Semver base exception"""
    pass


class NoMergeFoundException(SemverException):
    """No merge found in commit message"""
    pass


class NotMainBranchException(SemverException):
    """Not on main branch"""
    pass


class NoGitFlowException(SemverException):
    """No git flow branch found"""
    pass
