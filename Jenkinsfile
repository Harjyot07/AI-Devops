pipeline {
    agent { label 'ubuntu' }

    environment {
        // Git commit for traceability
        GIT_COMMIT_SHORT = sh(returnStdout: true, script: 'git rev-parse --short HEAD').trim()
        
        // Image tags with build number + git SHA for uniqueness
        FRONTEND_IMAGE = "new-frontend:${BUILD_NUMBER}-${GIT_COMMIT_SHORT}"
        BACKEND_IMAGE  = "new-backend:${BUILD_NUMBER}-${GIT_COMMIT_SHORT}"
        
        // Ensure PATH includes common Ubuntu binary locations
        PATH = "/usr/local/bin:/usr/bin:$PATH"
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        disableConcurrentBuilds()
        timeout(time: 30, unit: 'MINUTES')
    }

    stages {

        stage('Pre-flight Check') {
            steps {
                sh '''
                    echo "========================================"
                    echo "Node: $(hostname)"
                    echo "User: $(whoami)"
                    echo "Workspace: $(pwd)"
                    echo "Docker: $(docker --version)"
                    echo "Git Commit: ${GIT_COMMIT_SHORT}"
                    echo "========================================"
                    
                    # Verify Docker is accessible
                    docker info > /dev/null 2>&1 || { echo "ERROR: Docker not accessible"; exit 1; }
                '''
            }
        }

        stage('Clone Code') {
            steps {
                checkout scm
                sh '''
                    echo "Project files:"
                    ls -la
                    echo ""
                    echo "Git log (last 3):"
                    git log --oneline -3
                '''
            }
        }

        stage('Build Images') {
            parallel {
                stage('Build Frontend') {
                    steps {
                        dir('frontend') {
                            sh '''
                                echo "Building ${FRONTEND_IMAGE}..."
                                docker build -t ${FRONTEND_IMAGE} .
                                echo "Frontend build complete"
                            '''
                        }
                    }
                }
                stage('Build Backend') {
                    steps {
                        dir('backend') {
                            sh '''
                                echo "Building ${BACKEND_IMAGE}..."
                                docker build -t ${BACKEND_IMAGE} .
                                echo "Backend build complete"
                            '''
                        }
                    }
                }
            }
        }

        stage('Stop Old Containers') {
            steps {
                sh '''
                    # Detect docker compose command (Ubuntu may have plugin or legacy)
                    if docker compose version &> /dev/null; then
                        COMPOSE="docker compose"
                    elif docker-compose --version &> /dev/null; then
                        COMPOSE="docker-compose"
                    else
                        echo "ERROR: docker compose not found"
                        exit 1
                    fi
                    
                    echo "Using: $COMPOSE"
                    $COMPOSE down --remove-orphans || echo "No existing containers to stop"
                '''
            }
        }

        stage('Deploy Containers') {
            steps {
                sh '''
                    # Export image variables for docker-compose.yml substitution
                    export FRONTEND_IMAGE=${FRONTEND_IMAGE}
                    export BACKEND_IMAGE=${BACKEND_IMAGE}
                    
                    # Detect docker compose command
                    if docker compose version &> /dev/null; then
                        COMPOSE="docker compose"
                    else
                        COMPOSE="docker-compose"
                    fi
                    
                    echo "Deploying images:"
                    echo "  Frontend: ${FRONTEND_IMAGE}"
                    echo "  Backend:  ${BACKEND_IMAGE}"
                    
                    $COMPOSE up -d --remove-orphans
                '''
            }
        }

        stage('Verify Deployment') {
            steps {
                sh '''
                    echo "Container status:"
                    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
                    
                    echo ""
                    echo "Image list:"
                    docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | grep new- || true
                    
                    # Optional: Add health check endpoints here
                    # sleep 10
                    # curl -sf http://localhost:8080/health || exit 1
                '''
            }
        }

        stage('Cleanup Old Images') {
            steps {
                sh '''
                    # Remove dangling images and previous builds (keep last 3)
                    docker image prune -f
                    
                    # Remove old tagged images (optional - uncomment if disk space is tight)
                    # docker images --format "{{.Repository}}:{{.Tag}}" | grep "new-frontend:" | sort -r | tail -n +4 | xargs -r docker rmi || true
                    # docker images --format "{{.Repository}}:{{.Tag}}" | grep "new-backend:" | sort -r | tail -n +4 | xargs -r docker rmi || true
                '''
            }
        }
    }

    post {
        success {
            echo "========================================"
            echo "DEPLOYMENT SUCCESSFUL"
            echo "Frontend: ${FRONTEND_IMAGE}"
            echo "Backend:  ${BACKEND_IMAGE}"
            echo "Node:     ${env.NODE_NAME}"
            echo "========================================"
        }

        failure {
            echo "========================================"
            echo "DEPLOYMENT FAILED"
            echo "Check logs above for details"
            echo "========================================"
        }

        always {
            sh '''
                # Ubuntu disk cleanup
                docker system prune -f || true
                
                # Reset permissions if needed (Ubuntu agent workspace issues)
                # sudo chown -R jenkins:jenkins . || true
            '''
            cleanWs(
                cleanWhenSuccess: true,
                cleanWhenFailure: true,
                cleanWhenNotBuilt: true,
                deleteDirs: true
            )
        }
    }
}
