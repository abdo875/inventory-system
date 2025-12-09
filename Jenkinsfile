pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "abdelrahman121/inventory-backend"
    }

    stages {

        stage('Validate Branch') {
            when {
                expression {
                    return env.GIT_BRANCH == "origin/k8s-deployment" ||
                           env.BRANCH_NAME == "k8s-deployment"
                }
            }
            steps {
                echo "Deploying branch: ${env.GIT_BRANCH}"
            }
        }

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build & Push Docker Image') {
            when {
                expression { 
                    return env.GIT_BRANCH == "origin/k8s-deployment" || 
                           env.BRANCH_NAME == "k8s-deployment"
                }
            }
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-creds',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS'
                    )
                ]) {
                    script {
                        sh """
                            echo "==> Building Docker Image"
                            docker build -t ${DOCKER_IMAGE}:latest backend/

                            echo "==> Logging into DockerHub"
                            echo "${DOCKER_PASS}" | docker login -u "${DOCKER_USER}" --password-stdin

                            echo "==> Pushing to DockerHub (Safe Mode)"
                            docker push --max-concurrent-uploads 1 ${DOCKER_IMAGE}:latest
                        """
                    }
                }
            }
        }

        stage('Deploy to EC2 via Ansible') {
            when {
                expression { 
                    return env.GIT_BRANCH == "origin/k8s-deployment" ||
                           env.BRANCH_NAME == "k8s-deployment"
                }
            }
            steps {
                withCredentials([
                    sshUserPrivateKey(
                        credentialsId: 'aws-key',
                        keyFileVariable: 'SSH_KEY'
                    )
                ]) {
                    script {
                        sh """
                            echo "==> Running Ansible Deployment"
                            export ANSIBLE_HOST_KEY_CHECKING=False

                            ansible-playbook \
                              -i infra/hosts \
                              infra/deploy.yml \
                              --private-key \$SSH_KEY
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
