library('pipeline-library')

pipeline {
  options { timestamps() }
  agent any
  environment {
    SERVICE = 'auto-semver'
    GITHUB_URL = 'git@github.com:RightBrain-Networks/auto-semver.git'
    DOCKER_REGISTRY = credentials('RbnDockerRegistry')
    GITHUB_KEY = 'rbn-ops github'
    DOCKER_CREDENTIALS = 'rbnopsDockerHubToken'

    //Image tag to use for self-versioning
    SELF_SEMVER_TAG = "master"
    
  } 
  stages {
    //Runs versioning in docker container
    stage('Self Version') {
      steps {
        withCredentials([usernamePassword(credentialsId: env.DOCKER_CREDENTIALS, usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
          sh("docker login -u ${DOCKER_USERNAME} -p ${DOCKER_PASSWORD}")
        }
        runAutoSemver("rbnops/auto-semver:${SELF_SEMVER_TAG}")
      }
      post{
        // Update Git with status of version stage.
        success {
          updateGithubCommitStatus(GITHUB_URL, 'Passed version stage', 'SUCCESS', 'Version')
        }
        failure {
          updateGithubCommitStatus(GITHUB_URL, 'Failed version stage', 'FAILURE', 'Version')
        }
      }
    }
    stage('Build') {
      steps {

        echo "Building ${env.SERVICE} docker image"

        // Docker build flags are set via the getDockerBuildFlags() shared library.
        sh "docker build ${getDockerBuildFlags()} -t rightbrainnetworks/auto-semver:${env.VERSION} ."


        sh "python setup.py sdist"
      }
      post{
        // Update Git with status of build stage.
        success {
          updateGithubCommitStatus(GITHUB_URL, 'Passed build stage', 'SUCCESS', 'Build')
        }
        failure {
          updateGithubCommitStatus(GITHUB_URL, 'Failed build stage', 'FAILURE', 'Build')
        }
      }
    }
    stage('Push')
    {
      steps {

          // Authenticate & push to DockerHub
          withCredentials([usernamePassword(credentialsId: env.DOCKER_CREDENTIALS, usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
            sh("""
              docker login -u ${DOCKER_USERNAME} -p ${DOCKER_PASSWORD}
              docker push rightbrainnetworks/auto-semver:${env.VERSION}
              """)
          }
        
          // Copy artifact to S3
          sh "aws s3 cp `ls -t ./dist/semver-* | head -1` s3://rbn-ops-pkg-us-east-1/${env.SERVICE}/${env.SERVICE}-${env.VERSION}.tar.gz"
      }
      post
      {
        // Update Git with status of push stage.
        success {
            updateGithubCommitStatus(GITHUB_URL, 'Passed push stage', 'SUCCESS', 'Push')
        }
        failure {
            updateGithubCommitStatus(GITHUB_URL, 'Failed push stage', 'FAILURE', 'Push')
        }
      }
    }
    stage('Publish Release')
    {
      when {
          expression {
              "${env.SEMVER_STATUS}" == "0" && "${env.BRANCH_NAME}"  == "master"
          }
      }
      steps
      {
        // Create GitHub Release & Upload Artifacts
        createGitHubRelease('rbn-opsGitHubToken', 'RightBrain-Networks/auto-semver', "${env.SEMVER_RESOLVED_VERSION}",
          "${env.SEMVER_RESOLVED_VERSION}", ["auto-semver.tar.gz" : "dist/${env.SERVICE}-*.tar.gz"])

        // Update DockerHub latest tag
        sh("""
            docker tag rightbrainnetworks/auto-semver:${env.VERSION} rightbrainnetworks/auto-semver:latest
            docker push rightbrainnetworks/auto-semver:latest
          """)
      }
      post
      {
        // Update Git with status of release stage.
        success {
            updateGithubCommitStatus(GITHUB_URL, 'Passed release stage', 'SUCCESS', 'Release')
        }
        failure {
            updateGithubCommitStatus(GITHUB_URL, 'Failed release stage', 'FAILURE', 'Release')
        }
      }
    }
    stage('Push Version and Tag') {
        steps {
            echo "The current branch is ${env.BRANCH_NAME}."
            gitPushTags(env.GITHUB_KEY)
        }
    }
  }
 post { 
   success { updateGithubCommitStatus(GITHUB_URL, 'Passed build and test', 'SUCCESS') }
   failure { updateGithubCommitStatus(GITHUB_URL, 'Failed build and test', 'FAILURE') }
  }
  
}
