from flask import Flask, render_template_string

app = Flask(__name__)

# HTML template for the landing page
LANDING_PAGE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DevOps CI/CD Pipeline Demo</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            color: #333;
        }
        
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            padding: 40px;
            max-width: 600px;
            text-align: center;
            animation: fadeIn 0.8s ease-in;
        }
        
        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(-20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        h1 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 2.5em;
        }
        
        .subtitle {
            color: #764ba2;
            font-size: 1.2em;
            margin-bottom: 30px;
        }
        
        .info {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            text-align: left;
        }
        
        .info h2 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.5em;
        }
        
        .info ul {
            list-style: none;
            padding-left: 0;
        }
        
        .info li {
            padding: 8px 0;
            border-bottom: 1px solid #e9ecef;
        }
        
        .info li:last-child {
            border-bottom: none;
        }
        
        .info li strong {
            color: #764ba2;
        }
        
        .success-badge {
            display: inline-block;
            background: #28a745;
            color: white;
            padding: 10px 20px;
            border-radius: 25px;
            margin-top: 20px;
            font-weight: bold;
        }
        
        .footer {
            margin-top: 30px;
            color: #6c757d;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 DevOps CI/CD Pipeline</h1>
        <p class="subtitle">Python Flask Application</p>
        
        <div class="info">
            <h2>Pipeline Architecture</h2>
            <ul>
                <li><strong>Source:</strong> GitHub Repository</li>
                <li><strong>CI/CD:</strong> Jenkins Pipeline</li>
                <li><strong>Containerization:</strong> Docker</li>
                <li><strong>Container Registry:</strong> AWS ECR</li>
                <li><strong>Orchestration:</strong> AWS ECS</li>
            </ul>
        </div>
        
        <div class="success-badge">✅ Deployment Successful!</div>
        
        <div class="footer">
            <p>Automated deployment via Jenkins CI/CD Pipeline</p>
            <p>Built with Flask • Containerized with Docker • Deployed on AWS ECS</p>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def landing_page():
    """Main landing page route"""
    return render_template_string(LANDING_PAGE_HTML)

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    return {'status': 'healthy', 'service': 'flask-app'}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

