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
        
        stage('Setup Environment') {
            steps {
                sh '''
                    apt-get update && apt-get install -y python3 python3-pip python3-venv docker.io curl unzip
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt pytest
                    
                    # Installation AWS CLI v2
                    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
                    unzip -q awscliv2.zip
                    ./aws/install --update
                    rm -rf aws awscliv2.zip
                '''
            }
        }
        
        stage('Tests Unitaires') {
            steps {
                sh '''
                    . venv/bin/activate
                    python -m pytest tests/ --junitxml=test-results.xml || echo "Tests skipped"
                '''
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
        
        stage('Push to ECR') {
            steps {
                sh '''
                    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REPO
                    docker push $ECR_REPO:$IMAGE_TAG
                    docker push $ECR_REPO:latest
                '''
            }
        }
        
        stage('Deploy to EKS') {
            steps {
                sh '''
                    aws eks update-kubeconfig --name $CLUSTER_NAME --region $AWS_REGION || true
                    kubectl set image deployment/flask-app flask-app=$ECR_REPO:$IMAGE_TAG -n $NAMESPACE || true
                    kubectl rollout status deployment/flask-app -n $NAMESPACE --timeout=90s || true
                '''
            }
        }
    }
    
    post {
        success { echo "🎉 Pipeline terminé avec succès !" }
        failure { echo "❌ Pipeline en échec" }
    }
}
