
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

        stage('Install Security Scanner') {
            steps {
                sh '''
                    . .venv/bin/activate
                    python -m pip install -r requirements-security.txt
                '''
            }
        }

        stage('Audit Python Dependencies') {
            steps {
                sh '''
                    . .venv/bin/activate
                    for file in services/*/requirements.txt; do
                        echo "Auditing $file"
                        pip-audit -r "$file"
                    done
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

        stage('Archive Docker SBOM Reports') {
            steps {
                sh '''
                    set -eu
                    mkdir -p sbom-reports

                    cp /var/jenkins_home/shopsphere-sboms/*.cdx sbom-reports/

                    test "$(find sbom-reports -maxdepth 1 -type f -name '*.cdx' | wc -l)" -eq 4

                    echo "All four SBOM reports copied successfully."
                    ls -lh sbom-reports/
                '''

                archiveArtifacts artifacts: 'sbom-reports/*.cdx',
                                 fingerprint: true
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
