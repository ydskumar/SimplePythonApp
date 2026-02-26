def PREVIOUS_IMAGE = "none"

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
                withCredentials([usernamePassword(
                credentialsId: 'DockerHubCred',
                usernameVariable: 'DOCKER_USER',
                passwordVariable: 'DOCKER_PASS'
                )]) {
                
                sh 'docker build -t ${DOCKER_USER}/my-app:${BUILD_NUMBER} .'                
                }
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

        stage('Capture Previous Version') {
            steps {
                script {
                    PREVIOUS_IMAGE = sh(
                        script: "docker inspect --format='{{.Config.Image}}' ${CONTAINER_NAME} 2>/dev/null || echo 'none'",
                        returnStdout: true
                    ).trim()
                    echo "Previous image: ${PREVIOUS_IMAGE}"
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
                script {
                        try {
                        echo 'Deploying to test environment...'
                        withCredentials([usernamePassword(
                            credentialsId: 'DockerHubCred',
                            usernameVariable: 'DOCKER_USER',
                            passwordVariable: 'DOCKER_PASS'
                        )]) {
                            sh '''       
                            NETWORK_NAME=$(docker inspect jenkins --format='{{range $k,$v := .NetworkSettings.Networks}}{{println $k}}{{end}}')             
                            docker rm -f $CONTAINER_NAME > /dev/null 2>&1 || exit 0
                            docker pull $DOCKER_USER/$IMAGE_NAME:${BUILD_NUMBER}
                            docker run -d --network $NETWORK_NAME -e APP_VERSION=${BUILD_NUMBER} -p 8081:8081 --name $CONTAINER_NAME $DOCKER_USER/$IMAGE_NAME:${BUILD_NUMBER}                   
                        '''
                        } 
                    } catch (err) {
                        echo "Deployment failed. Attempting rollback..."

                        if (PREVIOUS_IMAGE != "none") {

                            sh """
                                docker rm -f ${CONTAINER_NAME} || true
                                docker run -d \
                                --network jenkins-custom_default \
                                -p 8081:8081 \
                                --name ${CONTAINER_NAME} \
                                ${PREVIOUS_IMAGE}
                            """

                            echo "Validating rollback..."

                            def rollbackStatus = sh(
                                script: '''
                                    for i in {1..10}; do
                                        status=$(curl -s -o /dev/null -w "%{http_code}" http://my-app-container:8081/health)
                                        if [ "$status" = "200" ]; then
                                            exit 0
                                        fi
                                        sleep 2
                                    done
                                    exit 1
                                ''',
                                returnStatus: true
                            )

                            if (rollbackStatus != 0) {
                                error("Rollback failed! System is unstable!")
                            }

                            echo "Rollback successful. Previous version restored."
                        }

                        error("Deployment failed. Rolled back successfully.")
                    }
                }      
                               
            }
        }

        stage('Health Check') {
            steps {
                    script {
                        def status = sh(
                            script: '''
                                for i in {1..30}; do
                                    status=$(curl -s -o /dev/null -w "%{http_code}" http://my-app-container:8081/health)
                                    if [ "$status" = "200" ]; then
                                        echo "App ready"
                                        exit 0
                                    fi

                                    echo "Not ready yet... ($i)"
                                    sleep 2
                                done

                                echo "Health timeout"
                                exit 1
                            ''',
                            returnStatus: true
                        )

                        if (status != 0) {
                            echo "Health failed. Rolling back..."

                            if (PREVIOUS_IMAGE != "none") {
                                sh """
                                    docker rm -f ${CONTAINER_NAME} || true
                                    docker run -d \
                                    --network jenkins-custom_default \
                                    -p 8081:8081 \
                                    --name ${CONTAINER_NAME} \
                                    ${PREVIOUS_IMAGE}
                                """
                            }

                            error("Health check failed. Rolled back.")
                        }
                    }
                }
        }
        
        stage('API Tests') {
            steps {
                script {
                    try {
                        sh '''
                            . venv/bin/activate
                            python -m pytest tests/test_api.py
                        '''
                    } catch (err) {
                        echo "API tests failed. Initiating rollback..."
                        rollback()
                        error("API tests failed after deployment. Rolled back.")
                    }
                }
            }
        }

        stage('Stability Check') {
            steps {
                script {
                    echo "Monitoring stability for 30 seconds..."

                    def stable = sh(
                        script: '''
                            for i in {1..15}; do
                                status=$(curl -s -o /dev/null -w "%{http_code}" http://my-app-container:8081/health)
                                if [ "$status" != "200" ]; then
                                    exit 1
                                fi
                                sleep 2
                            done
                            exit 0
                        ''',
                        returnStatus: true
                    )

                    if (stable != 0) {
                        error("Application became unstable after deployment!")
                    }

                    echo "Application stable."
                }
            }
        }

        stage('Cleanup') {
            steps {
                //sh "docker rm -f ${CONTAINER_NAME} || true"
                cleanWs()
            }
        }
    }

    post {        
        success {
        echo "Release ${BUILD_NUMBER} deployed successfully."
        }
        failure {
            echo "Release ${BUILD_NUMBER} failed. Check logs."
        }
    }
}