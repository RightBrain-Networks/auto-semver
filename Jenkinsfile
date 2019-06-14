library('pipeline-library@feature/add-with-ecr')

pipeline {
  options { timestamps() }
  agent any
  environment {
    SERVICE = 'auto-semver'
    GITHUB_KEY = 'autosemverDeployKey'
    GITHUB_URL = 'https://github.com/RightBrain-Networks/auto-semver'
    DOCKER_REGISTRY = '356438515751.dkr.ecr.us-east-1.amazonaws.com'
    VERSION = ""


    //Image tag to use for self-versioning
    SELF_SEMVER_TAG = "HEAD"
    
  }
  stages {
    //Pulls docker image for self-versioning
    stage("Pull Versioning Image")
    {
        steps
        {
          withEcr {
            sh "docker pull ${DOCKER_REGISTRY}/auto-semver:${SELF_SEMVER_TAG}"
          }
        }
    }
    //Runs versioning in docker container
    stage('Version') {
        agent {
            docker {
                image "${DOCKER_REGISTRY}/auto-semver:${SELF_SEMVER_TAG}"
            }
        }
      steps {
        // runs the automatic semver tool which will version, & tag,
        runAutoSemver()

        //Grabs current version
        script
        {
            env.VERSION = getVersion('-d')
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

        // Docker build flags are set via the getDockerBuildFlags() shared library.
        sh "docker build ${getDockerBuildFlags()} -t ${env.DOCKER_REGISTRY}/${env.SERVICE}:${env.VERSION} ."

        //sh "tar -czvf ${env.SERVICE}-${getVersion('-d')}.tar.gz deployer"
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
    stage('Push Version and Tag') {
        steps {
            echo "The current branch is ${env.BRANCH_NAME}."
            gitPush(env.GITHUB_KEY, env.BRANCH_NAME, true)
        }
    }
  }
  post {
      always {
          removeDockerImages()
          cleanWs()
      }
  }
  
}
