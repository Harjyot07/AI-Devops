pipeline {
    agent { label 'ubuntu' }

    environment {
        GIT_SHORT = sh(returnStdout: true, script: 'git rev-parse --short HEAD').trim()
        FRONTEND_IMAGE = "ai-jenkins-frontend:${BUILD_NUMBER}-${GIT_SHORT}"
        BACKEND_IMAGE  = "ai-jenkins-backend:${BUILD_NUMBER}-${GIT_SHORT}"
        
        // SonarQube config
        SONAR_HOST = "http://172.24.216.2:9000"
        SONAR_TOKEN = "your-sonar-token-here"  // We'll generate this below
    }

    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }

        // NEW: SonarQube Code Quality Scan
        stage('SonarQube Scan') {
            steps {
                sh '''
                    echo "🔍 Running SonarQube code quality scan..."
                    
                    # Install SonarScanner if not present
                    if ! command -v sonar-scanner &> /dev/null; then
                        echo "Installing SonarScanner..."
                        wget -q https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-5.0.1.3006-linux.zip
                        unzip -q sonar-scanner-cli-*.zip
                        mv sonar-scanner-*-linux /opt/sonar-scanner
                        ln -sf /opt/sonar-scanner/bin/sonar-scanner /usr/local/bin/sonar-scanner
                        rm sonar-scanner-cli-*.zip
                    fi
                    
                    # Run scan on your code
                    sonar-scanner \
                        -Dsonar.projectKey=ai-jenkins-app \
                        -Dsonar.projectName="AI Jenkins App" \
                        -Dsonar.host.url=${SONAR_HOST} \
                        -Dsonar.token=${SONAR_TOKEN} \
                        -Dsonar.sources=. \
                        -Dsonar.exclusions=**/node_modules/**,**/cypress/**,**/*.test.js \
                        -Dsonar.qualitygate.wait=true
                '''
            }
        }

        stage('Build Docker Images') {
            steps {
                sh '''
                    echo "Building images: ${FRONTEND_IMAGE} and ${BACKEND_IMAGE}"
                    docker compose build
                '''
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
            echo "✅ Deployed: ${FRONTEND_IMAGE} & ${BACKEND_IMAGE}"
            echo "📊 SonarQube Report: ${SONAR_HOST}/dashboard?id=ai-jenkins-app"
        }
        failure {
            echo "❌ Failed - check logs above"
        }
        always {
            echo "Pipeline done"
        }
    }
}
