pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "abdelrahman121/inventory-backend"
    }

    stages {

        /******************************
         * Validate Branch
         ******************************/
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

        /******************************
         * Checkout
         ******************************/
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        /******************************
         * Build & Push Docker Image
         ******************************/
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
                        def TAG = "build-${env.BUILD_NUMBER}"

                        sh """
                            echo "==> Building Docker Image"
                            docker build -t ${DOCKER_IMAGE}:${TAG} backend/
                            docker tag ${DOCKER_IMAGE}:${TAG} ${DOCKER_IMAGE}:latest

                            echo "==> Logging into DockerHub"
                            echo "${DOCKER_PASS}" | docker login -u "${DOCKER_USER}" --password-stdin
                        """

                        echo "==> Pushing Docker Image with retry logic"

                        retry(3) {
                            sh """
                                docker push ${DOCKER_IMAGE}:${TAG}
                                docker push ${DOCKER_IMAGE}:latest
                            """
                        }
                    }
                }
            }
        }

        /******************************
         * Deploy to EC2 via Ansible
         ******************************/
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
                        keyFileVariable: 'SSH_KEY',
                        usernameVariable: 'SSH_USER'
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
