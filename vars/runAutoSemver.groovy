
#!/usr/bin/env groovy

/**
 * Runs "semver -n" and updates environment variables ${env.SEMVER_NEW_VERSION}, ${env.SEMVER_RESOLVED_VERSION},
 * ${env.VERSION}, and ${env.SEMVER_STATUS}
 *
 * @param dockerImage (Optional) The docker image with semver to run in environment
 *
 */

// Run Auto Semver
def call(dockerImage = "rightbrainnetworks/auto-semver:latest", debug = false) {

    def docker_image = docker.image(dockerImage)
    docker_image.pull()
    docker_image.inside{

      def args = ""
      if(debug)
      {
        args="--debug"
      }
      def RETURN_STATUS
      def regex = '^\\s*current_version\\s*=\\s*\\K[^\\s]+'

      RETURN_STATUS = sh(script: "semver -n ${args}", returnStatus: true)
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

      env.SEMVER_RESOLVED_VERSION = getVersion("-d ${args}")

      env.VERSION = env.SEMVER_RESOLVED_VERSION
    }

}