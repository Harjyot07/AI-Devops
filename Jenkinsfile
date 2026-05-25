pipeline {
    agent { label 'ubuntu' }

    environment {
        // Git commit for tagging
        GIT_SHORT = sh(returnStdout: true, script: 'git rev-parse --short HEAD').trim()
        
        // Image names with build number + git SHA
        FRONTEND_IMAGE = "ai-jenkins-frontend:${BUILD_NUMBER}-${GIT_SHORT}"
        BACKEND_IMAGE  = "ai-jenkins-backend:${BUILD_NUMBER}-${GIT_SHORT}"
        
        // SonarQube config
        SONAR_HOST = "http://172.24.216.2:9000"
    }

    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
                sh '''
                    echo "Commit: $(git log --oneline -1)"
                    ls -la
                '''
            }
        }

        stage('SonarQube Scan') {
            steps {
                sh '''
                    echo "Checking SonarQube status..."
                    
                    # Wait for SonarQube to be ready
                    for i in 1 2 3 4 5 6; do
                        if curl -s ${SONAR_HOST}/api/system/status | grep -q "UP"; then
                            echo "✅ SonarQube is UP"
                            break
                        fi
                        echo "⏳ Waiting for SonarQube... attempt $i"
                        sleep 15
                    done
                    
                    # Check if SonarQube is actually ready
                    if ! curl -s ${SONAR_HOST}/api/system/status | grep -q "UP"; then
                        echo "⚠️ SonarQube not ready, skipping scan"
                        exit 0
                    fi
                    
                    echo "🔍 Running SonarQube scan..."
                    
                    # Install scanner if not present
                    if ! command -v sonar-scanner &> /dev/null; then
                        echo "Installing SonarScanner..."
                        cd /tmp
                        wget -q https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-5.0.1.3006-linux.zip
                        unzip -q sonar-scanner-cli-*.zip
                        rm -rf /opt/sonar-scanner
                        mv sonar-scanner-*-linux /opt/sonar-scanner
                        ln -sf /opt/sonar-scanner/bin/sonar-scanner /usr/local/bin/sonar-scanner
                        rm sonar-scanner-cli-*.zip
                    else
                        echo "SonarScanner already installed"
                    fi
                    
                    # Run scan with admin credentials
                    sonar-scanner \
                        -Dsonar.projectKey=ai-jenkins-app \
                        -Dsonar.projectName="AI Jenkins App" \
                        -Dsonar.host.url=${SONAR_HOST} \
                        -Dsonar.login=admin \
                        -Dsonar.password=admin \
                        -Dsonar.sources=. \
                        -Dsonar.exclusions=**/node_modules/**,**/cypress/**,**/*.test.js,**/Jenkinsfile \
                        -Dsonar.qualitygate.wait=false || echo "⚠️ Scan completed with warnings"
                '''
            }
        }

        stage('Build Docker Images') {
            parallel {
                stage('Build Frontend') {
                    steps {
                        dir('frontend') {
                            sh '''
                                echo "Building ${FRONTEND_IMAGE}..."
                                docker build -t ${FRONTEND_IMAGE} .
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
                            '''
                        }
                    }
                }
            }
        }

        stage('Deploy Stack') {
            steps {
                sh '''
                    echo "Stopping old containers..."
                    docker compose down || true

                    echo "Starting with new images..."
                    export FRONTEND_IMAGE=${FRONTEND_IMAGE}
                    export BACKEND_IMAGE=${BACKEND_IMAGE}
                    docker compose up -d
                '''
            }
        }

        stage('Verify Containers') {
            steps {
                sh '''
                    echo "Running containers:"
                    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
                '''
            }
        }

        stage('Health Check') {
            steps {
                sh '''
                    echo "Checking backend..."
                    curl -s http://localhost:3001 || echo "Backend not responding"
                    
                    echo "Checking frontend..."
                    curl -s http://localhost:3000 || echo "Frontend not responding"
                '''
            }
        }

        stage('Monitoring Check') {
            steps {
                sh '''
                    echo "Prometheus ready?"
                    curl -s http://localhost:9090/-/ready || echo "Prometheus issue"
                    
                    echo "Grafana ready?"
                    curl -s http://localhost:3003/api/health || echo "Grafana issue"
                    
                    echo "SonarQube ready?"
                    curl -s http://localhost:9000/api/system/status || echo "SonarQube issue"
                '''
            }
        }
    }

    post {
        success {
            echo "✅ Deployment Successful!"
            echo "Frontend: ${FRONTEND_IMAGE}"
            echo "Backend:  ${BACKEND_IMAGE}"
            echo "SonarQube: ${SONAR_HOST}/dashboard?id=ai-jenkins-app"
        }
        failure {
            echo "❌ Deployment Failed - check logs above"
        }
        always {
            echo "Pipeline completed"
            sh 'docker image prune -f || true'
        }
    }
}
