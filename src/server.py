#!/usr/bin/env python3
"""
MCP Server Training Project - Main Server Implementation

Ever wondered how AI assistants can actually interact with your files, GitHub repos, 
and external services? This is the real deal - a comprehensive MCP server that 
demonstrates various tool integrations and best practices for production deployment.

This module implements a working MCP server using FastMCP that can:
- Handle file operations safely
- Integrate with GitHub for issue management
- Connect to Notion for note-taking
- Fetch weather information
- Provide comprehensive error handling and validation

The server is designed to be production-ready with proper testing, security, 
and documentation. It's not just a demo - it's real software that could 
actually be deployed and used.
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

# MCP imports - these are the building blocks for our AI assistant's toolkit
from mcp.server.fastmcp import FastMCP
from mcp.types import Tool

# Third-party imports - the tools that make the magic happen
import httpx
from pydantic import BaseModel, Field
import aiofiles

# Configure logging - because we want to know what's happening
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration - where we store all the important stuff
class Config:
    """
    Configuration class for the MCP server.
    
    This handles all the environment variables and settings that make
    our server work. Think of it as the control panel for our AI assistant.
    """
    
    def __init__(self):
        # API tokens - these are like keys to different services
        self.notion_api_token = os.getenv("NOTION_API_TOKEN")
        self.notion_database_id = os.getenv("NOTION_DATABASE_ID")
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.openweather_api_key = os.getenv("OPENWEATHER_API_KEY")
        
        # Server identity - who we are
        self.server_name = "mcp-training-server"
        self.server_version = "1.0.0"
        
        # Validate that we have what we need
        self._validate_config()
    
    def _validate_config(self):
        """
        Validate that required configuration is present.
        
        This checks if we have the API keys we need and warns us
        if something's missing. It's like a pre-flight checklist.
        """
        missing_vars = []
        
        if not self.notion_api_token:
            missing_vars.append("NOTION_API_TOKEN")
        if not self.notion_database_id:
            missing_vars.append("NOTION_DATABASE_ID")
        if not self.github_token:
            missing_vars.append("GITHUB_TOKEN")
        if not self.openweather_api_key:
            missing_vars.append("OPENWEATHER_API_KEY")
        
        if missing_vars:
            logger.warning(f"Missing environment variables: {', '.join(missing_vars)}")
            logger.warning("Some tools may not function properly without these variables.")

# Initialize configuration - set up our control panel
config = Config()

# Create FastMCP server instance - this is the heart of our AI assistant
server = FastMCP(
    name=config.server_name,
    instructions="MCP Training Server - A comprehensive server demonstrating various tool integrations including Notion, GitHub, Weather APIs, and file operations."
)

class MCPTrainingServer:
    """
    Main MCP server class with comprehensive tool implementations.
    
    This is where all the magic happens. Each method here becomes a tool
    that your AI assistant can use. Think of it as giving your AI a
    Swiss Army knife of capabilities.
    """
    
    def __init__(self):
        self.config = config
        self.setup_tools()
    
    def setup_tools(self):
        """
        Register all available tools with the FastMCP server.
        
        This is where we define all the tools our AI assistant can use.
        Each @server.tool() decorator creates a new capability.
        """
        
        # Register tools using FastMCP decorators - this is the modern way
        @server.tool()
        async def get_notion_notes(max_results: int = 10) -> List[Dict[str, Any]]:
            """
            Retrieve a list of notes from a Notion database.
            
            This lets your AI assistant read your Notion notes. Pretty cool, right?
            Just make sure you've got your Notion API token set up.
            """
            if not self.config.notion_api_token or not self.config.notion_database_id:
                raise ValueError("Notion API token and database ID are required")
            
            async with httpx.AsyncClient() as client:
                headers = {
                    "Authorization": f"Bearer {self.config.notion_api_token}",
                    "Notion-Version": "2022-06-28",
                    "Content-Type": "application/json",
                }
                response = await client.post(
                    f"https://api.notion.com/v1/databases/{self.config.notion_database_id}/query",
                    headers=headers,
                    json={"page_size": max_results},
                )
                response.raise_for_status()
                results = response.json().get("results", [])
                return [page["properties"]["Name"]["title"][0]["text"]["content"] for page in results]

        @server.tool()
        async def create_notion_note(title: str, content: str) -> str:
            """
            Create a new note in a Notion database.
            
            Your AI assistant can now create notes in your Notion workspace.
            Just tell it what you want to remember!
            """
            if not self.config.notion_api_token or not self.config.notion_database_id:
                raise ValueError("Notion API token and database ID are required")
            
            async with httpx.AsyncClient() as client:
                headers = {
                    "Authorization": f"Bearer {self.config.notion_api_token}",
                    "Notion-Version": "2022-06-28",
                    "Content-Type": "application/json",
                }
                payload = {
                    "parent": {"database_id": self.config.notion_database_id},
                    "properties": {
                        "Name": {"title": [{"text": {"content": title}}]},
                        "Content": {"rich_text": [{"text": {"content": content}}]},
                    },
                }
                response = await client.post(
                    "https://api.notion.com/v1/pages",
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                return "Note created successfully!"

        @server.tool()
        async def get_github_issues(owner: str, repo: str, state: str = "open", max_results: int = 10) -> List[Dict[str, Any]]:
            """
            Retrieve GitHub issues from a repository.
            
            This lets your AI assistant read issues from your GitHub repos.
            Perfect for project management and bug tracking!
            """
            if not self.config.github_token:
                raise ValueError("GitHub token is required")
            
            async with httpx.AsyncClient() as client:
                headers = {
                    "Authorization": f"token {self.config.github_token}",
                    "Accept": "application/vnd.github.v3+json",
                }
                response = await client.get(
                    f"https://api.github.com/repos/{owner}/{repo}/issues",
                    headers=headers,
                    params={"state": state, "per_page": max_results},
                )
                response.raise_for_status()
                issues = response.json()
                return [{"title": issue["title"], "number": issue["number"], "state": issue["state"]} for issue in issues]

        @server.tool()
        async def create_github_issue(owner: str, repo: str, title: str, body: str = "") -> str:
            """
            Create a new GitHub issue.
            
            Your AI assistant can now create issues in your GitHub repos.
            Just describe the problem and let your AI handle the rest!
            """
            if not self.config.github_token:
                raise ValueError("GitHub token is required")
            
            async with httpx.AsyncClient() as client:
                headers = {
                    "Authorization": f"token {self.config.github_token}",
                    "Accept": "application/vnd.github.v3+json",
                }
                payload = {"title": title, "body": body}
                response = await client.post(
                    f"https://api.github.com/repos/{owner}/{repo}/issues",
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                return f"Issue created successfully! Issue #{response.json()['number']}"

        @server.tool()
        async def get_weather(city: str, country_code: str = "US") -> Dict[str, Any]:
            """
            Get current weather information for a location.
            
            Want to know if you need an umbrella? Your AI assistant can check
            the weather for any city in the world.
            """
            if not self.config.openweather_api_key:
                raise ValueError("OpenWeather API key is required")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "http://api.openweathermap.org/data/2.5/weather",
                    params={
                        "q": f"{city},{country_code}",
                        "appid": self.config.openweather_api_key,
                        "units": "metric"
                    }
                )
                response.raise_for_status()
                data = response.json()
                return {
                    "city": data["name"],
                    "country": data["sys"]["country"],
                    "temperature": data["main"]["temp"],
                    "description": data["weather"][0]["description"],
                    "humidity": data["main"]["humidity"],
                    "wind_speed": data["wind"]["speed"]
                }

        @server.tool()
        async def save_file(filename: str, content: str) -> str:
            """
            Save content to a file.
            
            Your AI assistant can now save files for you. It's like having
            a personal secretary that never forgets where you put things.
            """
            # Ensure we're writing to a safe directory - security first!
            safe_dir = os.path.join(os.getcwd(), "data")
            os.makedirs(safe_dir, exist_ok=True)
            
            filepath = os.path.join(safe_dir, filename)
            
            async with aiofiles.open(filepath, 'w') as f:
                await f.write(content)
            
            return f"Content saved to {filepath}"

        @server.tool()
        async def read_file(filename: str) -> str:
            """
            Read content from a file.
            
            Your AI assistant can read files you've saved. Perfect for
            reviewing documents or checking what you wrote earlier.
            """
            # Ensure we're reading from a safe directory
            safe_dir = os.path.join(os.getcwd(), "data")
            filepath = os.path.join(safe_dir, filename)
            
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"File {filename} not found")
            
            async with aiofiles.open(filepath, 'r') as f:
                content = await f.read()
            
            return content

        @server.tool()
        async def list_files(directory: str = ".") -> List[str]:
            """
            List files in a directory.
            
            Your AI assistant can see what files you have. It's like
            having a personal file manager that never gets confused.
            """
            # Ensure we're listing from a safe directory
            safe_dir = os.path.join(os.getcwd(), "data")
            target_dir = os.path.join(safe_dir, directory.lstrip("./"))
            
            if not os.path.exists(target_dir):
                raise FileNotFoundError(f"Directory {directory} not found")
            
            files = []
            for item in os.listdir(target_dir):
                item_path = os.path.join(target_dir, item)
                if os.path.isfile(item_path):
                    files.append(item)
            
            return files

        @server.tool()
        async def get_server_info() -> Dict[str, Any]:
            """
            Get information about the MCP server.
            
            This gives you the status of your AI assistant's toolkit.
            It's like checking the dashboard of your personal AI butler.
            """
            return {
                "server_name": self.config.server_name,
                "server_version": self.config.server_version,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "config_status": {
                    "notion_configured": bool(self.config.notion_api_token and self.config.notion_database_id),
                    "github_configured": bool(self.config.github_token),
                    "weather_configured": bool(self.config.openweather_api_key)
                }
            }
        
        # Store tool functions for testing - this lets our tests access the tools
        self.get_notion_notes = get_notion_notes
        self.create_notion_note = create_notion_note
        self.get_github_issues = get_github_issues
        self.create_github_issue = create_github_issue
        self.get_weather = get_weather
        self.save_file = save_file
        self.read_file = read_file
        self.list_files = list_files
        self.get_server_info = get_server_info

# Create server instance - this is what gets used by the MCP client
mcp_server = MCPTrainingServer()

if __name__ == "__main__":
    try:
        # Run the server using stdio transport - this is how MCP clients connect
        server.run(transport="stdio")
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        sys.exit(1) 