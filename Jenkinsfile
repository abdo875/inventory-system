pipeline {
    agent any

    environment {
        DOCKER_USER  = credentials('dockerhub-creds').username
        DOCKER_PASS  = credentials('dockerhub-creds').password
        SSH_KEY      = credentials('aws-key')
        IMAGE_NAME   = "abdelrahman121/inventory-backend"
    }

    stages {

        /* --------------------- CHECKOUT ---------------------- */
        stage('Checkout') {
            steps {
                git branch: 'k8s-deployment', url: 'https://github.com/abdo875/inventory-system.git'
            }
        }

        /* --------------------- BUILD IMAGE ---------------------- */
        stage('Build & Push Docker Image') {
            steps {
                script {
                    echo "==> Building Docker Image"
                    sh """
                        docker build -t ${IMAGE_NAME}:${BUILD_NUMBER} backend/
                        docker tag ${IMAGE_NAME}:${BUILD_NUMBER} ${IMAGE_NAME}:latest
                    """

                    echo "==> Logging into DockerHub"
                    sh """
                        echo ${DOCKER_PASS} | docker login -u ${DOCKER_USER} --password-stdin
                    """

                    echo "==> Pushing image..."
                    sh """
                        docker push ${IMAGE_NAME}:${BUILD_NUMBER}
                        docker push ${IMAGE_NAME}:latest
                    """
                }
            }
        }

        /* --------------------- DEPLOY TO EC2 ---------------------- */
        stage('Deploy to EC2 via Ansible') {
            steps {
                withCredentials([sshUserPrivateKey(credentialsId: 'aws-key', keyFileVariable: 'EC2_KEY')]) {
                    script {
                        echo "==> Running Ansible Deployment"

                        sh """
                            export ANSIBLE_HOST_KEY_CHECKING=False

                            ansible-playbook \
                                -i infra/hosts \
                                infra/deploy.yml \
                                --private-key ${EC2_KEY}
                        """
                    }
                }
            }
        }
    }

    post {
        success {
            echo "🎉 Deployment succeeded!"
        }
        failure {
            echo "❌ Deployment failed!"
        }
    }
}
