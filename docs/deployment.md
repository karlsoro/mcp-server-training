# MCP Server Training - Deployment Guide

This guide covers deploying the MCP Server Training project to various cloud platforms using best practices for production environments.

## 🎯 Deployment Overview

The MCP server can be deployed to multiple cloud platforms:

- **AWS**: Lambda functions, ECS, or EC2
- **Google Cloud**: Cloud Run, Cloud Functions, or GKE
- **Cloudflare**: Workers or Pages
- **Azure**: Container Instances or App Service
- **Self-hosted**: Docker containers on any infrastructure

## 🚀 AWS Deployment

### Option 1: AWS Lambda (Recommended)

Lambda provides serverless execution with automatic scaling.

#### Prerequisites
- AWS CLI installed and configured
- AWS SAM CLI installed
- Docker installed

#### Step 1: Create SAM Template

Create `template.yaml`:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Globals:
  Function:
    Timeout: 30
    MemorySize: 512
    Environment:
      Variables:
        LOG_LEVEL: INFO

Resources:
  MCPTrainingServer:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: .
      Handler: src.server.handler
      Runtime: python3.11
      Architectures:
        - x86_64
      Environment:
        Variables:
          NOTION_API_TOKEN: !Ref NotionApiToken
          NOTION_DATABASE_ID: !Ref NotionDatabaseId
          GITHUB_TOKEN: !Ref GitHubToken
          OPENWEATHER_API_KEY: !Ref OpenWeatherApiKey
      Policies:
        - CloudWatchLogsFullAccess
      Events:
        Api:
          Type: Api
          Properties:
            Path: /mcp
            Method: post

  # API Gateway
  MCPApi:
    Type: AWS::Serverless::Api
    Properties:
      StageName: prod
      Cors:
        AllowMethods: "'*'"
        AllowHeaders: "'*'"
        AllowOrigin: "'*'"

Parameters:
  NotionApiToken:
    Type: String
    NoEcho: true
    Description: Notion API Token
  
  NotionDatabaseId:
    Type: String
    Description: Notion Database ID
  
  GitHubToken:
    Type: String
    NoEcho: true
    Description: GitHub Personal Access Token
  
  OpenWeatherApiKey:
    Type: String
    NoEcho: true
    Description: OpenWeather API Key
```

#### Step 2: Create Lambda Handler

Create `src/lambda_handler.py`:

```python
import json
import asyncio
from src.server import MCPTrainingServer

async def handle_mcp_request(event, context):
    """Lambda handler for MCP requests."""
    try:
        # Parse the request body
        body = json.loads(event.get('body', '{}'))
        
        # Create server instance
        server = MCPTrainingServer()
        
        # Handle the request based on type
        request_type = body.get('type')
        
        if request_type == 'list_tools':
            result = await server.list_tools(None, body.get('params', {}))
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps(result.dict())
            }
        
        elif request_type == 'call_tool':
            result = await server.call_tool(None, body.get('params', {}))
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps(result.dict())
            }
        
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid request type'})
            }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def handler(event, context):
    """Main Lambda handler."""
    return asyncio.run(handle_mcp_request(event, context))
```

#### Step 3: Deploy with SAM

```bash
# Build the application
sam build

# Deploy to AWS
sam deploy --guided

# Follow the prompts to configure:
# - Stack name: mcp-training-server
# - AWS Region: us-east-1
# - Parameter values for your API keys
```

#### Step 4: Configure Secrets

Store sensitive data in AWS Secrets Manager:

```bash
# Create secrets
aws secretsmanager create-secret \
    --name mcp-training/notion-token \
    --secret-string "your-notion-token"

aws secretsmanager create-secret \
    --name mcp-training/github-token \
    --secret-string "your-github-token"

aws secretsmanager create-secret \
    --name mcp-training/openweather-key \
    --secret-string "your-openweather-key"
```

### Option 2: AWS ECS with Fargate

For more complex deployments with persistent connections.

#### Step 1: Create ECS Task Definition

```json
{
  "family": "mcp-training-server",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::YOUR_ACCOUNT:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::YOUR_ACCOUNT:role/mcp-training-task-role",
  "containerDefinitions": [
    {
      "name": "mcp-server",
      "image": "YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/mcp-training-server:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "LOG_LEVEL",
          "value": "INFO"
        }
      ],
      "secrets": [
        {
          "name": "NOTION_API_TOKEN",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:YOUR_ACCOUNT:secret:mcp-training/notion-token"
        },
        {
          "name": "GITHUB_TOKEN",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:YOUR_ACCOUNT:secret:mcp-training/github-token"
        },
        {
          "name": "OPENWEATHER_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:YOUR_ACCOUNT:secret:mcp-training/openweather-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/mcp-training-server",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

#### Step 2: Build and Push Docker Image

```bash
# Build image
docker build -t mcp-training-server .

# Tag for ECR
docker tag mcp-training-server:latest YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/mcp-training-server:latest

# Push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com
docker push YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/mcp-training-server:latest
```

## ☁️ Google Cloud Deployment

### Option 1: Cloud Run (Recommended)

Cloud Run provides serverless container execution.

#### Step 1: Create Cloud Run Service

```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/mcp-training-server

# Deploy to Cloud Run
gcloud run deploy mcp-training-server \
  --image gcr.io/YOUR_PROJECT_ID/mcp-training-server \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="LOG_LEVEL=INFO" \
  --set-secrets="NOTION_API_TOKEN=notion-token:latest" \
  --set-secrets="GITHUB_TOKEN=github-token:latest" \
  --set-secrets="OPENWEATHER_API_KEY=openweather-key:latest"
```

#### Step 2: Create Secrets

```bash
# Create secrets
echo -n "your-notion-token" | gcloud secrets create notion-token --data-file=-

echo -n "your-github-token" | gcloud secrets create github-token --data-file=-

echo -n "your-openweather-key" | gcloud secrets create openweather-key --data-file=-
```

### Option 2: Cloud Functions

For simpler deployments without containers.

#### Step 1: Create Function

```python
# main.py
import functions_framework
import json
import asyncio
from src.server import MCPTrainingServer

@functions_framework.http
def mcp_handler(request):
    """HTTP Cloud Function for MCP server."""
    try:
        # Parse request
        request_json = request.get_json()
        
        # Create server instance
        server = MCPTrainingServer()
        
        # Handle request
        request_type = request_json.get('type')
        
        if request_type == 'list_tools':
            result = asyncio.run(server.list_tools(None, request_json.get('params', {})))
            return json.dumps(result.dict())
        
        elif request_type == 'call_tool':
            result = asyncio.run(server.call_tool(None, request_json.get('params', {})))
            return json.dumps(result.dict())
        
        else:
            return json.dumps({'error': 'Invalid request type'}), 400
    
    except Exception as e:
        return json.dumps({'error': str(e)}), 500
```

#### Step 2: Deploy Function

```bash
# Deploy to Cloud Functions
gcloud functions deploy mcp-training-server \
  --runtime python311 \
  --trigger-http \
  --allow-unauthenticated \
  --set-env-vars="LOG_LEVEL=INFO" \
  --set-secrets="NOTION_API_TOKEN=notion-token:latest" \
  --set-secrets="GITHUB_TOKEN=github-token:latest" \
  --set-secrets="OPENWEATHER_API_KEY=openweather-key:latest"
```

## 🌐 Cloudflare Deployment

### Option 1: Cloudflare Workers

For edge computing with global distribution.

#### Step 1: Create Worker Script

```javascript
// worker.js
export default {
  async fetch(request, env, ctx) {
    try {
      const body = await request.json();
      
      // Handle MCP requests
      if (body.type === 'list_tools') {
        return new Response(JSON.stringify({
          tools: [
            {
              name: "get_weather",
              description: "Get weather information",
              inputSchema: {
                type: "object",
                properties: {
                  city: { type: "string" }
                }
              }
            }
            // Add more tools as needed
          ]
        }), {
          headers: { 'Content-Type': 'application/json' }
        });
      }
      
      if (body.type === 'call_tool') {
        // Implement tool calling logic
        const toolName = body.params.name;
        const args = body.params.arguments;
        
        if (toolName === 'get_weather') {
          const response = await fetch(
            `http://api.openweathermap.org/data/2.5/weather?q=${args.city}&appid=${env.OPENWEATHER_API_KEY}&units=metric`
          );
          const weather = await response.json();
          
          return new Response(JSON.stringify({
            content: [{
              type: "text",
              text: JSON.stringify(weather, null, 2)
            }]
          }), {
            headers: { 'Content-Type': 'application/json' }
          });
        }
      }
      
      return new Response(JSON.stringify({ error: 'Invalid request' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
      
    } catch (error) {
      return new Response(JSON.stringify({ error: error.message }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    }
  }
};
```

#### Step 2: Deploy to Workers

```bash
# Install Wrangler CLI
npm install -g wrangler

# Login to Cloudflare
wrangler login

# Deploy worker
wrangler publish
```

#### Step 3: Configure Environment Variables

```bash
# Set secrets
wrangler secret put NOTION_API_TOKEN
wrangler secret put GITHUB_TOKEN
wrangler secret put OPENWEATHER_API_KEY
```

### Option 2: Cloudflare Pages

For static site hosting with serverless functions.

#### Step 1: Create Pages Project

```bash
# Create project structure
mkdir mcp-pages
cd mcp-pages

# Create functions directory
mkdir functions

# Create API function
cat > functions/api/[[route]].js << 'EOF'
export async function onRequest(context) {
  const { request, env } = context;
  
  try {
    const body = await request.json();
    
    // Handle MCP requests
    if (body.type === 'list_tools') {
      return new Response(JSON.stringify({
        tools: [
          {
            name: "get_weather",
            description: "Get weather information"
          }
        ]
      }), {
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    return new Response(JSON.stringify({ error: 'Not implemented' }), {
      status: 501,
      headers: { 'Content-Type': 'application/json' }
    });
    
  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}
EOF
```

#### Step 2: Deploy to Pages

```bash
# Deploy to Cloudflare Pages
wrangler pages publish . --project-name mcp-training-server
```

## 🔧 CI/CD Pipeline

### GitHub Actions Workflow

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy MCP Server

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        pytest tests/
    
    - name: Run linting
      run: |
        flake8 src/ tests/
        black --check src/ tests/

  deploy-aws:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - uses: actions/checkout@v3
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-east-1
    
    - name: Deploy to AWS Lambda
      run: |
        sam build
        sam deploy --no-confirm-changeset --no-fail-on-empty-changeset

  deploy-gcp:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Cloud SDK
      uses: google-github-actions/setup-gcloud@v0
      with:
        project_id: ${{ secrets.GCP_PROJECT_ID }}
        service_account_key: ${{ secrets.GCP_SA_KEY }}
    
    - name: Deploy to Cloud Run
      run: |
        gcloud builds submit --tag gcr.io/${{ secrets.GCP_PROJECT_ID }}/mcp-training-server
        gcloud run deploy mcp-training-server \
          --image gcr.io/${{ secrets.GCP_PROJECT_ID }}/mcp-training-server \
          --platform managed \
          --region us-central1 \
          --allow-unauthenticated
```

## 🔒 Security Best Practices

### 1. Secrets Management

- Use cloud-native secret management (AWS Secrets Manager, GCP Secret Manager)
- Never commit secrets to version control
- Rotate secrets regularly
- Use least-privilege access policies

### 2. Network Security

- Use VPC for AWS deployments
- Configure security groups and firewall rules
- Enable HTTPS/TLS encryption
- Use private subnets for database access

### 3. Application Security

- Validate all input parameters
- Implement rate limiting
- Use secure headers
- Enable logging and monitoring

### 4. Container Security

- Use minimal base images
- Scan for vulnerabilities
- Run containers as non-root users
- Keep dependencies updated

## 📊 Monitoring and Observability

### 1. Logging

Configure structured logging:

```python
import structlog

logger = structlog.get_logger()

# Log important events
logger.info("tool_called", tool_name="get_weather", user_id=user_id)
logger.error("api_error", error=str(e), tool_name=tool_name)
```

### 2. Metrics

Use CloudWatch (AWS) or Cloud Monitoring (GCP):

```python
import boto3

cloudwatch = boto3.client('cloudwatch')

def record_metric(metric_name, value, unit='Count'):
    cloudwatch.put_metric_data(
        Namespace='MCPTraining',
        MetricData=[
            {
                'MetricName': metric_name,
                'Value': value,
                'Unit': unit
            }
        ]
    )
```

### 3. Health Checks

Implement health check endpoints:

```python
@app.route('/health')
def health_check():
    return {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    }
```

## 🚀 Performance Optimization

### 1. Caching

Implement caching for frequently accessed data:

```python
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

async def get_weather_cached(city):
    cache_key = f"weather:{city}"
    cached = redis_client.get(cache_key)
    
    if cached:
        return json.loads(cached)
    
    weather = await get_weather_from_api(city)
    redis_client.setex(cache_key, 300, json.dumps(weather))  # Cache for 5 minutes
    return weather
```

### 2. Connection Pooling

Use connection pooling for database and API connections:

```python
import aiohttp

# Create session with connection pooling
async with aiohttp.ClientSession(
    connector=aiohttp.TCPConnector(limit=100, limit_per_host=30)
) as session:
    # Use session for API calls
    pass
```

### 3. Async Processing

Use async/await for I/O operations:

```python
async def process_multiple_requests(requests):
    tasks = [process_request(req) for req in requests]
    results = await asyncio.gather(*tasks)
    return results
```

## 🔄 Scaling Strategies

### 1. Horizontal Scaling

- Use load balancers
- Implement auto-scaling policies
- Use stateless application design
- Share session data via Redis

### 2. Vertical Scaling

- Increase CPU and memory allocation
- Use larger instance types
- Optimize application performance

### 3. Database Scaling

- Use read replicas
- Implement connection pooling
- Use caching layers
- Consider NoSQL for specific use cases

## 📚 Next Steps

After deployment:

1. **Monitor Performance**: Set up alerts and dashboards
2. **Security Audit**: Regular security assessments
3. **Backup Strategy**: Implement data backup and recovery
4. **Disaster Recovery**: Plan for service outages
5. **Cost Optimization**: Monitor and optimize cloud costs

## 🆘 Troubleshooting

### Common Deployment Issues

1. **Environment Variables**: Ensure all required variables are set
2. **Permissions**: Check IAM roles and service account permissions
3. **Network**: Verify VPC and security group configurations
4. **Dependencies**: Ensure all dependencies are included in deployment package

### Debug Commands

```bash
# Check logs
aws logs tail /aws/lambda/mcp-training-server --follow

# Test function locally
sam local invoke MCPTrainingServer --event events/test-event.json

# Check Cloud Run logs
gcloud logs read --project=YOUR_PROJECT_ID --limit=50
```

For more detailed troubleshooting, refer to the platform-specific documentation and the [Setup Guide](setup.md). 