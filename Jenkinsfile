library('pipeline-library')

pipeline {
  options { timestamps() }
  agent any
  environment {

    GITHUB_URL = 'git@github.com:RightBrain-Networks/auto-semver.git'
    GITHUB_KEY = 'rbn-ops github'
    DOCKER_CREDENTIALS = 'rbnopsDockerHubToken'
    PYPI_CREDENTIALS = 'rbn_pypi_token'

    SERVICE = 'auto-semver'
    SELF_SEMVER_TAG = "master" //Image tag to use for self-versioning
    
  } 
  stages {
    //Runs versioning in docker container
    stage('Self Version') {
      steps {
        withCredentials([usernamePassword(credentialsId: env.DOCKER_CREDENTIALS, usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
          sh("docker login -u ${DOCKER_USERNAME} -p ${DOCKER_PASSWORD}")
        }
        runAutoSemver("rightbrainnetworks/auto-semver:${SELF_SEMVER_TAG}")
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
        script
        {
          dockerImage = docker.build("rightbrainnetworks/auto-semver:${env.VERSION}")
        }
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
    stage('Test') {
      agent {
          docker {
              image "rightbrainnetworks/auto-semver:${env.VERSION}"
          }
      }
      steps
      {
        dir('semver')
        {
          sh 'python tests.py'
        }
      }
      post{
        // Update Git with status of test stage.
        success {
          updateGithubCommitStatus(GITHUB_URL, 'Passed test stage', 'SUCCESS', 'Test')
        }
        failure {
          updateGithubCommitStatus(GITHUB_URL, 'Failed test stage', 'FAILURE', 'Test')
        }
      }
    }
    stage('Push')
    {
      steps {

          // Authenticate & push to DockerHub
          withCredentials([usernamePassword(credentialsId: env.DOCKER_CREDENTIALS, usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
            sh("docker login -u ${DOCKER_USERNAME} -p ${DOCKER_PASSWORD}")
            script
            {
              dockerImage.push("${env.VERSION}")
            }
          }

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
    stage('Release')
    {
      when {
          expression {
              "${env.SEMVER_STATUS}" == "0" && "${env.BRANCH_NAME}"  == "master"
          }
      }
      steps
      {
        script
        {
          dockerImage.push('latest')
        }

        // Create GitHub Release & Upload Artifacts
        createGitHubRelease('rbn-opsGitHubToken', 'RightBrain-Networks/auto-semver', "${env.SEMVER_RESOLVED_VERSION}",
          "${env.SEMVER_RESOLVED_VERSION}", ["auto-semver.tar.gz" : "dist/semver-${env.SEMVER_NEW_VERSION}.tar.gz"])


        // Upload package to PyPi
        script
        {
          docker.image("rightbrainnetworks/auto-semver:${env.VERSION}").inside()
          {
            withCredentials([string(credentialsId: env.PYPI_CREDENTIALS, variable: 'PYPI_PASSWORD')]) {
              sh("twine upload dist/* --verbose -u __token__ -p ${PYPI_PASSWORD}")
            }
          }
        }
      }
      post
      {
        // Update Git with status of release stage.
        success {
            updateGithubCommitStatus(GITHUB_URL, 'Passed release package stage', 'SUCCESS', 'Release')
        }
        failure {
            updateGithubCommitStatus(GITHUB_URL, 'Failed release package stage', 'FAILURE', 'Release')
        }
      }
    }
  }
 post { 
   success { updateGithubCommitStatus(GITHUB_URL, 'Passed build and test', 'SUCCESS') }
   failure { updateGithubCommitStatus(GITHUB_URL, 'Failed build and test', 'FAILURE') }
  }
  
}
