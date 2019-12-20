library('pipeline-library')

pipeline {
  options { timestamps() }
  agent any
  environment {
    SERVICE = 'auto-semver'
    GITHUB_URL = 'git@github.com:RightBrain-Networks/auto-semver.git'
    DOCKER_REGISTRY = credentials('RbnDockerRegistry')
    //Image tag to use for self-versioning
    SELF_SEMVER_TAG = "develop"
    
  }
  stages {
    //Runs versioning in docker container
    stage('Self Version') {
      steps {
        runAutoSemver("${env.DOCKER_REGISTRY}/auto-semver:${SELF_SEMVER_TAG}")
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
        sh "docker build ${getDockerBuildFlags()} -t ${env.DOCKER_REGISTRY}/${env.SERVICE}:${env.VERSION} ."


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
            sh "docker push ${env.DOCKER_REGISTRY}/${env.SERVICE}:${env.VERSION}"
            script
            {
              if("${env.BRANCH_NAME}" == "develop")
              {
                sh "docker tag ${env.DOCKER_REGISTRY}/${env.SERVICE}:${env.VERSION} ${env.DOCKER_REGISTRY}/${env.SERVICE}:latest"
                sh "docker push ${env.DOCKER_REGISTRY}/${env.SERVICE}:latest"
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
    stage('Publish Release')
    {
      when {
          expression {
              "${env.SEMVER_STATUS}" == "0" && "${env.BRANCH_NAME}"  == "master"
          }
      }
      steps
      {
        createGitHubRelease('rbn-opsGitHubToken', 'RightBrain-Networks/auto-semver', "${env.SEMVER_RESOLVED_VERSION}",
          "${env.SEMVER_RESOLVED_VERSION}", ["auto-semver.tar.gz" : "dist/${env.SERVICE}-*.tar.gz"])
      }
      
    }
    stage('Push Version and Tag') {
        steps {
            echo "The current branch is ${env.BRANCH_NAME}."
            gitPushTags('rbn-ops github')
        }
    }
  }
 post { 
   success { updateGithubCommitStatus(GITHUB_URL, 'Passed build and test', 'SUCCESS') }
   failure { updateGithubCommitStatus(GITHUB_URL, 'Failed build and test', 'FAILURE') }
  }
  
}
