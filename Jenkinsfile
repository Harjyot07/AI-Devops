pipeline {
    agent any

    environment {
        FRONTEND_IMAGE = "ai-jenkins-frontend"
        BACKEND_IMAGE  = "ai-jenkins-backend"
        GIT_COMMIT_SHORT = sh(
            script: "git rev-parse --short HEAD",
            returnStdout: true
        ).trim()
        
        // 🆓 FREE LOCAL AI - Ollama (now inside Kubernetes)
        OLLAMA_URL = "http://ollama.ollama.svc.cluster.local:11434"
        
        // Kubernetes Configuration
        K8S_NAMESPACE = "app"
        KUBECONFIG_CREDENTIALS = "kubeconfig"  // Add kubeconfig to Jenkins Credentials
        
        // Registry Configuration
        REGISTRY_URL = "localhost:5003"  // CHANGE THIS to your registry
        
        // Optional: Google Gemini
        // GEMINI_API_KEY = credentials('gemini-api-key')
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

        // 🤖 FREE AI CODE REVIEW
        stage('AI Code Review') {
            steps {
                script {
                    def diff = sh(
                        returnStdout: true, 
                        script: 'git diff HEAD~1 || echo "FIRST_COMMIT"'
                    ).trim()
                    
                    if (diff != "FIRST_COMMIT" && diff.trim()) {
                        echo "🤖 Running FREE AI Code Review with Ollama..."
                        
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

        // 🐳 Push to Registry (required for Kubernetes)
        stage('Push Images to Registry') {
            steps {
                script {
                    sh """
                    echo "=== Tagging for Registry ==="
                    docker tag ${FRONTEND_IMAGE}:${BUILD_NUMBER}-${GIT_COMMIT_SHORT} ${REGISTRY_URL}/${FRONTEND_IMAGE}:${BUILD_NUMBER}-${GIT_COMMIT_SHORT}
                    docker tag ${BACKEND_IMAGE}:${BUILD_NUMBER}-${GIT_COMMIT_SHORT} ${REGISTRY_URL}/${BACKEND_IMAGE}:${BUILD_NUMBER}-${GIT_COMMIT_SHORT}
                    
                    echo "=== Pushing Images ==="
                    docker push ${REGISTRY_URL}/${FRONTEND_IMAGE}:${BUILD_NUMBER}-${GIT_COMMIT_SHORT}
                    docker push ${REGISTRY_URL}/${BACKEND_IMAGE}:${BUILD_NUMBER}-${GIT_COMMIT_SHORT}
                    """
                }
            }
        }

        // ☸️ DEPLOY TO KUBERNETES
        stage('Deploy to Kubernetes') {
            steps {
                withCredentials([file(credentialsId: "${KUBECONFIG_CREDENTIALS}", variable: 'KUBECONFIG')]) {
                    script {
                        def IMAGE_TAG = "${BUILD_NUMBER}-${GIT_COMMIT_SHORT}"
                        
                        sh """
                        echo "=== Creating Namespace ==="
                        kubectl apply -f k8s/namespace.yaml
                        
                        echo "=== Updating Image Tags in Manifests ==="
                        sed -i 's|FRONTEND_IMAGE_PLACEHOLDER|${REGISTRY_URL}/${FRONTEND_IMAGE}:${IMAGE_TAG}|g' k8s/frontend-deployment.yaml
                        sed -i 's|BACKEND_IMAGE_PLACEHOLDER|${REGISTRY_URL}/${BACKEND_IMAGE}:${IMAGE_TAG}|g' k8s/backend-deployment.yaml
                        
                        echo "=== Applying App Manifests ==="
                        kubectl apply -f k8s/frontend-deployment.yaml
                        kubectl apply -f k8s/backend-deployment.yaml
                        kubectl apply -f k8s/frontend-service.yaml
                        kubectl apply -f k8s/backend-service.yaml
                        kubectl apply -f k8s/ingress.yaml
                        
                        echo "=== Applying Monitoring Stack ==="
                        kubectl apply -f k8s/prometheus-configmap.yaml
                        kubectl apply -f k8s/prometheus-deployment.yaml
                        kubectl apply -f k8s/prometheus-service.yaml
                        kubectl apply -f k8s/grafana-deployment.yaml
                        kubectl apply -f k8s/grafana-service.yaml
                        
                        echo "=== Applying Ollama ==="
                        kubectl apply -f k8s/ollama-pvc.yaml
                        kubectl apply -f k8s/ollama-deployment.yaml
                        kubectl apply -f k8s/ollama-service.yaml
                        
                        echo "=== Waiting for Rollouts ==="
                        kubectl rollout status deployment/frontend -n ${K8S_NAMESPACE} --timeout=300s
                        kubectl rollout status deployment/backend -n ${K8S_NAMESPACE} --timeout=300s
                        kubectl rollout status deployment/prometheus -n ${K8S_NAMESPACE} --timeout=300s
                        kubectl rollout status deployment/grafana -n ${K8S_NAMESPACE} --timeout=300s
                        kubectl rollout status deployment/ollama -n ollama --timeout=600s
                        """
                    }
                }
            }
        }

        stage('Verify & Health Check') {
            steps {
                withCredentials([file(credentialsId: "${KUBECONFIG_CREDENTIALS}", variable: 'KUBECONFIG')]) {
                    sh '''
                    echo "=== Pod Status ==="
                    kubectl get pods -n ${K8S_NAMESPACE}
                    kubectl get pods -n ollama
                    
                    echo "=== Service Status ==="
                    kubectl get svc -n ${K8S_NAMESPACE}
                    kubectl get svc -n ollama
                    
                    echo "=== Waiting for services (30s) ==="
                    sleep 30
                    
                    echo "=== Frontend Health Check ==="
                    kubectl run curl-test --image=curlimages/curl --rm -i --restart=Never -n ${K8S_NAMESPACE} -- \
                        curl -sf http://frontend:3000 && echo "✅ Frontend OK" || echo "⚠️ Frontend not responding"
                    
                    echo "=== Backend Health Check ==="
                    kubectl run curl-test --image=curlimages/curl --rm -i --restart=Never -n ${K8S_NAMESPACE} -- \
                        curl -sf http://backend:3001 && echo "✅ Backend OK" || echo "⚠️ Backend not responding"
                    
                    echo "=== Prometheus Check ==="
                    kubectl run curl-test --image=curlimages/curl --rm -i --restart=Never -n ${K8S_NAMESPACE} -- \
                        curl -sf http://prometheus:9090 && echo "✅ Prometheus OK" || echo "⚠️ Prometheus not responding"
                    
                    echo "=== Grafana Check ==="
                    kubectl run curl-test --image=curlimages/curl --rm -i --restart=Never -n ${K8S_NAMESPACE} -- \
                        curl -sf http://grafana:3000 && echo "✅ Grafana OK" || echo "⚠️ Grafana not responding"
                    
                    echo "=== Ollama Check ==="
                    kubectl run curl-test --image=curlimages/curl --rm -i --restart=Never -n ollama -- \
                        curl -sf http://ollama:11434/api/tags && echo "✅ Ollama OK" || echo "⚠️ Ollama not responding"
                    '''
                }
            }
        }

        // 🤖 FREE AI LOG ANALYSIS
        stage('AI Log Analysis') {
            steps {
                withCredentials([file(credentialsId: "${KUBECONFIG_CREDENTIALS}", variable: 'KUBECONFIG')]) {
                    script {
                        echo "🤖 Analyzing logs with FREE AI..."
                        
                        def logs = sh(
                            returnStdout: true,
                            script: 'kubectl logs -l app=backend --tail=30 -n ${K8S_NAMESPACE} 2>&1 || echo "NO_LOGS"'
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
                                    \\"prompt\\": \\"Analyze these Kubernetes pod logs for errors and warnings. Give a 2-sentence summary:\\n$(cat logs.txt | sed 's/"/\\\\"/g' | head -c 2000)\\",
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
    }

    post {
        always {
            node(null) {
                echo '🔧 Pipeline completed - cleaning up'
                sh 'docker image prune -f || true'
                sh 'rm -f diff.txt logs.txt || true'
            }
        }
        success {
            node(null) {
                echo '✅ Kubernetes Deployment Successful!'
                sh '''
                echo "Build #${BUILD_NUMBER} completed"
                echo "Images: ${FRONTEND_IMAGE}:${BUILD_NUMBER}-${GIT_COMMIT_SHORT}, ${BACKEND_IMAGE}:${BUILD_NUMBER}-${GIT_COMMIT_SHORT}"
                echo "Namespace: ${K8S_NAMESPACE}"
                echo "Ollama: http://ollama.ollama.svc.cluster.local:11434"
                '''
            }
        }
        failure {
            node(null) {
                echo '❌ Kubernetes Deployment Failed!'
                sh '''
                echo "=== FAILURE DIAGNOSIS ==="
                echo "Recent pod logs:"
                kubectl logs -l app=backend --tail=20 -n ${K8S_NAMESPACE} 2>/dev/null || true
                kubectl logs -l app=frontend --tail=20 -n ${K8S_NAMESPACE} 2>/dev/null || true
                kubectl logs -l app=ollama --tail=20 -n ollama 2>/dev/null || true
                echo "Pod status:"
                kubectl get pods -n ${K8S_NAMESPACE} 2>/dev/null || true
                kubectl get pods -n ollama 2>/dev/null || true
                echo "========================"
                '''
            }
        }
    }
}
