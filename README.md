# Semantic Versioning


# Usage

# FULL_PATH_TO_LOCAL_REPO gives container access to repo to be versioned
# FULL_PATH_TO_SSH_FOLDER gives container access to ssh keys to be able to push repo
docker build -t semver .
docker run -v FULL_PATH_TO_LOCAL_REPO:/application_repo -v FULL_PATH_TO_SSH_FOLDER:/root/.ssh semver

# after this finishes must go to FULL_PATH_TO_LOCAL_REPO and push yourself
git push origin develop
git push origin --tags
