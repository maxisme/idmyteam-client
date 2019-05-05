def virtualenv = "~/.virtualenvs/idmyteam-server/${env.BUILD_ID}"

void setBuildStatus(String message, String state) {
  step([
      $class: "GitHubCommitStatusSetter",
      reposSource: [$class: "ManuallyEnteredRepositorySource", url: "https://github.com/maxisme/idmyteam-server"],
      contextSource: [$class: "ManuallyEnteredCommitContextSource", context: "ci/jenkins/build-status"],
      errorHandlers: [[$class: "ChangingBuildStatusErrorHandler", result: "UNSTABLE"]],
      statusResultSource: [ $class: "ConditionalStatusResultSource", results: [[$class: "AnyBuildResult", message: message, state: state]] ]
  ]);
}

pipeline {
  agent any

  environment {
    PYTHONPATH="$WORKSPACE/settings/:$WORKSPACE/web/:$PYTHONPATH"
    SETTINGS_FILE="${WORKSPACE}/conf/test_local.yaml"
  }

  stages {
    stage('venv-setup') {
      steps {
        sh """
        virtualenv --system-site-packages ${virtualenv}
        . ${virtualenv}/bin/activate
        pip3 install -r test_requirements.txt --cache-dir ~/.pip-cache
        """
      }
    }
    stage('test') {
      steps {
        sh """
        . ${virtualenv}/bin/activate
        pytest tests/ -m "not rpi"
        """
      }
    }
  }
  post {
    always {
        sh "rm -rf ${virtualenv}"
    }
    success {
      setBuildStatus("Build succeeded", "SUCCESS");
    }
    failure {
        setBuildStatus("Build failed", "FAILURE");
    }
  }
}