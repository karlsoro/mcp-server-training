# MCP Server Training - Setup Guide

This guide provides step-by-step instructions for setting up and running the MCP Server Training project.

## 🎯 Prerequisites

Before you begin, ensure you have the following installed:

### Required Software
- **Python 3.10+**: [Download Python](https://www.python.org/downloads/)
- **Git**: [Download Git](https://git-scm.com/downloads)
- **Docker** (optional): [Download Docker](https://www.docker.com/products/docker-desktop/)

### API Keys and Tokens
You'll need to obtain the following API keys and tokens:

1. **Notion API Token**: [Create Notion Integration](https://www.notion.so/my-integrations)
2. **GitHub Personal Access Token**: [Create GitHub Token](https://github.com/settings/tokens)
3. **OpenWeather API Key**: [Get OpenWeather API Key](https://openweathermap.org/api)

## 🚀 Quick Start

### Step 1: Clone the Repository

```bash
git clone <your-repo-url>
cd mcp-server-training
```

### Step 2: Install uv Package Manager

The project uses `uv` for efficient package management. Install it:

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
Download from [https://astral.sh/uv](https://astral.sh/uv)

### Step 3: Set Up Virtual Environment

```bash
# Create virtual environment
uv venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate
```

### Step 4: Install Dependencies

```bash
# Install all dependencies
uv pip install -r requirements.txt

# Or install with uv
uv sync
```

### Step 5: Configure Environment Variables

```bash
# Copy the example environment file
cp env.example .env

# Edit the .env file with your actual values
nano .env  # or use your preferred editor
```

Fill in your API keys and tokens in the `.env` file:

```env
# Notion Configuration
NOTION_API_TOKEN=your_actual_notion_token
NOTION_DATABASE_ID=your_actual_database_id

# GitHub Configuration
GITHUB_TOKEN=your_actual_github_token

# OpenWeather Configuration
OPENWEATHER_API_KEY=your_actual_openweather_key
```

### Step 6: Set Up Notion Database

1. Create a new Notion database
2. Add the following properties:
   - **Name** (Title type)
   - **Content** (Text type)
3. Share the database with your Notion integration
4. Copy the database ID from the URL

### Step 7: Test the Server

```bash
# Run the server locally
python src/server.py
```

The server should start and listen for connections via stdio.

## 🧪 Testing the Server

### Using MCP Inspector

Install the MCP CLI tools:

```bash
uv pip install mcp[cli]
```

Test the server:

```bash
# Start the MCP inspector
mcp inspect

# In another terminal, run the server
python src/server.py
```

### Manual Testing

You can test individual tools using the MCP inspector or by creating a test script:

```python
# test_server.py
import asyncio
import json
from src.server import MCPTrainingServer

async def test_server():
    server = MCPTrainingServer()
    
    # Test server info
    result = await server.get_server_info({})
    print("Server Info:", json.dumps(result, indent=2))
    
    # Test weather (if configured)
    try:
        weather = await server.get_weather({"city": "New York"})
        print("Weather:", json.dumps(weather, indent=2))
    except Exception as e:
        print(f"Weather test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_server())
```

## 🐳 Docker Setup

### Build the Docker Image

```bash
# Build production image
docker build -t mcp-training-server .

# Build development image
docker build --target development -t mcp-training-server:dev .
```

### Run with Docker

```bash
# Run production container
docker run -i --rm \
  -e NOTION_API_TOKEN=your_token \
  -e NOTION_DATABASE_ID=your_database_id \
  -e GITHUB_TOKEN=your_github_token \
  -e OPENWEATHER_API_KEY=your_weather_key \
  mcp-training-server

# Run development container
docker run -i --rm \
  -v $(pwd):/app \
  -e NOTION_API_TOKEN=your_token \
  -e NOTION_DATABASE_ID=your_database_id \
  -e GITHUB_TOKEN=your_github_token \
  -e OPENWEATHER_API_KEY=your_weather_key \
  mcp-training-server:dev
```

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `NOTION_API_TOKEN` | Notion API token | Yes | - |
| `NOTION_DATABASE_ID` | Notion database ID | Yes | - |
| `GITHUB_TOKEN` | GitHub personal access token | Yes | - |
| `OPENWEATHER_API_KEY` | OpenWeather API key | Yes | - |
| `SERVER_NAME` | Server name | No | mcp-training-server |
| `SERVER_VERSION` | Server version | No | 1.0.0 |
| `LOG_LEVEL` | Logging level | No | INFO |

### Configuration Files

The server supports multiple configuration methods:

1. **Environment Variables**: Set in `.env` file or system environment
2. **Configuration Files**: Create `config/config.yaml` for advanced settings
3. **Command Line Arguments**: Use argparse for runtime configuration

## 🛠️ Development Setup

### Code Quality Tools

```bash
# Install development dependencies
uv pip install -r requirements.txt

# Run code formatting
black src/ tests/

# Run linting
flake8 src/ tests/

# Run type checking
mypy src/

# Run tests
pytest tests/
```

### Pre-commit Hooks

Set up pre-commit hooks for automatic code quality checks:

```bash
# Install pre-commit
uv pip install pre-commit

# Install hooks
pre-commit install
```

## 🔍 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure you're in the virtual environment
   ```bash
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   ```

2. **API Key Errors**: Verify your API keys are correctly set in `.env`
   ```bash
   echo $NOTION_API_TOKEN  # Should show your token
   ```

3. **Permission Errors**: Check file permissions
   ```bash
   chmod +x src/server.py
   ```

4. **Docker Issues**: Ensure Docker is running and you have sufficient permissions

### Debug Mode

Run the server in debug mode for more verbose output:

```bash
# Set debug environment variable
export LOG_LEVEL=DEBUG

# Run server
python src/server.py
```

### Logs

Check server logs for detailed error information:

```bash
# View logs in real-time
tail -f logs/mcp_server.log
```

## 📚 Next Steps

After successful setup:

1. **Read the API Documentation**: [API Guide](api.md)
2. **Deploy to Cloud**: [Deployment Guide](deployment.md)
3. **Extend Functionality**: [Development Guide](development.md)
4. **Run Tests**: [Testing Guide](testing.md)

## 🆘 Getting Help

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review the [API Documentation](api.md)
3. Open an issue on GitHub
4. Check the logs for error details

## 🔗 Additional Resources

- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- [MCP GitHub Repository](https://github.com/modelcontextprotocol)
- [Notion API Documentation](https://developers.notion.com/)
- [GitHub API Documentation](https://docs.github.com/en/rest)
- [OpenWeather API Documentation](https://openweathermap.org/api) 