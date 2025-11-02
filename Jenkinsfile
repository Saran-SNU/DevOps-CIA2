pipeline {
    agent any
    
    environment {
        AWS_DEFAULT_REGION = 'ap-south-1'  // Change to your AWS region
        ECR_REGISTRY = '315838644546.dkr.ecr.ap-south-1.amazonaws.com/devops-cia2-app'  // Update with your ECR registry
        ECR_REPOSITORY = 'devops-cia2-app'  // Update with your ECR repository name
        ECS_CLUSTER = 'devops-cia2-cluster'  // Update with your ECS cluster name
        ECS_SERVICE = 'devops-cia2-service'  // Update with your ECS service name
        AWS_CREDENTIALS = 'MY-AWS-ACCOUNT'  // Update with your Jenkins credential ID
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
                echo 'Installing dependencies and running unit tests...'
                sh '''
                    python -m pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install pytest pytest-cov
                '''
            }
        }
        
        stage('Test') {
            steps {
                echo 'Running unit tests...'
                sh '''
                    python -m pytest tests/ -v --cov=. --cov-report=term-missing || true
                '''
            }
        }
        
        stage('Code Quality') {
            steps {
                echo 'Running code quality checks...'
                sh '''
                    pip install pylint || true
                    pylint app.py --disable=C0111 || true
                '''
            }
        }
        
        stage('Docker Build') {
            steps {
                echo 'Building Docker image...'
                script {
                    dockerImage = docker.build("${ECR_REPOSITORY}:${IMAGE_TAG}", ".")
                    dockerImage.tag("${ECR_REPOSITORY}:latest")
                }
            }
        }
        
        stage('Push to ECR') {
            steps {
                echo 'Authenticating with AWS ECR and pushing image...'
                script {
                    withCredentials([aws(credentialsId: "${AWS_CREDENTIALS}", regionVariable: 'AWS_REGION')]) {
                        sh '''
                            aws ecr get-login-password --region ${AWS_DEFAULT_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY}
                            docker tag ${ECR_REPOSITORY}:${IMAGE_TAG} ${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}
                            docker tag ${ECR_REPOSITORY}:${IMAGE_TAG} ${ECR_REGISTRY}/${ECR_REPOSITORY}:latest
                            docker push ${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}
                            docker push ${ECR_REGISTRY}/${ECR_REPOSITORY}:latest
                        '''
                    }
                }
            }
        }
        
        stage('Deploy to ECS') {
            steps {
                echo 'Deploying to AWS ECS...'
                script {
                    withCredentials([aws(credentialsId: "${AWS_CREDENTIALS}", regionVariable: 'AWS_REGION')]) {
                        sh '''
                            # Get current task definition
                            TASK_DEFINITION=$(aws ecs describe-services --cluster ${ECS_CLUSTER} --services ${ECS_SERVICE} --query 'services[0].taskDefinition' --output text)
                            
                            # Get task definition JSON
                            aws ecs describe-task-definition --task-definition $TASK_DEFINITION --query 'taskDefinition' > task-definition.json
                            
                            # Update image in task definition
                            sed -i.bak "s|\"image\": \".*\"|\"image\": \"${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}\"|g" task-definition.json
                            
                            # Remove fields that shouldn't be in new task definition
                            jq 'del(.taskDefinitionArn, .revision, .status, .requiresAttributes, .placementConstraints, .compatibilities, .registeredAt, .registeredBy)' task-definition.json > new-task-definition.json
                            
                            # Register new task definition
                            NEW_TASK_DEF=$(aws ecs register-task-definition --cli-input-json file://new-task-definition.json --query 'taskDefinition.taskDefinitionArn' --output text)
                            
                            # Update ECS service with new task definition
                            aws ecs update-service --cluster ${ECS_CLUSTER} --service ${ECS_SERVICE} --task-definition $NEW_TASK_DEF --force-new-deployment
                            
                            # Wait for service to stabilize
                            echo "Waiting for ECS service to stabilize..."
                            aws ecs wait services-stable --cluster ${ECS_CLUSTER} --services ${ECS_SERVICE}
                            
                            echo "Deployment completed successfully!"
                        '''
                    }
                }
            }
        }
    }
    
    post {
        success {
            echo 'Pipeline succeeded! Sending success notification...'
            // Add email/Slack notification here
            // emailext (
            //     subject: "SUCCESS: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'",
            //     body: "Pipeline succeeded. Check console output at ${env.BUILD_URL}",
            //     to: "your-email@example.com"
            // )
        }
        failure {
            echo 'Pipeline failed! Sending failure notification...'
            // Add email/Slack notification here
            // emailext (
            //     subject: "FAILED: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'",
            //     body: "Pipeline failed. Check console output at ${env.BUILD_URL}",
            //     to: "your-email@example.com"
            // )
        }
        always {
            echo 'Cleaning up...'
            sh 'docker image prune -f || true'
            cleanWs()
        }
    }
}

