pipeline {
  agent any

  environment {
    DOCKERHUB = "abdelrahman121"
    IMAGE = "${DOCKERHUB}/inventory-backend"
    PATH = "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
  }

  stages {

    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Docker Login') {
      steps {
        withCredentials([usernamePassword(
          credentialsId: 'dockerhub-creds',
          usernameVariable: 'DOCKER_USER',
          passwordVariable: 'DOCKER_PASS'
        )]) {
          sh '''
            echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin
          '''
        }
      }
    }

    stage('Build') {
      steps {
        sh '''
          DOCKER_BUILDKIT=0 docker build -t ${IMAGE}:${GIT_COMMIT} ./backend
          docker tag ${IMAGE}:${GIT_COMMIT} ${IMAGE}:latest
        '''
      }
    }

    stage('Unit Tests') {
      steps {
        sh 'echo "Run tests here if exist (pytest...)"'
      }
    }

    stage('Push') {
      steps {
        withCredentials([usernamePassword(
          credentialsId: 'dockerhub-creds',
          usernameVariable: 'DOCKER_USER',
          passwordVariable: 'DOCKER_PASS'
        )]) {
          sh '''
            docker push ${IMAGE}:${GIT_COMMIT}
            docker push ${IMAGE}:latest
          '''
        }
      }
    }

    stage('Deploy') {
  steps {
    withCredentials([sshUserPrivateKey(
      credentialsId: 'aws-key',
      keyFileVariable: 'SSH_KEY',
      usernameVariable: 'SSH_USER'
    )]) {
      sh '''
        ansible-playbook -i infra/hosts infra/deploy.yml \
        --extra-vars "image_backend=${IMAGE}:latest" \
        --extra-vars "ansible_ssh_user=$SSH_USER ansible_ssh_private_key_file=$SSH_KEY"
      '''
    }
  }
}


  post {
    always {
      sh 'docker image prune -f || true'
    }
  }
}
