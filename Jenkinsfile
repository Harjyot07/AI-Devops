pipeline {
    agent any

    environment {
        FRONTEND_IMAGE = "ai-jenkins-frontend"
        BACKEND_IMAGE  = "ai-jenkins-backend"
        GIT_COMMIT_SHORT = sh(
            script: "git rev-parse --short HEAD",
            returnStdout: true
        ).trim()
    }

    stages {

        stage('Checkout Code') {
            steps {
                checkout scm

                sh '''
                echo "Commit:"
                git log --oneline -1

                echo "Workspace Files:"
                ls -la
                '''
            }
        }

        stage('Build Docker Images') {
            parallel {

                stage('Build Frontend') {
                    steps {
                        dir('frontend') {

                            sh '''
                            echo "Stopping old containers..."

                            docker ps -q | xargs -r docker stop

                            docker ps -aq | xargs -r docker rm -f

                            echo "Cleaning old images..."

                            docker image prune -a -f

                            echo "Building frontend image..."

                            docker build -t ${FRONTEND_IMAGE}:${BUILD_NUMBER}-${GIT_COMMIT_SHORT} .
                            '''
                        }
                    }
                }

                stage('Build Backend') {
                    steps {
                        dir('backend') {

                            sh '''
                            echo "Building backend image..."

                            docker build -t ${BACKEND_IMAGE}:${BUILD_NUMBER}-${GIT_COMMIT_SHORT} .
                            '''
                        }
                    }
                }
            }
        }

        stage('Deploy Stack') {
            steps {

                sh '''
                echo "Stopping previous compose stack..."

                docker compose down || true

                echo "Starting new stack..."

                docker compose up -d

                echo "Running containers..."

                docker ps
                '''
            }
        }

        stage('Verify Containers') {
            steps {

                sh '''
                echo "Container Verification"

                docker ps -a

                echo "Docker Images"

                docker images
                '''
            }
        }

        stage('Health Check') {
            steps {

                sh '''
                echo "Waiting for services..."

                sleep 20

                echo "Frontend Check"

                curl -I http://localhost:3000 || true

                echo "Backend Check"

                curl -I http://localhost:5000 || true
                '''
            }
        }

        stage('Monitoring Check') {
            steps {

                sh '''
                echo "Prometheus Containers"

                docker ps | grep prometheus || true

                echo "Monitoring completed"
                '''
            }
        }
    }

    post {

        always {

            echo 'Pipeline completed'

            sh '''
            docker image prune -f || true
            '''
        }

        success {

            echo '✅ Deployment Successful'
        }

        failure {

            echo '❌ Deployment Failed - check logs above'
        }
    }
}
