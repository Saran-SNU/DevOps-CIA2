# DevOps CI/CD Pipeline - Python Flask Application

This project demonstrates a complete CI/CD pipeline for deploying a Python Flask web application using Jenkins, Docker, AWS ECR, and AWS ECS.

## 🏗️ Pipeline Architecture

```
GitHub → Jenkins → Docker → AWS ECR → AWS ECS → Public Access
```

### Components

- **Source Code Management**: GitHub Repository
- **CI/CD Tool**: Jenkins Pipeline
- **Containerization**: Docker
- **Container Registry**: AWS Elastic Container Registry (ECR)
- **Container Orchestration**: AWS Elastic Container Service (ECS)

## 📋 Prerequisites

### Local Development
- Python 3.9+
- pip
- Docker (for local testing)

### Jenkins Server
- Jenkins with required plugins:
  - Git Plugin
  - GitHub Plugin
  - Docker Pipeline Plugin
  - AWS Credentials Plugin
  - Pipeline Plugin
- AWS CLI configured or AWS credentials stored in Jenkins

### AWS Account
- ECR repository create
- ECS cluster and service configured
- IAM permissions for ECR push and ECS deployment

## 🚀 Getting Started

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/Saran-SNU/DevOps-CIA2.git
   cd DevOps-CIA2
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application locally**
   ```bash
   python app.py
   ```
   Access the application at: `http://localhost:5000`

4. **Build and run with Docker locally** (optional)
   ```bash
   docker build -t devops-cia2-app:latest .
   docker run -p 5000:5000 devops-cia2-app:latest
   ```

## 📁 Project Structure

```
.
├── app.py              # Flask application
├── requirements.txt    # Python dependencies
├── Dockerfile          # Docker container configuration
├── Jenkinsfile         # Jenkins CI/CD pipeline definition
├── README.md           # Project documentation
├── .gitignore          # Git ignore rules
└── tests/              # Unit tests (optional)
    └── test_app.py
```

## 🔧 Jenkins Configuration

### 1. Install Required Plugins
- Git Plugin
- GitHub Plugin
- Docker Pipeline Plugin
- AWS Credentials Plugin
- Pipeline Plugin

### 2. Configure AWS Credentials in Jenkins
1. Navigate to: **Manage Jenkins → Credentials → Global**
2. Add AWS credentials with ID: `MY-AWS-ACCOUNT`
3. Provide AWS Access Key ID and Secret Access Key with ECR/ECS permissions

### 3. Create Pipeline Job
1. **Jenkins Dashboard → New Item → Pipeline**
2. Configure:
   - **Project URL**: `https://github.com/Saran-SNU/DevOps-CIA2`
   - **Pipeline Definition**: Pipeline script from SCM
   - **SCM**: Git
   - **Repository URL**: `https://github.com/Saran-SNU/DevOps-CIA2.git`
   - **Branch**: `*/main` or `*/master`
   - **Script Path**: `Jenkinsfile`

### 4. Configure GitHub Webhook
1. Go to your GitHub repository: **Settings → Webhooks → Add webhook**
2. **Payload URL**: `http://<jenkins-server-ip>:8080/github-webhook/`
3. **Content type**: `application/json`
4. **Which events**: Select "Just the push event"
5. Click **Add webhook**

This enables automatic Jenkins pipeline triggers on every commit push.

### 5. Update Jenkinsfile Environment Variables
Before running the pipeline, update these variables in `Jenkinsfile`:
- `AWS_DEFAULT_REGION`: Your AWS region (e.g., `us-east-1`)
- `ECR_REGISTRY`: Your ECR registry URL
- `ECR_REPOSITORY`: Your ECR repository name
- `ECS_CLUSTER`: Your ECS cluster name
- `ECS_SERVICE`: Your ECS service name
- `AWS_CREDENTIALS`: Your Jenkins credential ID for AWS

## 📊 Pipeline Stages

The Jenkins pipeline consists of the following stages:

1. **Checkout**: Pulls latest code from GitHub
2. **Build**: Installs Python dependencies
3. **Test**: Runs unit tests (if available)
4. **Code Quality**: Runs linting checks
5. **Docker Build**: Builds Docker image
6. **Push to ECR**: Authenticates with AWS ECR and pushes image
7. **Deploy to ECS**: Updates ECS service with new image

## 🐳 Docker Configuration

The Dockerfile creates a lightweight Python 3.9 container:
- Sets working directory to `/app`
- Installs dependencies from `requirements.txt`
- Copies application code
- Exposes port 5000
- Runs Flask application

## ☁️ AWS Configuration

### ECR Setup
1. Create ECR repository in AWS Console
2. Note the repository URI format: `<account-id>.dkr.ecr.<region>.amazonaws.com/<repo-name>`
3. Configure IAM permissions for Jenkins to push images

### ECS Setup
1. **Task Definition**: Configure container with ECR image, port 5000
2. **Cluster**: Create ECS cluster (Fargate or EC2)
3. **Service**: Create service with public IP enabled
4. **Security Group**: Allow inbound traffic on port 5000

## 🌐 Accessing the Application

After successful deployment:
1. Find the task public IP in ECS Console → Cluster → Tasks → Networking tab
2. Access the application at: `http://<public-ip>:5000`
3. Health check endpoint: `http://<public-ip>:5000/health`

## 🧪 Testing

Run tests locally:
```bash
pip install pytest pytest-cov
pytest tests/ -v
```

## 📝 CI/CD Workflow

1. **Developer commits code** → Push to GitHub
2. **GitHub webhook triggers Jenkins** → Automatic pipeline execution
3. **Jenkins executes pipeline**:
   - Checks out code
   - Builds and tests application
   - Builds Docker image
   - Pushes to ECR
   - Deploys to ECS
4. **Application accessible** → Public IP on port 5000

## 📸 Required Screenshots for Submission

- Jenkins pipeline stages view (all stages successful)
- ECR repository showing Docker images with tags
- ECS cluster showing running tasks with public IP
- Jenkinsfile code in repository
- Application running in browser at `http://<public-ip>:5000`
- CloudWatch logs (optional advantage task)

## 🔍 Monitoring

- **CloudWatch Logs**: Configure log groups for ECS tasks
- **Jenkins Notifications**: Email/Slack notifications on build status
- **Health Check**: `/health` endpoint for monitoring

## 📧 Support

For issues or questions, please create an issue in the GitHub repository.

## 📄 License

This project is created for educational purposes as part of DevOps coursework.

---

**Built with ❤️ using Flask, Docker, Jenkins, and AWS**

