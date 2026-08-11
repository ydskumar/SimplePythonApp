def PREVIOUS_IMAGE = 'none'

pipeline {
    agent any

    parameters {
        string(
            name: 'GIT_REPO_URL',
            defaultValue: 'https://github.consilio.com/srkumar/SimplePythonApp.git',
            description: 'Git repository URL to checkout'
        )
        string(
            name: 'GIT_BRANCH',
            defaultValue: 'master',
            description: 'Git branch to build and deploy'
        )
        string(
            name: 'GIT_CRED_ID',
            defaultValue: 'GitHubCred',
            description: 'Jenkins credentials ID for Git checkout'
        )
        string(
            name: 'DOCKER_CRED_ID',
            defaultValue: 'DockerHubCred',
            description: 'Jenkins credentials ID for Docker Hub login'
        )
        booleanParam(
            name: 'SKIP_APPROVAL',
            defaultValue: false,
            description: 'Skip the manual approval gate before deploy'
        )
        booleanParam(
            name: 'LEAVE_CONTAINER_RUNNING',
            defaultValue: true,
            description: 'Leave the test container running after a successful deploy'
        )
    }

    options {
        skipDefaultCheckout()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timestamps()
    }

    environment {
        // Docker / deploy
        IMAGE_NAME             = 'mysimplepython-app'
        CONTAINER_NAME         = 'mysimplepython-app-container'
        DOCKER_NETWORK         = ''
        JENKINS_CONTAINER_NAME = 'jenkins'
        HOST_PORT              = '8081'
        APP_PORT               = '8081'
        HEALTH_PATH            = '/health'
        HEALTH_URL             = "http://${CONTAINER_NAME}:${APP_PORT}${HEALTH_PATH}"
        IMAGE_TAG              = "${env.BUILD_NUMBER}"

        // Quality / timing gates
        COVERAGE_MIN           = '80'
        HEALTH_RETRIES         = '30'
        STABILITY_CHECKS       = '15'
        APPROVAL_TIMEOUT_HOURS = '1'
    }

    stages {
        stage('Checkout') {
            steps {
                echo "Checking out ${params.GIT_BRANCH} from ${params.GIT_REPO_URL}"
                cleanWs()
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: "*/${params.GIT_BRANCH}"]],
                    userRemoteConfigs: [[
                        url: params.GIT_REPO_URL,
                        credentialsId: params.GIT_CRED_ID
                    ]]
                ])
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
                echo "Running unit tests (coverage >= ${COVERAGE_MIN}%)..."
                sh '''
                    . venv/bin/activate
                    python -m pytest --cov=app --cov-fail-under="${COVERAGE_MIN}"
                '''
            }
        }

        stage('Docker Login') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: params.DOCKER_CRED_ID,
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh 'echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin'
                }
            }
        }

        stage('Build & Push Image') {
            steps {
                echo "Building and pushing ${IMAGE_NAME}:${IMAGE_TAG}..."
                withCredentials([usernamePassword(
                    credentialsId: params.DOCKER_CRED_ID,
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh '''
                        docker build -t "$DOCKER_USER/$IMAGE_NAME:${IMAGE_TAG}" .
                        docker push "$DOCKER_USER/$IMAGE_NAME:${IMAGE_TAG}"
                    '''
                }
            }
        }

        stage('Capture Previous Version') {
            steps {
                script {
                    PREVIOUS_IMAGE = sh(
                        script: "docker inspect --format='{{.Config.Image}}' ${env.CONTAINER_NAME} 2>/dev/null || echo 'none'",
                        returnStdout: true
                    ).trim()
                    env.PREVIOUS_IMAGE = PREVIOUS_IMAGE

                    def network = sh(
                        script: '''
                            docker inspect "$JENKINS_CONTAINER_NAME" --format='{{range $name, $_ := .NetworkSettings.Networks}}{{println $name}}{{end}}' 2>/dev/null \
                            | head -n1 \
                            || true
                        ''',
                        returnStdout: true
                    ).trim()

                    if (!network) {
                        error("Unable to detect Docker network for ${env.JENKINS_CONTAINER_NAME}.")
                    }

                    env.DOCKER_NETWORK = network

                    echo "Previous image: ${PREVIOUS_IMAGE}"
                    echo "Docker network: ${env.DOCKER_NETWORK}"
                    echo "Health URL: ${env.HEALTH_URL}"
                }
            }
        }

        stage('Manual Approval') {
            when {
                expression { return !params.SKIP_APPROVAL }
            }
            steps {
                script {
                    timeout(time: env.APPROVAL_TIMEOUT_HOURS.toInteger(), unit: 'HOURS') {
                        input message: "Approve deployment of ${env.IMAGE_NAME}:${env.IMAGE_TAG} to Test?", ok: 'Deploy'
                    }
                }
            }
        }

        stage('Deploy to Test (Local Container)') {
            steps {
                script {
                    try {
                        echo 'Deploying to test environment...'
                        withCredentials([usernamePassword(
                            credentialsId: params.DOCKER_CRED_ID,
                            usernameVariable: 'DOCKER_USER',
                            passwordVariable: 'DOCKER_PASS'
                        )]) {
                            sh '''
                                docker rm -f "$CONTAINER_NAME" >/dev/null 2>&1 || true
                                docker pull "$DOCKER_USER/$IMAGE_NAME:${IMAGE_TAG}"
                                docker run -d \
                                  --network "$DOCKER_NETWORK" \
                                  -e "APP_VERSION=${IMAGE_TAG}" \
                                  -p "${HOST_PORT}:${APP_PORT}" \
                                  --name "$CONTAINER_NAME" \
                                  "$DOCKER_USER/$IMAGE_NAME:${IMAGE_TAG}"
                            '''
                        }
                    } catch (err) {
                        echo "Deployment failed: ${err}"
                        def rolledBack = rollback(validate: true)
                        if (rolledBack) {
                            error('Deployment failed. Rolled back to previous version.')
                        } else {
                            error('Deployment failed. No previous version available to roll back.')
                        }
                    }
                }
            }
        }

        stage('Health Check') {
            steps {
                script {
                    def status = sh(
                        script: """
                            sleep 5
                            for i in \$(seq 1 ${env.HEALTH_RETRIES}); do
                                status=\$(curl -s -o /dev/null -w '%{http_code}' '${env.HEALTH_URL}' || true)
                                if [ "\$status" = "200" ]; then
                                    echo "App ready"
                                    exit 0
                                fi
                                echo "Not ready yet... (\$i)"
                                sleep 2
                            done
                            echo "Health timeout"
                            exit 1
                        """,
                        returnStatus: true
                    )

                    if (status != 0) {
                        echo 'Health check failed. Initiating rollback...'
                        def rolledBack = rollback(validate: true)
                        if (rolledBack) {
                            error('Health check failed. Rolled back to previous version.')
                        } else {
                            error('Health check failed. No previous version available to roll back.')
                        }
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
                        echo "API tests failed: ${err}"
                        def rolledBack = rollback(validate: true)
                        if (rolledBack) {
                            error('API tests failed after deployment. Rolled back to previous version.')
                        } else {
                            error('API tests failed after deployment. No previous version available to roll back.')
                        }
                    }
                }
            }
        }

        stage('Stability Check') {
            steps {
                script {
                    echo "Monitoring stability (${env.STABILITY_CHECKS} checks, 2s apart)..."

                    def stable = sh(
                        script: """
                            for i in \$(seq 1 ${env.STABILITY_CHECKS}); do
                                status=\$(curl -s -o /dev/null -w '%{http_code}' '${env.HEALTH_URL}' || true)
                                if [ "\$status" != "200" ]; then
                                    exit 1
                                fi
                                sleep 2
                            done
                            exit 0
                        """,
                        returnStatus: true
                    )

                    if (stable != 0) {
                        echo 'Stability check failed. Initiating rollback...'
                        def rolledBack = rollback(validate: true)
                        if (rolledBack) {
                            error('Application became unstable after deployment. Rolled back to previous version.')
                        } else {
                            error('Application became unstable after deployment. No previous version available to roll back.')
                        }
                    }

                    echo 'Application stable.'
                }
            }
        }

        stage('Cleanup Workspace') {
            steps {
                script {
                    if (!params.LEAVE_CONTAINER_RUNNING) {
                        sh 'docker rm -f "$CONTAINER_NAME" || true'
                    } else {
                        echo "Leaving container ${env.CONTAINER_NAME} running on port ${env.HOST_PORT}."
                    }
                    cleanWs()
                }
            }
        }
    }

    post {
        always {
            sh 'docker logout || true'
        }
        success {
            echo "Release ${IMAGE_TAG} from ${params.GIT_BRANCH} deployed successfully."
        }
        failure {
            echo "Release ${IMAGE_TAG} from ${params.GIT_BRANCH} failed. Check logs."
        }
    }
}

/**
 * Restore the previously running container on the same Docker network used for deploy.
 * @return true if a previous image was restored, false if none was available
 */
def rollback(Map args = [:]) {
    boolean validate = args.get('validate', true)
    def previous = env.PREVIOUS_IMAGE ?: PREVIOUS_IMAGE
    def network = env.DOCKER_NETWORK
    def container = env.CONTAINER_NAME ?: 'my-app-container'
    def hostPort = env.HOST_PORT ?: '8081'
    def appPort = env.APP_PORT ?: '8081'
    def healthUrl = env.HEALTH_URL ?: "http://${container}:${appPort}/health"

    if (!previous || previous == 'none') {
        echo 'No previous image found. Cannot rollback.'
        return false
    }

    if (!network) {
        error('Unable to rollback because Docker network was not detected.')
    }

    echo "Rolling back to ${previous} on network ${network}"

    sh """
        docker rm -f '${container}' || true
        docker run -d \
          --network '${network}' \
          -p '${hostPort}:${appPort}' \
          --name '${container}' \
          '${previous}'
    """

    if (validate) {
        echo "Validating rollback at ${healthUrl}..."
        def rollbackStatus = sh(
            script: """
                for i in \$(seq 1 10); do
                    status=\$(curl -s -o /dev/null -w '%{http_code}' '${healthUrl}' || true)
                    if [ "\$status" = "200" ]; then
                        exit 0
                    fi
                    sleep 2
                done
                exit 1
            """,
            returnStatus: true
        )

        if (rollbackStatus != 0) {
            error('Rollback failed! System is unstable!')
        }

        echo 'Rollback successful. Previous version restored.'
    }

    return true
}
