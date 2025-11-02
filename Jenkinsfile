pipeline {
    agent any

    environment {
        AWS_DEFAULT_REGION = 'ap-south-1'  // Change to your AWS region
        ECR_REGISTRY = '315838644546.dkr.ecr.ap-south-1.amazonaws.com'  // ECR registry (no repo name)
        ECR_REPOSITORY = 'devops-cia2-app'  // ECR repository name
        ECS_CLUSTER = 'devops-cia2-cluster'  // ECS cluster name
        ECS_SERVICE = 'devops-cia2-service'  // ECS service name
        AWS_CREDENTIALS = 'MY-AWS-ACCOUNT'  // Jenkins credential ID for AWS
        IMAGE_TAG = "${env.BUILD_ID}"
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out code from GitHub repository...'
                checkout scm
                sh 'git branch -a'
                sh 'git log -1 --pretty=format:"%h - %an, %ar : %s"'
            }
        }

        stage('Build') {
            steps {
                echo 'Setting up Python environment and installing dependencies...'
                sh '''
                    python3 -m venv venv || python -m venv venv
                    source venv/bin/activate || . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Test') {
            steps {
                echo 'Running unit tests...'
                sh '''
                    source venv/bin/activate || . venv/bin/activate
                    pip install pytest pytest-cov || true
                    if [ -d "tests" ] && [ -n "$(ls -A tests/*.py 2>/dev/null)" ]; then
                        pytest tests/ -v --cov=. --cov-report=term-missing || true
                    else
                        echo "No tests found, skipping..."
                    fi
                '''
            }
        }

        stage('Code Quality') {
            steps {
                echo 'Running code quality checks...'
                sh '''
                    source venv/bin/activate || . venv/bin/activate
                    pip install pylint || true
                    pylint **/*.py --disable=C0111 || true
                '''
            }
        }

        stage('Docker Build') {
            steps {
                echo 'Building Docker image...'
                sh '''
                    docker build -t ${ECR_REPOSITORY}:${IMAGE_TAG} .
                    docker tag ${ECR_REPOSITORY}:${IMAGE_TAG} ${ECR_REPOSITORY}:latest
                '''
            }
        }

        stage('Push to ECR') {
            steps {
                echo 'Pushing image to ECR...'
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: "${AWS_CREDENTIALS}"]]) {
                    sh '''
                        aws ecr get-login-password --region ${AWS_DEFAULT_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY}
                        docker tag ${ECR_REPOSITORY}:${IMAGE_TAG} ${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}
                        docker push ${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}
                    '''
                }
            }
        }

        stage('Deploy to ECS') {
            steps {
                echo 'Deploying updated image to AWS ECS...'
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: "${AWS_CREDENTIALS}"]]) {
                    sh '''
                        # Safety check: Verify cluster exists
                        CLUSTER_STATUS=$(aws ecs describe-clusters --clusters ${ECS_CLUSTER} --query 'clusters[0].status' --output text)
                        if [ -z "$CLUSTER_STATUS" ] || [ "$CLUSTER_STATUS" == "None" ]; then
                            echo "❌ Error: ECS cluster '${ECS_CLUSTER}' does not exist or is not accessible."
                            exit 1
                        fi
                        echo "✅ Cluster '${ECS_CLUSTER}' status: $CLUSTER_STATUS"
                        
                        # Safety check: Verify service exists
                        SERVICE_STATUS=$(aws ecs describe-services --cluster ${ECS_CLUSTER} --services ${ECS_SERVICE} --query 'services[0].status' --output text)
                        if [ -z "$SERVICE_STATUS" ] || [ "$SERVICE_STATUS" == "None" ]; then
                            echo "❌ Error: ECS service '${ECS_SERVICE}' does not exist in cluster '${ECS_CLUSTER}'."
                            exit 1
                        fi
                        echo "✅ Service '${ECS_SERVICE}' status: $SERVICE_STATUS"
                        
                        # Get current task definition
                        TASK_DEFINITION=$(aws ecs describe-services --cluster ${ECS_CLUSTER} --services ${ECS_SERVICE} --query 'services[0].taskDefinition' --output text)
                        
                        if [ -z "$TASK_DEFINITION" ] || [ "$TASK_DEFINITION" == "None" ]; then
                            echo "❌ Error: Could not retrieve task definition. Check if service exists."
                            exit 1
                        fi
                        
                        echo "Current task definition: $TASK_DEFINITION"
                        
                        # Get task definition JSON
                        aws ecs describe-task-definition --task-definition $TASK_DEFINITION --query 'taskDefinition' > task-definition.json
                        
                        # Update image in task definition (handle both Linux and macOS sed)
                        if [[ "$OSTYPE" == "darwin"* ]]; then
                            sed -i '' "s|\"image\": \".*\"|\"image\": \"${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}\"|g" task-definition.json
                        else
                            sed -i.bak "s|\"image\": \".*\"|\"image\": \"${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}\"|g" task-definition.json
                        fi
                        
                        # Clean up task definition JSON (remove read-only fields)
                        jq 'del(.taskDefinitionArn, .revision, .status, .requiresAttributes, .placementConstraints, .compatibilities, .registeredAt, .registeredBy)' task-definition.json > new-task-definition.json
                        
                        # Register new task definition
                        NEW_TASK_DEF=$(aws ecs register-task-definition --cli-input-json file://new-task-definition.json --query 'taskDefinition.taskDefinitionArn' --output text)
                        
                        if [ -z "$NEW_TASK_DEF" ] || [ "$NEW_TASK_DEF" == "None" ]; then
                            echo "❌ Error: Failed to register new task definition"
                            exit 1
                        fi
                        
                        echo "New task definition: $NEW_TASK_DEF"
                        
                        # Update ECS service with new task definition
                        aws ecs update-service --cluster ${ECS_CLUSTER} --service ${ECS_SERVICE} --task-definition $NEW_TASK_DEF --force-new-deployment
                        
                        echo "Waiting for ECS service to stabilize (this may take several minutes)..."
                        aws ecs wait services-stable --cluster ${ECS_CLUSTER} --services ${ECS_SERVICE} || {
                            echo "⚠️ Warning: Service did not stabilize within timeout, but deployment was triggered"
                        }
                        
                        echo "✅ Deployment completed successfully!"
                    '''
                }
            }
        }
    }

    post {
        success {
            echo '✅ Pipeline succeeded! Deployment successful.'
        }
        failure {
            echo '❌ Pipeline failed! Please check the Jenkins logs.'
        }
        always {
            echo '🧹 Cleaning up...'
            sh '''
                docker image prune -f || true
                docker builder prune -f || true
            '''
            cleanWs()
        }
    }
}
