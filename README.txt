Semantic Versioning
----------


Usage
-----

docker build -t semver .
docker run -v FULL_PATH_TO_LOCAL_REPO:/application_repo semver

# after this finishes must go to FULL_PATH_TO_LOCAL_REPO and push yourself
git push origin develop
git push origin --tags
