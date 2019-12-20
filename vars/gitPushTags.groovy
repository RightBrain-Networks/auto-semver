#!/usr/bin/env groovy

/**
 * Pushes tags to a repo
 *
 * @param creds The Jenkins Git credentials to use.
 */

def call(creds) {

  withCredentials([usernamePassword(credentialsId: creds, usernameVariable: 'GIT_USERNAME', passwordVariable: 'GIT_PASSWORD')]) {
    def gitOrigin = sh(script: "git remote", returnStdout: true).trim()
    // Need to remove the protocol to add in user name and host
    def gitHost = sh(script: "git remote get-url ${gitOrigin}", returnStdout: true).trim().replaceFirst('https://','')
    // Push tags to branch
    sh("git push https://${env.GIT_USERNAME}:${env.GIT_PASSWORD}@${gitHost} --tags") 
  }
}
