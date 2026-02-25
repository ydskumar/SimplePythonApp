pipeline {
    agent {
        docker {
            image 'python:3.13'
        }
    }

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
                checkout scmGit(branches: [[name: '*/master']], extensions: [], userRemoteConfigs: [[credentialsId: 'GitHubCred', url: 'https://github.com/ydskumar/SimplePythonApp.git']])
            }
        }

        stage('Install Dependencies') {
    steps {
        sh 'pip install -r requirements.txt'
    }
}
        stage('Run Unit Tests') {
            steps {
                echo 'Running unit tests...'
                sh 'pytest --cov=app --cov-fail-under=80'               
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image...'
                sh "docker build -t $IMAGE_NAME ."
            }
        }
        stage('Deploy to Test (Local Container)') {
            steps {
                echo 'Deploying to test environment...'
                sh '''
                    docker rm -f $CONTAINER_NAME > /dev/null 2>&1 || exit 0
                    docker run -d -p 5000:5000 --name $CONTAINER_NAME $IMAGE_NAME
                '''
            }
        }

        stage('Wait for Container') {
    steps {
        echo 'Waiting for container to start...'
        sh 'sleep 5'
    }
}
        stage('Run API Requests Test') {
            steps {
                echo 'Running API requests test...'
               sh 'pytest tests/test_api.py'                
            }
        }
    }

    post {
        always {
            echo 'Cleaning up...'
            sh 'docker rm -f $CONTAINER_NAME > /dev/null 2>&1 || exit 0'
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