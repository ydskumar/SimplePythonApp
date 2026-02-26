pipeline {
    agent any

    environment {
        IMAGE_NAME = 'my-app'
        CONTAINER_NAME = 'my-app-container'
        DOCKERHUB_USER = credentials('DockerHubCred')
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
                sh '''
                    python -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run Unit Tests') {
            steps {
                echo 'Running unit tests...'
                sh '''                   
                    . venv/bin/activate
                    python -m pytest --cov=app --cov-fail-under=80
                '''
               
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image...'
                // sh 'docker build -t $IMAGE_NAME:${BUILD_NUMBER} .'
                sh 'docker build -t $DOCKER_USER/$IMAGE_NAME:${BUILD_NUMBER} .'
            }
        }

        stage('Push Image') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'DockerHubCred',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh '''
                        echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin
                        docker push $DOCKER_USER/$IMAGE_NAME:${BUILD_NUMBER}
                    '''
                }
            }
        }

        stage('Manual Approval') {
            steps {
                input message: "Approve deployment to Test?", ok: "Deploy"
            }
        }

        stage('Deploy to Test (Local Container)') {
            steps {
                echo 'Deploying to test environment...'
                sh '''                    
                    docker rm -f $CONTAINER_NAME > /dev/null 2>&1 || exit 0
                    docker pull $DOCKER_USER/$IMAGE_NAME:${BUILD_NUMBER}
                    docker run -d --network jenkins-custom_default -p 8081:8081 --name $CONTAINER_NAME $DOCKER_USER/$IMAGE_NAME:${BUILD_NUMBER}
                '''
            }
        }

        stage('Health Check') {
            steps {
                sh '''
                    for i in {1..20}; do
                        status=$(curl -s -o /dev/null -w "%{http_code}" http://${CONTAINER_NAME}:8081/health)
                        if [ "$status" = "200" ]; then
                            echo "Application is healthy!"
                            exit 0
                        fi
                        echo "Waiting..."
                        sleep 2
                    done
                    echo "Health check failed!"
                    exit 1
                '''
            }
        }
        
        stage('Run API Requests Test') {
            steps {
                echo 'Running API requests test...'
               sh '''
                    . venv/bin/activate
                    python -m pytest tests/test_api.py
                '''
            }
        }

        stage('Cleanup') {
            steps {
                sh "docker rm -f ${CONTAINER_NAME} || true"
                cleanWs()
            }
        }
    }

    post {        
        success {
            echo 'Pipeline succeeded!'
        }
        failure {
            echo 'Pipeline failed.'
        }
    }
}