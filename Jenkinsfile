library('pipeline-library')

pipeline {
  options { timestamps() }
  agent any
  environment {
    SERVICE = 'auto-semver'
    GITHUB_KEY = 'autosemverDeployKey'
    GITHUB_URL = 'git@github.com:RightBrain-Networks/auto-semver.git'
    DOCKER_REGISTRY = '356438515751.dkr.ecr.us-east-1.amazonaws.com'


    //Image tag to use for self-versioning
    SELF_SEMVER_TAG = "bugfix.pipeline"
    
  }
  stages {
    //Runs versioning in docker container
    stage('Self Version') {
      steps {
        script
        {

          def docker_image = docker.image("${DOCKER_REGISTRY}/auto-semver:${SELF_SEMVER_TAG}")
          docker_image.inside{

            def RETURN_STATUS
            def regex = '^\\s*current_version\\s*=\\s*\\K[^\\s]+'
            env.SEMVER_OLD_VERSION = sh(script: "grep -Po '${regex}' .bumpversion.cfg", returnStdout: true).trim()

            RETURN_STATUS = sh(script: "semver -n", returnStatus: true)
            echo "Semver Return Status: ${RETURN_STATUS}"
            env.SEMVER_STATUS = RETURN_STATUS
            switch (RETURN_STATUS) {
              case "0":
                echo 'Versioned will push after build/test.'
                break
              case "128":
                echo 'Unknown Semver Failure'
                sh 'exit 1'
                break
              default:
                echo 'No versioning required.'
                break
            }

            env.SEMVER_NEW_VERSION = sh(script: "grep -Po '${regex}' .bumpversion.cfg", returnStdout: true).trim()
            env.SEMVER_RESOLVED_VERSION = getVersion('-d')

            env.VERSION = getVersion('-d')
            }
          }
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
        sh "aws s3 cp `find ./dist/ -name semver-*` s3://rbn-ops-pkg-us-east-1/${env.SERVICE}/${env.SERVICE}-${env.VERSION}.tar.gz"
        
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
