
#!/usr/bin/env groovy

/**
 * Runs "semver -n". Upon successful return, pushes changes from remote repo
 * to ${env.GIT_BRANCH}.
 *
 * @param dockerImage (Optional) The docker image with semver to run in environment
 *
 */

// Run Auto Semver
def call(dockerImage = "rightbrainnetworks/auto-semver:latest") {

    def docker_image = docker.image(dockerImage)
    docker_image.pull()
    docker_image.inside{

      def RETURN_STATUS
      def regex = '^\\s*current_version\\s*=\\s*\\K[^\\s]+'

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