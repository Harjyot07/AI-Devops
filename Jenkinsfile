pipeline {
    agent any

    environment {
        FRONTEND_IMAGE = "ai-jenkins-frontend"
        BACKEND_IMAGE  = "ai-jenkins-backend"
        GIT_COMMIT_SHORT = sh(
            script: "git rev-parse --short HEAD",
            returnStdout: true
        ).trim()
        
        // 🆓 FREE LOCAL AI - Ollama (runs on your server, zero cost)
        OLLAMA_URL = "http://host.docker.internal:11434"
        
        // Optional: Google Gemini (free tier, 6,000 req/day)
        // GEMINI_API_KEY = credentials('gemini-api-key')  // Uncomment after adding to Jenkins
    }

    stages {

        stage('Checkout Code') {
            steps {
                checkout scm
                sh '''
                echo "Commit: $(git log --oneline -1)"
                echo "Workspace Files:"
                ls -la
                '''
            }
        }

        // 🤖 FREE AI CODE REVIEW (using Ollama - 100% free)
        stage('AI Code Review') {
            steps {
                script {
                    def diff = sh(
                        returnStdout: true, 
                        script: 'git diff HEAD~1 || echo "FIRST_COMMIT"'
                    ).trim()
                    
                    if (diff != "FIRST_COMMIT" && diff.trim()) {
                        echo "🤖 Running FREE AI Code Review with Ollama..."
                        
                        // Save diff to file to avoid escaping issues
                        writeFile file: 'diff.txt', text: diff
                        
                        def review = sh(
                            returnStdout: true,
                            script: '''
                            curl -s ${OLLAMA_URL}/api/generate \
                              -H "Content-Type: application/json" \
                              -d "{
                                \\"model\\": \\"codellama\\",
                                \\"prompt\\": \\"You are a senior DevOps engineer. Review this code diff for: 1) Security issues, 2) Docker best practices, 3) CI/CD improvements. Be concise:\\n$(cat diff.txt | sed 's/"/\\\\"/g' | sed 's/\\n/\\\\n/g')\\",
                                \\"stream\\": false,
                                \\"options\\": { \\"temperature\\": 0.3 }
                              }" 2>/dev/null || echo '{"response": "Ollama not available - skipping AI review"}'
                            '''
                        )
                        
                        echo "📝 AI Review: ${review}"
                    } else {
                        echo "ℹ️ First commit or no diff - skipping AI review"
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
                            echo "=== Building Frontend ==="
                            docker build -t ${FRONTEND_IMAGE}:${BUILD_NUMBER}-${GIT_COMMIT_SHORT} .
                            docker tag ${FRONTEND_IMAGE}:${BUILD_NUMBER}-${GIT_COMMIT_SHORT} ${FRONTEND_IMAGE}:latest
                            '''
                        }
                    }
                }
                stage('Build Backend') {
                    steps {
                        dir('backend') {
                            sh '''
                            echo "=== Building Backend ==="
                            docker build -t ${BACKEND_IMAGE}:${BUILD_NUMBER}-${GIT_COMMIT_SHORT} .
                            docker tag ${BACKEND_IMAGE}:${BUILD_NUMBER}-${GIT_COMMIT_SHORT} ${BACKEND_IMAGE}:latest
                            '''
                        }
                    }
                }
            }
        }

        stage('Deploy Stack') {
            steps {
                sh '''
                echo "=== Deploying Stack ==="
                docker compose down || true
                docker compose up -d --build
                echo "=== Running Containers ==="
                docker ps
                '''
            }
        }

        stage('Verify & Health Check') {
            steps {
                sh '''
                echo "=== Container Verification ==="
                docker ps -a
                
                echo "=== Waiting for services (15s) ==="
                sleep 15
                
                echo "=== Frontend Health Check ==="
                curl -sf http://localhost:3000 && echo "✅ Frontend OK" || echo "⚠️ Frontend not responding"
                
                echo "=== Backend Health Check ==="
                curl -sf http://localhost:5000 && echo "✅ Backend OK" || echo "⚠️ Backend not responding (check your backend port - maybe 3001?)"
                
                echo "=== Prometheus Check ==="
                curl -sf http://localhost:9090 && echo "✅ Prometheus OK" || echo "⚠️ Prometheus not responding"
                
                echo "=== Grafana Check ==="
                curl -sf http://localhost:3003 && echo "✅ Grafana OK" || echo "⚠️ Grafana not responding"
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
                        script: 'docker logs backend --tail 30 2>&1 || echo "NO_LOGS"'
                    ).trim()
                    
                    if (logs != "NO_LOGS" && logs.trim()) {
                        writeFile file: 'logs.txt', text: logs
                        
                        def analysis = sh(
                            returnStdout: true,
                            script: '''
                            curl -s ${OLLAMA_URL}/api/generate \
                              -H "Content-Type: application/json" \
                              -d "{
                                \\"model\\": \\"codellama\\",
                                \\"prompt\\": \\"Analyze these Docker logs for errors and warnings. Give a 2-sentence summary:\\n$(cat logs.txt | sed 's/"/\\\\"/g' | head -c 2000)\\",
                                \\"stream\\": false
                              }" 2>/dev/null || echo '{"response": "Ollama unavailable"}'
                            '''
                        )
                        
                        echo "📊 AI Log Analysis: ${analysis}"
                    } else {
                        echo "ℹ️ No logs available for analysis"
                    }
                }
            }
        }
    }

    // ✅ FIXED: post block now works correctly with 'agent any'
    post {
        always {
            node(null) {  // Ensure we have a node context
                echo '🔧 Pipeline completed - cleaning up'
                sh 'docker image prune -f || true'
                sh 'rm -f diff.txt logs.txt || true'
            }
        }
        success {
            node(null) {
                echo '✅ Deployment Successful!'
                sh '''
                echo "Build #${BUILD_NUMBER} completed"
                echo "Images: ${FRONTEND_IMAGE}:${BUILD_NUMBER}-${GIT_COMMIT_SHORT}, ${BACKEND_IMAGE}:${BUILD_NUMBER}-${GIT_COMMIT_SHORT}"
                '''
            }
        }
        failure {
            node(null) {
                echo '❌ Deployment Failed!'
                sh '''
                echo "=== FAILURE DIAGNOSIS ==="
                echo "Recent container logs:"
                docker logs backend --tail 20 2>/dev/null || true
                docker logs frontend --tail 20 2>/dev/null || true
                echo "========================"
                '''
            }
        }
    }
}
