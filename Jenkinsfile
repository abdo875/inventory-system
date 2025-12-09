pipeline {
    agent any

    environment {
        IMAGE_NAME = "abdelrahman121/inventory-backend"
    }

    stages {

        /* ========== CHECKOUT ========== */
        stage('Checkout') {
            steps {
                git branch: 'k8s-deployment',
                    url: 'https://github.com/abdo875/inventory-system.git'
            }
        }

        /* ========== BUILD & PUSH ========== */
        stage('Build & Push Docker Image') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', 
                                                 usernameVariable: 'DOCKER_USER', 
                                                 passwordVariable: 'DOCKER_PASS')]) {

                    script {
                        sh """
                            echo "==> Building Docker Image"
                            docker build -t ${IMAGE_NAME}:${BUILD_NUMBER} backend/
                            docker tag ${IMAGE_NAME}:${BUILD_NUMBER} ${IMAGE_NAME}:latest

                            echo "==> Logging into DockerHub"
                            echo ${DOCKER_PASS} | docker login -u ${DOCKER_USER} --password-stdin

                            echo "==> Pushing Images"
                            docker push ${IMAGE_NAME}:${BUILD_NUMBER}
                            docker push ${IMAGE_NAME}:latest
                        """
                    }
                }
            }
        }

        /* ========== DEPLOY VIA ANSIBLE ========== */
        stage('Deploy to EC2 via Ansible') {
            steps {
                withCredentials([sshUserPrivateKey(credentialsId: 'aws-key', keyFileVariable: 'EC2_KEY')]) {
                    script {
                        sh """
                            echo "==> Running Ansible Deployment"
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
