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
            defaultValue: 'GitHubCredCorp',
            description: 'Jenkins credentials ID for Git checkout'
        )
        string(
            name: 'FUNCTIONAL_TEST_REPO_URL',
            defaultValue: 'https://github.consilio.com/srkumar/SimplePythonAppTests.git',
            description: 'Functional test repository URL'
        )
        string(
            name: 'FUNCTIONAL_TEST_BRANCH',
            defaultValue: 'master',
            description: 'Functional test repository branch'
        )
        string(
            name: 'DOCKER_CRED_ID',
            defaultValue: 'DockerHubCred',
            description: 'Jenkins credentials ID for Docker Hub login'
        )
        string(
            name: 'APP_NAME',
            defaultValue: 'mysimplepython-app',
            description: 'Application name used when IMAGE_NAME is not supplied'
        )
        string(
            name: 'IMAGE_NAME',
            defaultValue: '',
            description: 'Docker image name. Defaults to APP_NAME when blank.'
        )
        string(
            name: 'BASE_CONTAINER_NAME',
            defaultValue: '',
            description: 'Base Docker container name. Defaults to <IMAGE_NAME>-container when blank.'
        )
        string(
            name: 'APP_PORT',
            defaultValue: '8081',
            description: 'Port exposed by the application container'
        )
        string(
            name: 'HEALTH_PATH',
            defaultValue: '/health',
            description: 'HTTP path used for deployment health checks'
        )
        string(
            name: 'DOCKER_REGISTRY',
            defaultValue: 'docker.io',
            description: 'Docker registry host'
        )
        string(
            name: 'DOCKER_BUILD_CONTEXT',
            defaultValue: '.',
            description: 'Docker build context path'
        )
        string(
            name: 'DOCKERFILE_PATH',
            defaultValue: 'Dockerfile',
            description: 'Dockerfile path relative to the workspace'
        )
        text(
            name: 'DOCKER_RUN_ARGS',
            defaultValue: '''--read-only
                                --tmpfs /tmp:rw,noexec,nosuid,size=64m
                                --cap-drop ALL
                                --security-opt no-new-privileges''',
            description: 'Additional docker run arguments, one argument or argument pair per line'
        )
        text(
            name: 'DOCKER_ENV_VARS',
            defaultValue: 'APP_VERSION=${IMAGE_TAG}',
            description: 'Container environment variables as KEY=VALUE lines. Supports ${ENV_NAME} placeholders.'
        )
        string(
            name: 'DOCKER_NETWORK',
            defaultValue: '',
            description: 'Docker network for local deployments. Blank auto-detects the Jenkins container network.'
        )
        string(
            name: 'JENKINS_CONTAINER_NAME',
            defaultValue: 'jenkins',
            description: 'Jenkins controller/agent container name used to auto-detect the local Docker network'
        )
        string(
            name: 'DEV_HOST_PORT',
            defaultValue: '8081',
            description: 'Host port for dev deployments'
        )
        string(
            name: 'TEST_HOST_PORT',
            defaultValue: '8082',
            description: 'Host port for test deployments'
        )
        string(
            name: 'STAGE_HOST_PORT',
            defaultValue: '8083',
            description: 'Host port for stage deployments'
        )
        string(
            name: 'PROD_HOST_PORT',
            defaultValue: '8084',
            description: 'Host port for prod deployments'
        )
        booleanParam(
            name: 'SKIP_APPROVAL',
            defaultValue: false,
            description: 'Skip the manual approval gate for dev/test only. Stage and prod always require approval.'
        )
        booleanParam(
            name: 'LEAVE_CONTAINER_RUNNING',
            defaultValue: true,
            description: 'Leave the test container running after a successful deploy'
        )
        choice(
            name: 'DEPLOY_ENV',
            choices: ['dev', 'test', 'stage', 'prod'],
            description: 'Target environment for local Docker promotion/deployment'
        )
        choice(
            name: 'DEPLOY_RUNTIME',
            choices: ['local-docker', 'remote-docker'],
            description: 'Deployment runtime platform'
        )
        string(
            name: 'REMOTE_DOCKER_HOST',
            defaultValue: 'us2vtcan02.consiliotest.com',
            description: 'Remote VM hostname or IP for remote-docker deployments'
        )
        string(
            name: 'REMOTE_DOCKER_SSH_PORT',
            defaultValue: '22',
            description: 'SSH port for the remote Docker VM'
        )
        string(
            name: 'REMOTE_DOCKER_SSH_CRED_ID',
            defaultValue: 'RemoteDockerVmSshKey',
            description: 'Jenkins SSH private key credential ID for the remote Docker VM'
        )
        string(
            name: 'TRUSTED_DEPLOY_BRANCHES',
            defaultValue: 'master,main,release/*',
            description: 'Comma-separated branch patterns allowed to publish and deploy images'
        )
        string(
            name: 'PROMOTE_IMAGE_TAG',
            defaultValue: '',
            description: 'Existing immutable image tag to promote to the selected environment. Leave blank to build a new image.'
        )
        booleanParam(
            name: 'ENFORCE_DEPENDENCY_SCAN',
            defaultValue: true,
            description: 'Fail the build when the configured dependency scan command exits non-zero'
        )
        booleanParam(
            name: 'ENFORCE_IMAGE_SCAN',
            defaultValue: true,
            description: 'Fail the build when Trivy finds HIGH or CRITICAL image vulnerabilities'
        )
        booleanParam(
            name: 'HEALTH_CHECK_ENABLED',
            defaultValue: true,
            description: 'Run HTTP health and stability checks after deployment'
        )
        text(
            name: 'INSTALL_COMMAND',
            defaultValue: '''python -m venv venv
                            . venv/bin/activate
                            pip install --upgrade pip
                            pip install -r requirements.txt
                            pip install pip-audit''',
            description: 'Language-specific dependency install/setup command. Leave blank to skip.'
        )
        text(
            name: 'LINT_COMMAND',
            defaultValue: '''. venv/bin/activate
                                flake8 app tests --statistics --tee --output-file reports/lint/flake8.log''',
            description: 'Language-specific lint command. Leave blank to skip.'
        )
        text(
            name: 'DEPENDENCY_SCAN_COMMAND',
            defaultValue: '''. venv/bin/activate
                            pip-audit -r requirements.txt --format json --output reports/dependency-scan/pip-audit.json''',
            description: 'Dependency scan command. Leave blank to skip.'
        )
        text(
            name: 'TEST_COMMAND',
            defaultValue: '''. venv/bin/activate
                                python -m pytest tests/test_unit.py tests/test_api.py \
                                --junitxml=reports/junit/unit-api-tests.xml \
                                --cov=app \
                                --cov-report=xml:reports/coverage/coverage.xml \
                                --cov-report=html:reports/coverage/html \
                                --cov-fail-under="${COVERAGE_MIN}"''',
            description: 'Unit/API test command. Leave blank to skip.'
        )
        text(
            name: 'FUNCTIONAL_TEST_COMMAND',
            defaultValue: 'mvn -B test',
            description: 'Functional test command. Leave blank to skip.'
        )
        string(
            name: 'JUNIT_REPORTS',
            defaultValue: 'reports/junit/*.xml',
            description: 'JUnit report glob for primary tests. Leave blank to skip publishing.'
        )
        string(
            name: 'COVERAGE_ARTIFACTS',
            defaultValue: 'reports/coverage/**',
            description: 'Coverage artifact glob. Leave blank to skip publishing.'
        )
        string(
            name: 'LINT_ARTIFACTS',
            defaultValue: 'reports/lint/**',
            description: 'Lint artifact glob. Leave blank to skip publishing.'
        )
        string(
            name: 'DEPENDENCY_SCAN_ARTIFACTS',
            defaultValue: 'reports/dependency-scan/**',
            description: 'Dependency scan artifact glob. Leave blank to skip publishing.'
        )
        string(
            name: 'IMAGE_SCAN_ARTIFACTS',
            defaultValue: 'reports/image-scan/**',
            description: 'Image scan artifact glob. Leave blank to skip publishing.'
        )
        string(
            name: 'FUNCTIONAL_TEST_JUNIT_REPORTS',
            defaultValue: 'functional-tests/target/surefire-reports/*.xml',
            description: 'Functional test JUnit report glob. Leave blank to skip publishing.'
        )
        string(
            name: 'FUNCTIONAL_TEST_ARTIFACTS',
            defaultValue: 'functional-tests/target/surefire-reports/**',
            description: 'Functional test artifact glob. Leave blank to skip publishing.'
        )
        string(
            name: 'ALLURE_RESULTS_PATH',
            defaultValue: 'functional-tests/target/allure-results',
            description: 'Allure results path. Leave blank to skip Allure publishing.'
        )
    }

    options {
        skipDefaultCheckout()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timestamps()
    }

    environment {
        // Quality / timing gates
        COVERAGE_MIN           = '80'
        HEALTH_RETRIES         = '30'
        STABILITY_CHECKS       = '15'
        APPROVAL_TIMEOUT_HOURS = '1'
        DIAGNOSTICS_ARTIFACTS  = 'reports/diagnostics/**'
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

        stage('Prepare Metadata') {
            steps {
                script {
                    configureDeploymentEnvironment()

                    def shortCommit = sh(
                        script: 'git rev-parse --short HEAD',
                        returnStdout: true
                    ).trim()
                    def fullCommit = sh(
                        script: 'git rev-parse HEAD',
                        returnStdout: true
                    ).trim()
                    def buildDate = sh(
                        script: "date -u +%Y-%m-%dT%H:%M:%SZ",
                        returnStdout: true
                    ).trim()
                    def safeBranch = sanitizeTag(params.GIT_BRANCH)
                    def promoteTag = getPromoteImageTag()

                    env.GIT_COMMIT_SHORT = shortCommit
                    env.GIT_COMMIT_FULL = fullCommit
                    env.BUILD_DATE_UTC = buildDate
                    env.MOVING_IMAGE_TAG = "${safeBranch}-latest"
                    env.BUILD_IMAGE = promoteTag ? 'false' : 'true'
                    env.IMAGE_TAG = promoteTag ?: "${env.BUILD_NUMBER}-${shortCommit}"
                    env.IMAGE_PUSH_ENABLED = isTrustedBranch(params.GIT_BRANCH, params.TRUSTED_DEPLOY_BRANCHES) ? 'true' : 'false'
                    env.DEPLOY_ENABLED = shouldDeploy(params.GIT_BRANCH, params.TRUSTED_DEPLOY_BRANCHES) ? 'true' : 'false'

                    if (env.DEPLOY_ENABLED != 'true') {
                        echo "Deployment disabled for untrusted branch ${params.GIT_BRANCH}; CI validation will continue."
                    }

                    echo "Image tag: ${env.IMAGE_TAG}"
                    echo "Moving tag: ${env.MOVING_IMAGE_TAG}"
                    echo "Promote image tag: ${promoteTag ?: '(not supplied)'}"
                    echo "Build image: ${env.BUILD_IMAGE}"
                    echo "Image push enabled: ${env.IMAGE_PUSH_ENABLED}"
                    echo "Deploy enabled: ${env.DEPLOY_ENABLED}"
                    echo "Target environment: ${params.DEPLOY_ENV} (${params.DEPLOY_RUNTIME})"
                }
            }
        }

        stage('Validate Promotion Policy') {
            steps {
                script {
                    if (!['local-docker', 'remote-docker'].contains(params.DEPLOY_RUNTIME)) {
                        error("Unsupported deployment runtime: ${params.DEPLOY_RUNTIME}")
                    }

                    if (
                        shouldDeploy(params.GIT_BRANCH, params.TRUSTED_DEPLOY_BRANCHES) &&
                        ['stage', 'prod'].contains(params.DEPLOY_ENV) &&
                        !getPromoteImageTag()
                    ) {
                        error("${params.DEPLOY_ENV} deployments must promote an existing immutable image tag using PROMOTE_IMAGE_TAG.")
                    }
                }
            }
        }

        stage('Install Dependencies') {
            when {
                expression { return env.BUILD_IMAGE == 'true' && commandEnabled(params.INSTALL_COMMAND) }
            }
            steps {
                sh 'mkdir -p reports/junit reports/coverage reports/lint reports/dependency-scan reports/diagnostics'
                script {
                    runConfiguredCommand('Install dependencies', params.INSTALL_COMMAND)
                }
            }
        }

        stage('Lint') {
            when {
                expression { return env.BUILD_IMAGE == 'true' && commandEnabled(params.LINT_COMMAND) }
            }
            steps {
                echo 'Running configured lint checks...'
                sh 'mkdir -p reports/lint'
                script {
                    runConfiguredCommand('Lint', params.LINT_COMMAND)
                }
            }
            post {
                always {
                    script {
                        archiveConfiguredArtifacts(params.LINT_ARTIFACTS)
                    }
                }
            }
        }

        stage('Dependency Scan') {
            when {
                expression { return env.BUILD_IMAGE == 'true' && commandEnabled(params.DEPENDENCY_SCAN_COMMAND) }
            }
            steps {
                echo 'Running configured dependency scan...'
                script {
                    def scanStatus = sh(
                        script: withReportSetup(params.DEPENDENCY_SCAN_COMMAND, 'reports/dependency-scan'),
                        returnStatus: true
                    )

                    if (scanStatus != 0 && params.ENFORCE_DEPENDENCY_SCAN) {
                        error('Dependency scan failed. See configured dependency scan artifacts.')
                    }

                    if (scanStatus != 0) {
                        echo 'Dependency scan found issues, but enforcement is disabled.'
                    }
                }
            }
            post {
                always {
                    script {
                        archiveConfiguredArtifacts(params.DEPENDENCY_SCAN_ARTIFACTS)
                    }
                }
            }
        }

        stage('Run Unit and API Tests') {
            when {
                expression { return env.BUILD_IMAGE == 'true' && commandEnabled(params.TEST_COMMAND) }
            }
            steps {
                echo 'Running configured unit/API tests...'
                sh 'mkdir -p reports/junit reports/coverage/html'
                script {
                    runConfiguredCommand('Unit/API tests', params.TEST_COMMAND)
                }
            }
            post {
                always {
                    script {
                        publishConfiguredJUnit(params.JUNIT_REPORTS)
                        archiveConfiguredArtifacts(params.COVERAGE_ARTIFACTS)
                    }
                }
            }
        }

        stage('Docker Login') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: params.DOCKER_CRED_ID,
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh 'echo "$DOCKER_PASS" | docker login "$DOCKER_REGISTRY" -u "$DOCKER_USER" --password-stdin'
                }
            }
        }

        stage('Build Image') {
            when {
                expression { return env.BUILD_IMAGE == 'true' }
            }
            steps {
                echo "Building ${env.IMAGE_NAME}:${env.IMAGE_TAG}..."
                withCredentials([usernamePassword(
                    credentialsId: params.DOCKER_CRED_ID,
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh '''
                        IMAGE_REPO="$DOCKER_REGISTRY/$DOCKER_USER/$IMAGE_NAME"
                        docker build \
                          --build-arg "BUILD_DATE=${BUILD_DATE_UTC}" \
                          --build-arg "VCS_REF=${GIT_COMMIT_FULL}" \
                          --build-arg "VERSION=${IMAGE_TAG}" \
                          --build-arg "BUILD_URL=${BUILD_URL}" \
                          --label "org.opencontainers.image.created=${BUILD_DATE_UTC}" \
                          --label "org.opencontainers.image.revision=${GIT_COMMIT_FULL}" \
                          --label "org.opencontainers.image.version=${IMAGE_TAG}" \
                          --label "org.opencontainers.image.source=${GIT_REPO_URL}" \
                          --label "ci.jenkins.branch=${GIT_BRANCH}" \
                          --label "ci.jenkins.build_number=${BUILD_NUMBER}" \
                          --label "ci.jenkins.build_url=${BUILD_URL}" \
                          -t "$IMAGE_REPO:${IMAGE_TAG}" \
                          -t "$IMAGE_REPO:${MOVING_IMAGE_TAG}" \
                          -f "$DOCKERFILE_PATH" \
                          "$DOCKER_BUILD_CONTEXT"
                    '''
                }
            }
        }

        stage('Image Scan') {
            steps {
                echo "Scanning image ${env.IMAGE_TAG}..."
                script {
                    def scannerStatus = sh(
                        script: 'command -v trivy >/dev/null 2>&1',
                        returnStatus: true
                    )

                    if (scannerStatus != 0) {
                        sh 'mkdir -p reports/image-scan'
                        writeFile file: 'reports/image-scan/trivy.txt', text: 'Trivy is not installed on this Jenkins agent.\n'
                        if (params.ENFORCE_IMAGE_SCAN) {
                            error('Trivy is required for enforced image scanning.')
                        }
                        echo 'Trivy is not installed; image scan enforcement is disabled for this run.'
                        return
                    }

                    withCredentials([usernamePassword(
                        credentialsId: params.DOCKER_CRED_ID,
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS'
                    )]) {
                        def scanStatus = sh(
                            script: '''
                                mkdir -p reports/image-scan
                                IMAGE_REPO="$DOCKER_REGISTRY/$DOCKER_USER/$IMAGE_NAME"
                                if [ "$BUILD_IMAGE" != "true" ]; then
                                    docker pull "$IMAGE_REPO:${IMAGE_TAG}"
                                fi
                                trivy image \
                                  --severity HIGH,CRITICAL \
                                  --format table \
                                  --output reports/image-scan/trivy.txt \
                                  --exit-code 1 \
                                  "$IMAGE_REPO:${IMAGE_TAG}"
                            ''',
                            returnStatus: true
                        )

                        if (scanStatus != 0 && params.ENFORCE_IMAGE_SCAN) {
                            error('Image scan failed. See reports/image-scan/trivy.txt.')
                        }

                        if (scanStatus != 0) {
                            echo 'Image scan found issues, but enforcement is disabled.'
                        }
                    }
                }
            }
            post {
                always {
                    script {
                        archiveConfiguredArtifacts(params.IMAGE_SCAN_ARTIFACTS)
                    }
                }
            }
        }

        stage('Push Image') {
            when {
                expression { return env.BUILD_IMAGE == 'true' && isTrustedBranch(params.GIT_BRANCH, params.TRUSTED_DEPLOY_BRANCHES) }
            }
            steps {
                echo "Pushing ${env.IMAGE_NAME}:${env.IMAGE_TAG} and ${env.MOVING_IMAGE_TAG}..."
                withCredentials([usernamePassword(
                    credentialsId: params.DOCKER_CRED_ID,
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh '''
                        IMAGE_REPO="$DOCKER_REGISTRY/$DOCKER_USER/$IMAGE_NAME"
                        docker push "$IMAGE_REPO:${IMAGE_TAG}"
                        docker push "$IMAGE_REPO:${MOVING_IMAGE_TAG}"
                    '''
                }
            }
        }

        stage('Capture Previous Version') {
            when {
                expression { return shouldDeploy(params.GIT_BRANCH, params.TRUSTED_DEPLOY_BRANCHES) }
            }
            steps {
                script {
                    if (isRemoteDeploy()) {
                        withRemoteDockerVm {
                            PREVIOUS_IMAGE = sh(
                                script: '''
                                    ssh -i "$REMOTE_SSH_KEY" \
                                      -p "$REMOTE_DOCKER_SSH_PORT" \
                                      -o BatchMode=yes \
                                      -o StrictHostKeyChecking=no \
                                      "$REMOTE_SSH_USER@$REMOTE_DOCKER_HOST" \
                                      "docker inspect --format='{{.Config.Image}}' '$CONTAINER_NAME' 2>/dev/null || echo 'none'"
                                ''',
                                returnStdout: true
                            ).trim()
                        }
                    } else {
                        PREVIOUS_IMAGE = sh(
                            script: "docker inspect --format='{{.Config.Image}}' ${env.CONTAINER_NAME} 2>/dev/null || echo 'none'",
                            returnStdout: true
                        ).trim()

                        def network = (params.DOCKER_NETWORK ?: '').trim()
                        if (!network) {
                            network = sh(
                                script: '''
                                    docker inspect "$JENKINS_CONTAINER_NAME" \
                                      --format='{{range $name, $_ := .NetworkSettings.Networks}}{{println $name}}{{end}}' 2>/dev/null \
                                    | head -n1 \
                                    || true
                                ''',
                                returnStdout: true
                            ).trim()
                        }

                        if (!network) {
                            error("Unable to detect Docker network for ${env.JENKINS_CONTAINER_NAME}.")
                        }

                        env.DOCKER_NETWORK = network
                    }

                    env.PREVIOUS_IMAGE = PREVIOUS_IMAGE

                    echo "Previous image: ${PREVIOUS_IMAGE}"
                    if (!isRemoteDeploy()) {
                        echo "Docker network: ${env.DOCKER_NETWORK}"
                    }
                    echo "Health URL: ${env.HEALTH_URL}"
                    echo "Container name: ${env.CONTAINER_NAME}"
                }
            }
        }

        stage('Manual Approval') {
            when {
                expression {
                    return shouldDeploy(params.GIT_BRANCH, params.TRUSTED_DEPLOY_BRANCHES) &&
                        requiresManualApproval(params.DEPLOY_ENV, params.SKIP_APPROVAL)
                }
            }
            steps {
                script {
                    timeout(time: env.APPROVAL_TIMEOUT_HOURS.toInteger(), unit: 'HOURS') {
                        input message: "Approve deployment of ${env.IMAGE_NAME}:${env.IMAGE_TAG} to ${params.DEPLOY_ENV}?", ok: 'Deploy'
                    }
                }
            }
        }

        stage('Deploy Docker Container') {
            when {
                expression { return shouldDeploy(params.GIT_BRANCH, params.TRUSTED_DEPLOY_BRANCHES) }
            }
            steps {
                script {
                    try {
                        echo "Deploying to ${params.DEPLOY_ENV} on ${params.DEPLOY_RUNTIME}..."
                        if (isRemoteDeploy()) {
                            deployRemoteContainer()
                        } else {
                            deployLocalContainer()
                        }
                    } catch (err) {
                        echo "Deployment failed: ${err}"
                        captureDeploymentDiagnostics('deploy')
                        def rolledBack = rollback(validate: params.HEALTH_CHECK_ENABLED)
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
            when {
                expression { return shouldDeploy(params.GIT_BRANCH, params.TRUSTED_DEPLOY_BRANCHES) && params.HEALTH_CHECK_ENABLED }
            }
            steps {
                script {
                    def status = sh(
                        script: """
                            mkdir -p reports/diagnostics/health-check
                            sleep 5
                            for i in \$(seq 1 ${env.HEALTH_RETRIES}); do
                                status=\$(curl -s -o /dev/null -w '%{http_code}' '${env.HEALTH_URL}' || true)
                                if [ "\$status" = "200" ]; then
                                    echo "App ready" | tee -a reports/diagnostics/health-check/health-check.log
                                    exit 0
                                fi
                                echo "Not ready yet... (\$i): HTTP \$status" | tee -a reports/diagnostics/health-check/health-check.log
                                sleep 2
                            done
                            curl -sv '${env.HEALTH_URL}' > reports/diagnostics/health-check/health-response.txt 2>&1 || true
                            echo "Health timeout" | tee -a reports/diagnostics/health-check/health-check.log
                            exit 1
                        """,
                        returnStatus: true
                    )

                    if (status != 0) {
                        echo 'Health check failed. Initiating rollback...'
                        captureDeploymentDiagnostics('health-check')
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

        stage('Functional Tests') {
            when {
                expression {
                    return shouldDeploy(params.GIT_BRANCH, params.TRUSTED_DEPLOY_BRANCHES) &&
                        commandEnabled(params.FUNCTIONAL_TEST_COMMAND)
                }
            }
            steps {
                script {
                    try {
                        if (commandEnabled(params.FUNCTIONAL_TEST_REPO_URL)) {
                            dir('functional-tests') {
                                deleteDir()
                                checkout([
                                    $class: 'GitSCM',
                                    branches: [[name: "*/${params.FUNCTIONAL_TEST_BRANCH}"]],
                                    userRemoteConfigs: [[
                                        url: params.FUNCTIONAL_TEST_REPO_URL,
                                        credentialsId: params.GIT_CRED_ID
                                    ]]
                                ])

                                withEnv(["BASE_URL=${env.APP_BASE_URL}"]) {
                                    runConfiguredCommand('Functional tests', params.FUNCTIONAL_TEST_COMMAND)
                                }
                            }
                        } else {
                            withEnv(["BASE_URL=${env.APP_BASE_URL}"]) {
                                runConfiguredCommand('Functional tests', params.FUNCTIONAL_TEST_COMMAND)
                            }
                        }
                    } catch (err) {
                        echo "Functional tests failed: ${err}"
                        captureDeploymentDiagnostics('functional-tests')
                        def rolledBack = rollback(validate: params.HEALTH_CHECK_ENABLED)
                        if (rolledBack) {
                            error('Functional tests failed after deployment. Rolled back to previous version.')
                        } else {
                            error('Functional tests failed after deployment. No previous version available to roll back.')
                        }
                    }
                }
            }
            post {
                always {
                    script {
                        publishConfiguredJUnit(params.FUNCTIONAL_TEST_JUNIT_REPORTS)
                        archiveConfiguredArtifacts(params.FUNCTIONAL_TEST_ARTIFACTS)
                        if (commandEnabled(params.ALLURE_RESULTS_PATH) && fileExists(params.ALLURE_RESULTS_PATH.trim())) {
                            allure([
                                includeProperties: false,
                                jdk: '',
                                properties: [],
                                reportBuildPolicy: 'ALWAYS',
                                results: [[path: params.ALLURE_RESULTS_PATH.trim()]]
                            ])
                        } else {
                            echo 'No functional test Allure results found to publish.'
                        }
                    }
                }
            }
        }

        stage('Stability Check') {
            when {
                expression { return shouldDeploy(params.GIT_BRANCH, params.TRUSTED_DEPLOY_BRANCHES) && params.HEALTH_CHECK_ENABLED }
            }
            steps {
                script {
                    echo "Monitoring stability (${env.STABILITY_CHECKS} checks, 2s apart)..."

                    def stable = sh(
                        script: """
                            mkdir -p reports/diagnostics/stability-check
                            for i in \$(seq 1 ${env.STABILITY_CHECKS}); do
                                status=\$(curl -s -o /dev/null -w '%{http_code}' '${env.HEALTH_URL}' || true)
                                if [ "\$status" != "200" ]; then
                                    echo "Stability check \$i failed with HTTP \$status" \
                                      | tee -a reports/diagnostics/stability-check/stability-check.log
                                    curl -sv '${env.HEALTH_URL}' > reports/diagnostics/stability-check/health-response.txt 2>&1 || true
                                    exit 1
                                fi
                                echo "Stability check \$i passed" | tee -a reports/diagnostics/stability-check/stability-check.log
                                sleep 2
                            done
                            exit 0
                        """,
                        returnStatus: true
                    )

                    if (stable != 0) {
                        echo 'Stability check failed. Initiating rollback...'
                        captureDeploymentDiagnostics('stability-check')
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
                    if (shouldDeploy(params.GIT_BRANCH, params.TRUSTED_DEPLOY_BRANCHES) && !params.LEAVE_CONTAINER_RUNNING) {
                        if (isRemoteDeploy()) {
                            withRemoteDockerVm {
                                sh '''
                                    ssh -i "$REMOTE_SSH_KEY" \
                                      -p "$REMOTE_DOCKER_SSH_PORT" \
                                      -o BatchMode=yes \
                                      -o StrictHostKeyChecking=no \
                                      "$REMOTE_SSH_USER@$REMOTE_DOCKER_HOST" \
                                      "docker rm -f '$CONTAINER_NAME' || true"
                                '''
                            }
                        } else {
                            sh 'docker rm -f "$CONTAINER_NAME" || true'
                        }
                    } else if (shouldDeploy(params.GIT_BRANCH, params.TRUSTED_DEPLOY_BRANCHES)) {
                        echo "Leaving container ${env.CONTAINER_NAME} running on ${env.APP_BASE_URL}."
                    } else {
                        echo 'No deployment container cleanup needed.'
                    }
                    if (isRemoteDeploy()) {
                        withRemoteDockerVm {
                            sh '''
                                ssh -i "$REMOTE_SSH_KEY" \
                                  -p "$REMOTE_DOCKER_SSH_PORT" \
                                  -o BatchMode=yes \
                                  -o StrictHostKeyChecking=no \
                                  "$REMOTE_SSH_USER@$REMOTE_DOCKER_HOST" \
                                  "docker image prune -f || true"
                            '''
                        }
                    } else {
                        sh 'docker image prune -f || true'
                    }
                }
            }
        }
    }

    post {
        always {
            script {
                publishPipelineArtifacts()
            }
            sh 'docker logout "$DOCKER_REGISTRY" || true'
        }
        success {
            echo "Release ${env.IMAGE_TAG} from ${params.GIT_BRANCH} completed successfully for ${params.DEPLOY_ENV}."
        }
        failure {
            echo "Release ${env.IMAGE_TAG} from ${params.GIT_BRANCH} failed. Check logs."
        }
        cleanup {
            cleanWs()
        }
    }
}

def configureDeploymentEnvironment() {
    def ports = [
        dev  : (params.DEV_HOST_PORT ?: '').trim(),
        test : (params.TEST_HOST_PORT ?: '').trim(),
        stage: (params.STAGE_HOST_PORT ?: '').trim(),
        prod : (params.PROD_HOST_PORT ?: '').trim()
    ]
    def target = params.DEPLOY_ENV ?: 'dev'
    def hostPort = ports[target]

    if (!hostPort) {
        error("Host port is required for deployment environment: ${target}")
    }

    def appName = (params.APP_NAME ?: '').trim()
    def imageName = (params.IMAGE_NAME ?: '').trim() ?: appName
    if (!imageName) {
        error('IMAGE_NAME or APP_NAME is required.')
    }

    def baseContainerName = (params.BASE_CONTAINER_NAME ?: '').trim() ?: "${imageName}-container"

    env.APP_NAME = appName ?: imageName
    env.IMAGE_NAME = imageName
    env.BASE_CONTAINER_NAME = baseContainerName
    env.CONTAINER_NAME = "${baseContainerName}-${target}"
    env.APP_PORT = requireParam('APP_PORT', params.APP_PORT)
    env.HEALTH_PATH = normalizePath(params.HEALTH_PATH ?: '/')
    env.DOCKER_REGISTRY = requireParam('DOCKER_REGISTRY', params.DOCKER_REGISTRY)
    env.DOCKER_BUILD_CONTEXT = requireParam('DOCKER_BUILD_CONTEXT', params.DOCKER_BUILD_CONTEXT)
    env.DOCKERFILE_PATH = requireParam('DOCKERFILE_PATH', params.DOCKERFILE_PATH)
    env.JENKINS_CONTAINER_NAME = requireParam('JENKINS_CONTAINER_NAME', params.JENKINS_CONTAINER_NAME)
    env.HOST_PORT = hostPort

    if (isRemoteDeploy()) {
        def remoteHost = (params.REMOTE_DOCKER_HOST ?: '').trim()
        if (!remoteHost) {
            error('REMOTE_DOCKER_HOST is required when DEPLOY_RUNTIME is remote-docker.')
        }
        env.APP_BASE_URL = "http://${remoteHost}:${env.HOST_PORT}"
    } else {
        env.APP_BASE_URL = "http://${env.CONTAINER_NAME}:${env.APP_PORT}"
    }
    env.HEALTH_URL = "${env.APP_BASE_URL}${env.HEALTH_PATH}"
}

def commandEnabled(Object value) {
    return value != null && value.toString().trim().length() > 0
}

def runConfiguredCommand(String label, Object command) {
    def scriptText = command?.toString()?.trim()
    if (!scriptText) {
        echo "Skipping ${label}; no command configured."
        return
    }

    sh script: scriptText
}

def withReportSetup(Object command, String reportDir) {
    return """
        mkdir -p '${reportDir}'
        ${command?.toString()?.trim() ?: 'true'}
    """
}

def publishConfiguredJUnit(Object patterns) {
    def normalized = patterns?.toString()?.trim()
    if (normalized) {
        junit allowEmptyResults: true, testResults: normalized
    } else {
        echo 'No JUnit report pattern configured.'
    }
}

def archiveConfiguredArtifacts(Object patterns) {
    def normalized = patterns?.toString()?.trim()
    if (normalized) {
        archiveArtifacts allowEmptyArchive: true, artifacts: normalized
    } else {
        echo 'No artifact pattern configured.'
    }
}

def joinPatterns(Object... patterns) {
    return patterns
        .collect { it?.toString()?.trim() }
        .findAll { it }
        .join(', ')
}

def dockerRunArgs() {
    return normalizeLines(params.DOCKER_RUN_ARGS).join(' ')
}

def dockerEnvArgs() {
    return normalizeLines(params.DOCKER_ENV_VARS)
        .collect { "-e ${shellQuote(expandEnvPlaceholders(it))}" }
        .join(' ')
}

def normalizeLines(Object value) {
    return (value ?: '')
        .toString()
        .split(/\r?\n/)
        .collect { it.trim() }
        .findAll { it && !it.startsWith('#') }
}

def expandEnvPlaceholders(String value) {
    return value.replaceAll(/\$\{([A-Za-z_][A-Za-z0-9_]*)\}/) { full, name ->
        return env[name] ?: full
    }
}

def shellQuote(String value) {
    return "'${value.replace("'", "'\"'\"'")}'"
}

def requireParam(String name, Object value) {
    def normalized = value?.toString()?.trim()
    if (!normalized) {
        error("${name} is required.")
    }
    return normalized
}

def normalizePath(String value) {
    def normalized = (value ?: '/').trim()
    return normalized.startsWith('/') ? normalized : "/${normalized}"
}

def isRemoteDeploy() {
    return params.DEPLOY_RUNTIME == 'remote-docker'
}

def withRemoteDockerVm(Closure body) {
    if (!(params.REMOTE_DOCKER_HOST ?: '').trim()) {
        error('REMOTE_DOCKER_HOST is required when DEPLOY_RUNTIME is remote-docker.')
    }

    withCredentials([sshUserPrivateKey(
        credentialsId: params.REMOTE_DOCKER_SSH_CRED_ID,
        keyFileVariable: 'REMOTE_SSH_KEY',
        usernameVariable: 'REMOTE_SSH_USER'
    )]) {
        withEnv([
            "REMOTE_DOCKER_HOST=${params.REMOTE_DOCKER_HOST.trim()}",
            "REMOTE_DOCKER_SSH_PORT=${(params.REMOTE_DOCKER_SSH_PORT ?: '22').trim()}"
        ]) {
            body()
        }
    }
}

def deployLocalContainer() {
    def runArgs = dockerRunArgs()
    def envArgs = dockerEnvArgs()

    withCredentials([usernamePassword(
        credentialsId: params.DOCKER_CRED_ID,
        usernameVariable: 'DOCKER_USER',
        passwordVariable: 'DOCKER_PASS'
    )]) {
        sh """
            IMAGE_REPO="\$DOCKER_REGISTRY/\$DOCKER_USER/\$IMAGE_NAME"
            docker rm -f "\$CONTAINER_NAME" >/dev/null 2>&1 || true
            docker pull "\$IMAGE_REPO:\$IMAGE_TAG"
            docker run -d \
              --network "\$DOCKER_NETWORK" \
              ${runArgs} \
              ${envArgs} \
              -p "\$HOST_PORT:\$APP_PORT" \
              --name "\$CONTAINER_NAME" \
              "\$IMAGE_REPO:\$IMAGE_TAG"
        """
    }
}

def deployRemoteContainer() {
    def runArgs = dockerRunArgs()
    def envArgs = dockerEnvArgs()

    withCredentials([usernamePassword(
        credentialsId: params.DOCKER_CRED_ID,
        usernameVariable: 'DOCKER_USER',
        passwordVariable: 'DOCKER_PASS'
    )]) {
        withRemoteDockerVm {
            sh """
                IMAGE_REPO="\$DOCKER_REGISTRY/\$DOCKER_USER/\$IMAGE_NAME"
                REMOTE_TARGET="\$REMOTE_SSH_USER@\$REMOTE_DOCKER_HOST"
                remote_ssh() {
                    ssh -i "\$REMOTE_SSH_KEY" \
                      -p "\$REMOTE_DOCKER_SSH_PORT" \
                      -o BatchMode=yes \
                      -o StrictHostKeyChecking=no \
                      "\$REMOTE_TARGET" "\$@"
                }

                printf '%s' "\$DOCKER_PASS" | remote_ssh \
                  "docker login '\$DOCKER_REGISTRY' -u '\$DOCKER_USER' --password-stdin"

                remote_ssh "
                    set -eu
                    docker rm -f '\$CONTAINER_NAME' >/dev/null 2>&1 || true
                    docker pull '\$IMAGE_REPO:\$IMAGE_TAG'
                    docker run -d \
                      ${runArgs} \
                      ${envArgs} \
                      -p '\$HOST_PORT:\$APP_PORT' \
                      --name '\$CONTAINER_NAME' \
                      '\$IMAGE_REPO:\$IMAGE_TAG'
                "

                remote_ssh "docker logout '\$DOCKER_REGISTRY' || true"
            """
        }
    }
}

def shouldDeploy(String branch, String trustedPatterns) {
    return isTrustedBranch(branch, trustedPatterns)
}

def getPromoteImageTag() {
    return params.PROMOTE_IMAGE_TAG ? params.PROMOTE_IMAGE_TAG.toString().trim() : ''
}

def isTrustedBranch(String branch, String trustedPatterns) {
    def current = normalizeBranch(branch)
    return trustedPatterns
        .split(',')
        .collect { it.trim() }
        .findAll { it }
        .any { pattern -> branchMatches(current, pattern) }
}

def branchMatches(String branch, String pattern) {
    def normalizedPattern = normalizeBranch(pattern)

    if (normalizedPattern.endsWith('/*')) {
        return branch.startsWith(normalizedPattern[0..-2])
    }

    return branch == normalizedPattern
}

def normalizeBranch(String branch) {
    return (branch ?: '')
        .trim()
        .replaceFirst(/^refs\/heads\//, '')
        .replaceFirst(/^origin\//, '')
        .replaceFirst(/^\*\//, '')
}

def sanitizeTag(String value) {
    def tag = normalizeBranch(value).toLowerCase().replaceAll(/[^a-z0-9_.-]+/, '-')
    tag = tag.replaceAll(/^-+/, '').replaceAll(/-+$/, '')
    return tag ?: 'branch'
}

def requiresManualApproval(String targetEnv, boolean skipApproval) {
    if (['stage', 'prod'].contains(targetEnv)) {
        return true
    }

    return !skipApproval
}

def captureDeploymentDiagnostics(String reason) {
    def safeReason = sanitizeTag(reason)

    if (isRemoteDeploy()) {
        withRemoteDockerVm {
            sh """
                mkdir -p 'reports/diagnostics/${safeReason}'
                {
                    echo 'reason=${safeReason}'
                    echo 'environment=${params.DEPLOY_ENV}'
                    echo 'runtime=${params.DEPLOY_RUNTIME}'
                    echo 'remote_host=${params.REMOTE_DOCKER_HOST}'
                    echo 'image_tag=${env.IMAGE_TAG}'
                    echo 'container=${env.CONTAINER_NAME}'
                    echo 'health_url=${env.HEALTH_URL}'
                    date -u +%Y-%m-%dT%H:%M:%SZ
                } > 'reports/diagnostics/${safeReason}/context.txt' 2>&1 || true

                REMOTE_TARGET="\$REMOTE_SSH_USER@\$REMOTE_DOCKER_HOST"
                remote_ssh() {
                    ssh -i "\$REMOTE_SSH_KEY" \
                      -p "\$REMOTE_DOCKER_SSH_PORT" \
                      -o BatchMode=yes \
                      -o StrictHostKeyChecking=no \
                      "\$REMOTE_TARGET" "\$@"
                }

                remote_ssh "docker ps -a --filter name='${env.CONTAINER_NAME}'" \
                  > 'reports/diagnostics/${safeReason}/docker-ps.txt' 2>&1 || true
                remote_ssh "docker inspect '${env.CONTAINER_NAME}'" > 'reports/diagnostics/${safeReason}/docker-inspect.json' 2>&1 || true
                remote_ssh "docker logs --timestamps '${env.CONTAINER_NAME}'" \
                  > 'reports/diagnostics/${safeReason}/container.log' 2>&1 || true
                curl -sv '${env.HEALTH_URL}' > 'reports/diagnostics/${safeReason}/health-response.txt' 2>&1 || true
            """
        }
    } else {
        sh """
            mkdir -p 'reports/diagnostics/${safeReason}'
            {
                echo 'reason=${safeReason}'
                echo 'environment=${params.DEPLOY_ENV}'
                echo 'runtime=${params.DEPLOY_RUNTIME}'
                echo 'image_tag=${env.IMAGE_TAG}'
                echo 'container=${env.CONTAINER_NAME}'
                echo 'health_url=${env.HEALTH_URL}'
                date -u +%Y-%m-%dT%H:%M:%SZ
            } > 'reports/diagnostics/${safeReason}/context.txt' 2>&1 || true
            docker ps -a --filter "name=${env.CONTAINER_NAME}" > 'reports/diagnostics/${safeReason}/docker-ps.txt' 2>&1 || true
            docker inspect '${env.CONTAINER_NAME}' > 'reports/diagnostics/${safeReason}/docker-inspect.json' 2>&1 || true
            docker logs --timestamps '${env.CONTAINER_NAME}' > 'reports/diagnostics/${safeReason}/container.log' 2>&1 || true
            curl -sv '${env.HEALTH_URL}' > 'reports/diagnostics/${safeReason}/health-response.txt' 2>&1 || true
        """
    }

    archiveArtifacts allowEmptyArchive: true, artifacts: "reports/diagnostics/${safeReason}/**"
}

def publishPipelineArtifacts() {
    publishConfiguredJUnit(joinPatterns(
        params.JUNIT_REPORTS,
        params.FUNCTIONAL_TEST_JUNIT_REPORTS
    ))
    archiveConfiguredArtifacts(joinPatterns(
        params.LINT_ARTIFACTS,
        params.DEPENDENCY_SCAN_ARTIFACTS,
        params.COVERAGE_ARTIFACTS,
        params.IMAGE_SCAN_ARTIFACTS,
        env.DIAGNOSTICS_ARTIFACTS,
        params.FUNCTIONAL_TEST_ARTIFACTS,
        commandEnabled(params.ALLURE_RESULTS_PATH) ? "${params.ALLURE_RESULTS_PATH.trim()}/**" : ''
    ))
}

/**
 * Restore the previously running container on the selected Docker runtime.
 * @return true if a previous image was restored, false if none was available
 */
def rollback(Map args = [:]) {
    boolean validate = args.get('validate', true)
    def previous = env.PREVIOUS_IMAGE ?: PREVIOUS_IMAGE
    def network = env.DOCKER_NETWORK
    def container = env.CONTAINER_NAME ?: "${env.BASE_CONTAINER_NAME ?: env.IMAGE_NAME}-container"
    def hostPort = env.HOST_PORT ?: params.DEV_HOST_PORT
    def appPort = env.APP_PORT ?: params.APP_PORT
    def healthUrl = env.HEALTH_URL ?: "http://${container}:${appPort}${normalizePath(params.HEALTH_PATH ?: '/')}"
    def runArgs = dockerRunArgs()
    def envArgs = dockerEnvArgs()

    if (!previous || previous == 'none') {
        echo 'No previous image found. Cannot rollback.'
        return false
    }

    if (isRemoteDeploy()) {
        echo "Rolling back to ${previous} on remote Docker VM ${params.REMOTE_DOCKER_HOST}"

        withRemoteDockerVm {
            sh """
                ssh -i "\$REMOTE_SSH_KEY" \
                  -p "\$REMOTE_DOCKER_SSH_PORT" \
                  -o BatchMode=yes \
                  -o StrictHostKeyChecking=no \
                  "\$REMOTE_SSH_USER@\$REMOTE_DOCKER_HOST" "
                    set -eu
                    docker rm -f '${container}' || true
                    docker run -d \
                      ${runArgs} \
                      ${envArgs} \
                      -p '${hostPort}:${appPort}' \
                      --name '${container}' \
                      '${previous}'
                  "
            """
        }
    } else {
        if (!network) {
            error('Unable to rollback because Docker network was not detected.')
        }

        echo "Rolling back to ${previous} on network ${network}"

        sh """
            docker rm -f '${container}' || true
            docker run -d \
              --network '${network}' \
              ${runArgs} \
              ${envArgs} \
              -p '${hostPort}:${appPort}' \
              --name '${container}' \
              '${previous}'
        """
    }

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
