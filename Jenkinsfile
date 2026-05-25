pipeline {
    agent { label 'ubuntu' }

    environment {
        // Git commit for tagging
        GIT_SHORT = sh(returnStdout: true, script: 'git rev-parse --short HEAD').trim()
        
        // Image names with build number + git SHA
        FRONTEND_IMAGE = "ai-jenkins-frontend:${BUILD_NUMBER}-${GIT_SHORT}"
        BACKEND_IMAGE  = "ai-jenkins-backend:${BUILD_NUMBER}-${GIT_SHORT}"
    }

    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
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
                '''
            }
        }
    }

    post {
        success {
            echo "✅ Deployed: ${FRONTEND_IMAGE} & ${BACKEND_IMAGE}"
        }
        failure {
            echo "❌ Failed - check logs above"
        }
        always {
            echo "Pipeline done"
            // Optional: cleanWs()
        }
    }
}
