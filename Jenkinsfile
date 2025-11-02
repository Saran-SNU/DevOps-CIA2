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
                echo 'Installing dependencies and setting up Python environment...'
                sh '''
                    sudo apt update -y
                    sudo apt install -y python3 python3-venv python3-pip

                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Test') {
            steps {
                echo 'Running unit tests...'
                sh '''
                    . venv/bin/activate
                    pip install pytest pytest-cov || true
                    pytest tests/ -v --cov=. --cov-report=term-missing || true
                '''
            }
        }

        stage('Code Quality') {
            steps {
                echo 'Running code quality checks...'
                sh '''
                    . venv/bin/activate
                    pip install pylint || true
                    pylint app.py --disable=C0111 || true
                '''
            }
        }

        stage('Docker Build') {
            steps {
                echo 'Building Docker image...'
                sh '''
                    sudo apt install -y docker.io || true
                    docker build -t ${ECR_REPOSITORY}:${IMAGE_TAG} .
                    docker tag ${ECR_REPOSITORY}:${IMAGE_TAG} ${ECR_REPOSITORY}:latest
                '''
            }
        }

        stage('Push to ECR') {
            steps {
                echo 'Authenticating with AWS ECR and pushing image...'
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: "${AWS_CREDENTIALS}"]]) {
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

        stage('Deploy to ECS') {
            steps {
                echo 'Deploying updated image to AWS ECS...'
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: "${AWS_CREDENTIALS}"]]) {
                    sh '''
                        sudo apt install -y jq

                        TASK_DEFINITION=$(aws ecs describe-services --cluster ${ECS_CLUSTER} --services ${ECS_SERVICE} --query 'services[0].taskDefinition' --output text)

                        aws ecs describe-task-definition --task-definition $TASK_DEFINITION --query 'taskDefinition' > task-definition.json

                        sed -i.bak "s|\"image\": \".*\"|\"image\": \"${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}\"|g" task-definition.json

                        jq 'del(.taskDefinitionArn, .revision, .status, .requiresAttributes, .placementConstraints, .compatibilities, .registeredAt, .registeredBy)' task-definition.json > new-task-definition.json

                        NEW_TASK_DEF=$(aws ecs register-task-definition --cli-input-json file://new-task-definition.json --query 'taskDefinition.taskDefinitionArn' --output text)

                        aws ecs update-service --cluster ${ECS_CLUSTER} --service ${ECS_SERVICE} --task-definition $NEW_TASK_DEF --force-new-deployment

                        echo "Waiting for ECS service to stabilize..."
                        aws ecs wait services-stable --cluster ${ECS_CLUSTER} --services ${ECS_SERVICE}

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
                docker system prune -af || true
            '''
            cleanWs()
        }
    }
}
