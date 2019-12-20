![Release Version](https://img.shields.io/github/v/release/RightBrain-Networks/auto-semver) ![GitHub Downloads](https://img.shields.io/github/downloads/RightBrain-Networks/auto-semver/total)

# Automatic Semantic Versioning

This code repository extends/wraps the bumpversion library to automatically determine which type of increment (Major, Minor, Patch) to perform based on git branch names.
The tool uses the git log to determine if the last commit was a merge into a main line branch, and if it was, detect the name of the branch being merged in. If the name of the branch begins with one of the key words provided to the configuration file, a new version is produced.

***It is important to note that the tool performs actions on a local Git repository. After completion, it will be necessary to do a `git push --tags` if a commit and/or tag are created***

## Setup

auto-semver is a pip installable package to install, make sure pip is installed and simply run:

`pip install path/to/auto-semver-<version>tar.gz`

## Configuration

There are two configuration files that must appear in the top directory of repository for which we want to update the version. These files are `VERSION` and `.bumpversion.cfg`.

Below is an example configuration of a `.bumpversion.cfg` file using commits:

```ini
[bumpversion]
current_version = 0.0.0
commit = False
tag = True
tag_name = {new_version}
message = Bump version: {current_version} -> {new_version}

[bumpversion:file:VERSION]
search = version=0.0.0
replace = version={new_version}

[semver]
main_branches = master
major_branches = major
minor_branches = feature
patch_branches = hotfix, bugfix
```

### bumpversion

```ini
[bumpversion]
current_version = 0.0.0
commit = False
tag = True
tag_name = v{new_version}
message = Bump version: {current_version} -> {new_version}
```

The `current_version` exists to tell bumpversion what the current version is. To have auto-semver manage this value, set it to `0.0.0`. The `commit` and `tag` options determine whether to create a new Git commit and a new Git tag, respectively. The `tag_name` represents what the name of the Git tag will be, and by default is set to `{new_version}`, which will be substitued with the new version during runtime. This can be changed as desired - for example, `v{new_version}` could resolve to `v1.15.5`. The `message` option is what the message used if there is a git commit.

### File updates

```ini
[bumpversion:file:VERSION]
search = version={current_version}
replace = version={new_version}

[bumpversion:file:example_app/__init__.py]
search = version = '{current_version}'
replace = version = '{new_version}'
```

The `search` and `replace` options describe how the tool will update the version in the `VERSION` file. The format must match the format of the contents of the `VERSION` file. The `{current_version}` represents the old version of the application and the `{new_version}` represents the version after it is updated. These will be substituted with the actual values at runtime.

You can use this to update mutiple files are runtime.

### Branch Based Versioning

```ini
[semver]
main_branches = master
major_branches = major
minor_branches = feature
patch_branches = hotfix, bugfix
```

The last four options are exceptionally important - they tie in to how the branching was done in the Git repository. Each one is expected to be a comma-delimited list. The `main_branches` option represents the Git branches that feature branches will be merged into. Functionally, the tool will make commits on the currently checked out branch during runtime, which must match one of the specified branches.

In order for the tool to make a determination on how to increment the version, it looks at the most recent commit, checks to determine if it was a merge from another branch, then compares the branch name to the values listed for the options. If the merged in branch name was prefixed with one of the values for `major_branches`, the major version number is incremented and the other numbers are set to 0. If the merged in branch name was prefixed with one of the values for `minor_branche`', the minor version number is incremented and the patch number is set to 0. If the merged in branch name was prefixed with one of the values for `patch_branches`, the patch number will be incremented.

Below is an example configuration in the VERSION file:

```VERSION
version=1.15.5
```

The value for `version` represents the current version of the application, and should match the current_version in the `.bumpversion.cfg`.

## Usage

<a name="semver"></a>
#### semver

The `semver` command runs auto-semver in the current working directory.

The exit code of auto-semver determines the output.

**Exit codes**:

|Value|Meaning|
|---|---|
|0|Successfully ran auto-semver|
|1|No merge found|
|2|Not a main branch|
|3|No version branch name found|
|128|Unknown error occured|

#### Flags

`-n`

Does not push after versioning.

`-h`

Shows helps screen.

<a name="semver_get_version"></a>
### semver_get_version

The `semver_get_version` command returns the version number if the `semver` command exited `0`. If `semver` exited anything else, `semver_get_version` will return the branch name.

#### Flags

`-d`

Replaces `/` with `.` in branch names. For example, `feature/test` becomes `feature.test`

### Jenkins Shared Library

This repository is also home to a Jenkins shared library to assit in running auto-semver.

```groovy
library('auto-semver')

pipeline
{
    options { timestamps() }
    agent any
    environment {
        GIT_KEY = 'githubKey' // Git credentials
    }
    stages{
        stage('Version') {
            steps {
                runAutoSemver()
            }
        }
        stage('Push Version and Tag') {
            steps {
                gitPushTags(env.GIT_KEY)
            }
        }
    }
}
```

#### runAutoSemver( String _dockerImage_ )

**dockerImage:** The Docker image and tag to run auto-semver with. By default, it pulls `rightbrainnetworks/auto-semver:latest`.