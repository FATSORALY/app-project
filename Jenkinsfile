pipeline {
    agent any
    
    environment {
        AWS_REGION     = 'eu-west-3'
        AWS_ACCOUNT_ID = '240676008744'
        ECR_REPO       = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/devops-free-tier-app"
        CLUSTER_NAME   = 'devops-free-tier'
        NAMESPACE      = 'app'
        IMAGE_TAG      = "${env.BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Tests Unitaires') {
            steps {
                sh 'pip install -r requirements.txt pytest'
                sh 'pytest tests/ --junitxml=test-results.xml'
            }
            post {
                always {
                    junit 'test-results.xml'
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                sh 'docker build -t ${ECR_REPO}:${IMAGE_TAG} .'
                sh 'docker tag ${ECR_REPO}:${IMAGE_TAG} ${ECR_REPO}:latest'
            }
        }
        
        stage('Trivy Security Scan') {
            steps {
                sh 'trivy image --exit-code 1 --severity HIGH,CRITICAL ${ECR_REPO}:${IMAGE_TAG}'
            }
        }
        
        stage('Push to ECR') {
            steps {
                withAWS(credentials: 'aws-jenkins-creds', region: AWS_REGION) {
                    sh '''
                        aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REPO
                        docker push $ECR_REPO:$IMAGE_TAG
                        docker push $ECR_REPO:latest
                    '''
                }
            }
        }
        
        stage('Deploy to EKS') {
            steps {
                withAWS(credentials: 'aws-jenkins-creds', region: AWS_REGION) {
                    sh '''
                        aws eks update-kubeconfig --name $CLUSTER_NAME --region $AWS_REGION
                        kubectl set image deployment/flask-app flask-app=$ECR_REPO:$IMAGE_TAG -n $NAMESPACE || true
                        kubectl rollout status deployment/flask-app -n $NAMESPACE --timeout=120s
                    '''
                }
            }
        }
    }
    
    post {
        success { echo "✅ Pipeline terminé avec succès !" }
        failure { echo "❌ Pipeline en échec" }
    }
}
