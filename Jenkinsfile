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
    }

    post {
        always {
            echo 'ShopSphere Jenkins pipeline finished.'
        }
        success {
            echo 'All tests passed.'
        }
        failure {
            echo 'Pipeline failed. Review the test output.'
        }
    }
}
