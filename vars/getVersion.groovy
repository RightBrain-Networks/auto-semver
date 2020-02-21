#!/usr/bin/env groovy

/** 
 * Run semver_get_version to return the current version of the repository
 *
 * @param flags Flags or arguments to pass to semver_get_version
 * @return "1.9.2"
 */
def call(flags='') {
    def VERSION
    VERSION = sh(returnStdout: true, script: "semver_get_version ${flags}")
    return VERSION.trim()
}