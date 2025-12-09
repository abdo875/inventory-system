pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "abdo875/inventory-system"   // غيّر لاسمك لو مختلف
    }

    stages {

        /****************************************
         * 1) CHECK BRANCH
         ****************************************/
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

        /****************************************
         * 2) CHECKOUT SOURCE
         ****************************************/
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        /****************************************
         * 3) BUILD & PUSH DOCKER IMAGE
         ****************************************/
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
                        credentialsId: 'dockerhub_creds',
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

                            echo "==> Pushing to DockerHub"
                            docker push ${DOCKER_IMAGE}:latest
                        """
                    }
                }
            }
        }

        /****************************************
         * 4) DEPLOY TO EC2 USING ANSIBLE
         ****************************************/
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
                        credentialsId: 'ec2_ssh_key',
                        keyFileVariable: 'SSH_KEY',
                        usernameVariable: 'SSH_USER'
                    )
                ]) {
                    script {
                        sh """
                            echo "==> Deploying with Ansible"
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

    /****************************************
     * 5) POST STATUS
     ****************************************/
    post {
        success {
            echo "Deployment completed successfully 🎉"
        }
        failure {
            echo "❌ Deployment failed!"
        }
    }
}
