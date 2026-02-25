pipeline {
    agent any

    environment {
        IMAGE_NAME = 'my-app'
        CONTAINER_NAME = 'my-app-container'
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out code...'
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                echo 'Installing dependencies...'
                sh 'pip install -r requirements.txt'
            }
        }
        stage('Run Unit Tests') {
            steps {
                echo 'Running unit tests...'
                sh 'python -m pytest --cov=app --cov-fail-under=80'
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image...'
                sh "docker build -t ${IMAGE_NAME} ."
            }
        }
        stage('Deploy to Test (Local Container)') {
            steps {
                echo 'Deploying to test environment...'
                sh '''
                    docker rm -f ${CONTAINER_NAME} || true
                    docker run -d -p 5000:5000 --name ${CONTAINER_NAME} ${IMAGE_NAME}
                '''
            }
        }
        stage('Run API Requests Test') {
            steps {
                echo 'Running API requests test...'
                sh 'sleep 5' // Wait for the container to start
                sh 'python -m pytest tests/test_api.py'
            }
        }
    }

    post {
        always {
            echo 'Cleaning up...'
            sh 'docker rm -f ${CONTAINER_NAME} || true'
        }
        success {
            echo 'Pipeline succeeded!'
        }
        failure {
            echo 'Pipeline failed.'
        }
    }
}