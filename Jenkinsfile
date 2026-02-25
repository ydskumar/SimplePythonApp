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

        stage('Debug Workspace') {
    steps {
        bat 'dir'
    }
}

stage('Check Agent OS') {
    steps {
        bat 'echo %OS%'
    }
}

        stage('Checkout') {
            steps {
                echo 'Cleaning workspace...'
                cleanWs()

                echo 'Checking out code...'
                checkout scmGit(
                    branches: [[name: '*/master']],
                    userRemoteConfigs: [[
                        url: 'file:///C:/Dev/Docker/My-Simple-Python-App'
                    ]]
                )
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
                echo 'Stopping old container (if exists)...'
                bat 'docker rm -f %CONTAINER_NAME% >nul 2>&1 || exit /b 0'

                echo 'Starting container...'
                bat "docker run -d -p 8081:8081 --name %CONTAINER_NAME% %IMAGE_NAME%"
            }
        }

        stage('Run API Requests Test') {
            steps {
                echo 'Waiting for container to start...'
                bat 'timeout /t 5 /nobreak'

                echo 'Running API tests...'
                bat 'python -m pytest tests/test_api.py'
            }
        }
    }

    post {
        always {
            echo 'Cleaning up container...'
            bat 'docker rm -f %CONTAINER_NAME% >nul 2>&1 || exit /b 0'

            echo 'Cleaning workspace...'
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