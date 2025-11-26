pipeline {
  agent any
  environment {
    DOCKERHUB = "abdelrahman121"
    IMAGE = "${DOCKERHUB}/inventory-backend"
  }
  stages {
    stage('Checkout') {
      steps { checkout scm }
    }
    stage('Build') {
      steps {
        sh 'docker build -t ${IMAGE}:${GIT_COMMIT} ./backend'
        sh 'docker tag ${IMAGE}:${GIT_COMMIT} ${IMAGE}:latest'
      }
    }
    stage('Unit Tests') {
      steps {
        sh 'echo "Run tests here if exist (pytest...)"'
      }
    }
    stage('Push') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
          sh 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin'
          sh 'docker push ${IMAGE}:${GIT_COMMIT}'
          sh 'docker push ${IMAGE}:latest'
        }
      }
    }
    stage('Deploy') {
      steps {
        // call ansible from Jenkins (ansible should be installed on agent)
        sh 'ansible-playbook -i infra/hosts infra/deploy.yml --extra-vars "image_backend=${IMAGE}:latest"'
      }
    }
  }
  post {
    always {
      sh 'docker image prune -f'
    }
  }
}
