pipeline {
    agent any

    environment {
        FRONTEND_IMAGE = "ai-jenkins-frontend"
        BACKEND_IMAGE  = "ai-jenkins-backend"
        GIT_COMMIT_SHORT = sh(
            script: "git rev-parse --short HEAD",
            returnStdout: true
        ).trim()
        
        // 🔑 FREE OPTION 1: Google Gemini (6,000 req/day free)
        GEMINI_API_KEY = credentials('gemini-api-key')  // Get from Google AI Studio
        
        // 🔑 FREE OPTION 2: Ollama (LOCAL - runs on your server, 100% free)
        OLLAMA_URL = "http://localhost:11434"  // Or host.docker.internal:11434 if in Docker
        
        // Choose your AI: 'gemini' or 'ollama'
        AI_PROVIDER = "gemini"  // Switch to "ollama" for local free AI
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

        // 🤖 FREE AI CODE REVIEW STAGE
        stage('AI Code Review') {
            steps {
                script {
                    def diff = sh(
                        returnStdout: true, 
                        script: 'git diff HEAD~1 || echo "No previous commit diff"'
                    ).trim()
                    
                    if (diff && diff != "No previous commit diff") {
                        echo "🤖 Running FREE AI Code Review..."
                        
                        def review = ""
                        
                        if (env.AI_PROVIDER == "gemini") {
                            // FREE Google Gemini API
                            review = sh(
                                returnStdout: true,
                                script: """
                                curl -s https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${GEMINI_API_KEY} \\
                                  -H "Content-Type: application/json" \\
                                  -d '{
                                    "contents": [{
                                      "parts":[{
                                        "text": "You are a senior DevOps engineer. Review this code diff for: 1) Security issues, 2) Docker best practices, 3) CI/CD improvements. Be concise:\\n${diff.replaceAll("'", "\\\\'").replaceAll('"', '\\\\"').replaceAll("\\n", "\\\\n")}"
                                      }]
                                    }],
                                    "generationConfig": {
                                      "maxOutputTokens": 1000,
                                      "temperature": 0.3
                                    }
                                  }'
                                """
                            )
                        } else {
                            // FREE LOCAL Ollama (100% free, runs on your server)
                            review = sh(
                                returnStdout: true,
                                script: """
                                curl -s ${OLLAMA_URL}/api/generate \\
                                  -H "Content-Type: application/json" \\
                                  -d '{
                                    "model": "codellama",
                                    "prompt": "You are a senior DevOps engineer. Review this code diff for security issues, Docker best practices, and CI/CD improvements. Be concise:\\n${diff.replaceAll("'", "\\\\'").replaceAll('"', '\\\\"').replaceAll("\\n", "\\\\n")}",
                                    "stream": false
                                  }'
                                """
                            )
                        }
                        
                        echo "📝 FREE AI Review Results:"
                        echo "${review}"
                    } else {
                        echo "ℹ️ No diff found for AI review"
                    }
                }
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

        // 🤖 FREE AI LOG ANALYSIS
        stage('AI Log Analysis') {
            steps {
                script {
                    echo "🤖 Analyzing logs with FREE AI..."
                    
                    def logs = sh(
                        returnStdout: true,
                        script: 'docker logs backend --tail 50 2>&1 || echo "No backend logs"'
                    ).trim()
                    
                    if (logs && logs != "No backend logs") {
                        def analysis = ""
                        
                        if (env.AI_PROVIDER == "gemini") {
                            analysis = sh(
                                returnStdout: true,
                                script: """
                                curl -s https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${GEMINI_API_KEY} \\
                                  -H "Content-Type: application/json" \\
                                  -d '{
                                    "contents": [{
                                      "parts":[{
                                        "text": "Analyze these Docker logs for errors, warnings, and performance issues. Provide a 3-bullet summary:\\n${logs.replaceAll("'", "\\\\'").replaceAll('"', '\\\\"').replaceAll("\\n", "\\\\n")}"
                                      }]
                                    }],
                                    "generationConfig": {
                                      "maxOutputTokens": 500,
                                      "temperature": 0.2
                                    }
                                  }'
                                """
                            )
                        } else {
                            analysis = sh(
                                returnStdout: true,
                                script: """
                                curl -s ${OLLAMA_URL}/api/generate \\
                                  -H "Content-Type: application/json" \\
                                  -d '{
                                    "model": "codellama",
                                    "prompt": "Analyze these Docker logs for errors and performance issues. Provide a brief summary:\\n${logs.replaceAll("'", "\\\\'").replaceAll('"', '\\\\"').replaceAll("\\n", "\\\\n")}",
                                    "stream": false
                                  }'
                                """
                            )
                        }
                        
                        echo "📊 FREE AI Log Analysis:"
                        echo "${analysis}"
                    }
                }
            }
        }
    }

    post {
        always {
            echo 'Pipeline completed'
            sh 'docker image prune -f || true'
        }
        success {
            script {
                echo '✅ Deployment Successful'
                if (env.AI_PROVIDER == "gemini") {
                    def celebration = sh(
                        returnStdout: true,
                        script: """
                        curl -s https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${GEMINI_API_KEY} \\
                          -H "Content-Type: application/json" \\
                          -d '{
                            "contents": [{
                              "parts":[{
                                "text": "Write a short, fun deployment success message for a DevOps team. Build #${BUILD_NUMBER} succeeded."
                              }]
                            }]
                          }'
                        """
                    )
                    echo "🎉 ${celebration}"
                }
            }
        }
        failure {
            echo '❌ Deployment Failed - check logs above'
        }
    }
}
