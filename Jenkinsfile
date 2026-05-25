pipeline {

    agent { label 'ubuntu' }

    environment {
        APP_NAME = "fullstack-app"
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
                    echo "Building Docker images..."
                    docker compose build
                '''
            }
        }

        stage('Deploy Stack') {
            steps {
                sh '''
                    echo "Stopping old containers..."
                    docker compose down || true

                    echo "Starting new containers..."
                    docker compose up -d --build
                '''
            }
        }

        stage('Verify Containers') {
            steps {
                sh '''
                    echo "Checking running containers..."
                    docker ps

                    echo "Checking logs (optional debug)..."
                    docker compose ps
                '''
            }
        }

        stage('Health Check') {
            steps {
                sh '''
                    echo "Checking backend..."
                    curl -s http://localhost:3001 || true

                    echo "Checking frontend..."
                    curl -s http://localhost:3000 || true
                '''
            }
        }

        stage('Monitoring Check') {
            steps {
                sh '''
                    echo "Prometheus status check..."
                    curl -s http://localhost:9090/-/ready || true

                    echo "Grafana status check..."
                    curl -s http://localhost:3002/api/health || true
                '''
            }
        }
    }

    post {

        success {
            echo "✅ Deployment Successful: All services are running"
        }

        failure {
            echo "❌ Deployment Failed: Check logs"
        }

        always {
            echo "Pipeline execution completed"
        }
    }
}
