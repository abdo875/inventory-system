pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "DOCKERHUB_USERNAME/inventory-system"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build & Push Docker Image') {
            steps {
                script {
                    sh """
                      docker build -t ${DOCKER_IMAGE}:latest backend/
                      echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                      docker push ${DOCKER_IMAGE}:latest
                    """
                }
            }
        }

        stage('Deploy to EC2 via Ansible') {
            steps {
                script {
                    sh """
                      ansible-playbook -i infra/hosts infra/deploy.yml \
                      --private-key \$SSH_KEY
                    """
                }
            }
        }
    }
}
