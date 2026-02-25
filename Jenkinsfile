pipeline {
    agent any

    environment {
        IMAGE_NAME = 'my-app'
        CONTAINER_NAME = 'my-app-container'
    }

    options {
        skipDefaultCheckout()
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out code...'
                cleanWs()
                checkout scmGit(branches: [[name: '*/master']], extensions: [], userRemoteConfigs: [[url: 'file:///C:/Dev/Docker/My-Simple-Python-App']])
            }
        }

        stage('Install Dependencies') {
            steps {
                echo 'Installing dependencies...'
                bat 'pip install -r requirements.txt'
            }
        }
        stage('Run Unit Tests') {
            steps {
                echo 'Running unit tests...'
                bat 'python -m pytest --cov=app --cov-fail-under=80'
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image...'
                bat "docker build -t %IMAGE_NAME% ."
            }
        }
        stage('Deploy to Test (Local Container)') {
            steps {
                echo 'Deploying to test environment...'
                bat '''
                    docker rm -f %CONTAINER_NAME% || true
                    docker run -d -p 5000:5000 --name %CONTAINER_NAME% %IMAGE_NAME% 
                '''
            }
        }
        stage('Run API Requests Test') {
            steps {
                echo 'Running API requests test...'
                bat 'timeout /t 5' // Wait for the container to start
                bat 'python -m pytest tests/test_api.py'
            }
        }
    }

    post {
        always {
            echo 'Cleaning up...'
            bat 'docker rm -f %CONTAINER_NAME% || true'
            cleanWs()
        }
        success {
            echo 'Pipeline succeeded!'
        }
        failure {
            echo 'Pipeline failed.'
        }
    }
}