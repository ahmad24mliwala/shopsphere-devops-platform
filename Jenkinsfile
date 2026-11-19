pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        USER_SERVICE_URL = 'http://shopsphere-user:8000'
        PRODUCT_SERVICE_URL = 'http://shopsphere-product:8000'
        ORDER_SERVICE_URL = 'http://shopsphere-order:8000'
        PAYMENT_SERVICE_URL = 'http://shopsphere-payment:8000'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Test Dependencies') {
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install -r requirements-dev.txt
                '''
            }
        }

        stage('Run API and Integration Tests') {
            steps {
                sh '''
                    . .venv/bin/activate
                    pytest -v
                '''
            }
        }

        stage('Deploy to EC2') {
            steps {
                withCredentials([
                    sshUserPrivateKey(
                        credentialsId: 'shopsphere-deploy-ssh',
                        keyFileVariable: 'SSH_KEY',
                        usernameVariable: 'SSH_USER'
                    )
                ]) {
                    sh '''
                        set -eu

                        ssh -i "$SSH_KEY" \
                            -o IdentitiesOnly=yes \
                            -o BatchMode=yes \
                            -o StrictHostKeyChecking=yes \
                            -o UserKnownHostsFile=/var/jenkins_home/.ssh/known_hosts \
                            -T "$SSH_USER@172.31.38.252" "shopsphere-deploy"
                    '''
                }
            }
        }
    }

    post {
        always {
            echo 'ShopSphere Jenkins pipeline finished.'
        }
        success {
            echo 'Tests and deployment completed successfully.'
        }
        failure {
            echo 'Pipeline failed. Review the console output.'
        }
    }
}
