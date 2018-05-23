Semantic Versioning
===================

Usage
=====

FULL\_PATH\_TO\_LOCAL\_REPO gives container access to repo to be versioned
==========================================================================

FULL\_PATH\_TO\_SSH\_FOLDER gives container access to ssh keys to be able to push repo
======================================================================================

docker build -t semver . docker run -v
FULL\_PATH\_TO\_LOCAL\_REPO:/application\_repo -v
FULL\_PATH\_TO\_SSH\_FOLDER:/root/.ssh semver

after this finishes must go to FULL\_PATH\_TO\_LOCAL\_REPO and push yourself
============================================================================

git push origin develop git push origin --tags
