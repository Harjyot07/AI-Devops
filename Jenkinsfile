pipeline {

    agent {label'ubuntu'}

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Deploy App') {
            steps {

                sh '''
                    docker compose down || true
                    docker compose up --build -d
                '''
            }
        }

        stage('Verify') {
            steps {

                sh '''
                    docker ps
                '''
            }
        }
    }

    post {

        success {
            echo "Application Deployed Successfully"
        }

        failure {
            echo "Deployment Failed"
        }
    }
}
