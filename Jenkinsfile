library('pipeline-library')

pipeline {
  options { timestamps() }
  agent any
  environment {
    SERVICE = 'auto-semver'
    GITHUB_KEY = 'rbn-ops github'
    GITHUB_URL = 'git@github.com:RightBrain-Networks/auto-semver.git'


    //Image tag to use for self-versioning
    SELF_SEMVER_TAG = "develop"
    
  }
  stages {
    //Runs versioning in docker container
    stage('Self Version') {
      steps {
          withCredentials([string(credentialsId: 'RbnDockerRegistry', variable: 'DOCKER_REGISTRY')]) {
            runAutoSemver("${DOCKER_REGISTRY}/auto-semver:${SELF_SEMVER_TAG}")
          }
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

        withCredentials([string(credentialsId: 'RbnDockerRegistry', variable: 'DOCKER_REGISTRY')]) {
          // Docker build flags are set via the getDockerBuildFlags() shared library.
          sh "docker build ${getDockerBuildFlags()} -t ${DOCKER_REGISTRY}/${env.SERVICE}:${env.VERSION} ."
        }

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
        withEcr {
          withCredentials([string(credentialsId: 'RbnDockerRegistry', variable: 'DOCKER_REGISTRY')]) {
            sh "docker push ${DOCKER_REGISTRY}/${env.SERVICE}:${env.VERSION}"
            script
            {
              if("${env.BRANCH_NAME}" == "develop")
              {
                sh "docker tag ${DOCKER_REGISTRY}/${env.SERVICE}:${env.VERSION} ${DOCKER_REGISTRY}/${env.SERVICE}:latest"
                sh "docker push ${DOCKER_REGISTRY}/${env.SERVICE}:latest"
              }
            }
          }
        }
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
