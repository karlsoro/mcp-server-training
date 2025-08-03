#!/usr/bin/env python3
"""
Simple test script for MCP Server Training Project
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from server import MCPTrainingServer


async def test_server():
    """Test the MCP server functionality."""
    print("🧪 Testing MCP Server Training Project")
    print("=" * 50)
    
    # Set test environment variables
    test_env = {
        'NOTION_API_TOKEN': 'test_notion_token',
        'NOTION_DATABASE_ID': 'test_database_id',
        'GITHUB_TOKEN': 'test_github_token',
        'OPENWEATHER_API_KEY': 'test_weather_key'
    }
    
    # Update environment
    os.environ.update(test_env)
    
    try:
        # Create server instance
        print("📦 Creating server instance...")
        server = MCPTrainingServer()
        print("✅ Server instance created successfully")
        
        # Test server info
        print("\n🔍 Testing server info...")
        info = await server.get_server_info({})
        print(f"✅ Server info retrieved:")
        print(f"   - Name: {info['server_name']}")
        print(f"   - Version: {info['server_version']}")
        print(f"   - Available tools: {len(info['available_tools'])}")
        print(f"   - Config status: {info['config_status']}")
        
        # Test file operations
        print("\n📁 Testing file operations...")
        
        # Create test data directory
        data_dir = Path('data')
        data_dir.mkdir(exist_ok=True)
        
        # Test save file
        save_result = await server.save_file({
            'filename': 'test.txt',
            'content': 'Hello, MCP Server!'
        })
        print(f"✅ File saved: {save_result}")
        
        # Test list files
        files = await server.list_files({'directory': '.'})
        print(f"✅ Files listed: {files}")
        
        # Test read file
        content = await server.read_file({'filename': 'test.txt'})
        print(f"✅ File content: {content}")
        
        # Test tool listing
        print("\n🛠️ Testing tool listing...")
        from mcp.types import ListToolsRequest
        tools_result = await server.list_tools(None, ListToolsRequest())
        print(f"✅ Available tools: {len(tools_result.tools)}")
        for tool in tools_result.tools:
            print(f"   - {tool.name}: {tool.description}")
        
        # Test tool calling
        print("\n🔧 Testing tool calling...")
        from mcp.types import CallToolRequest
        call_result = await server.call_tool(None, CallToolRequest(
            name='get_server_info',
            arguments={}
        ))
        print(f"✅ Tool call result: {call_result.isError}")
        
        print("\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def main():
    """Main function."""
    print("🚀 MCP Server Training - Test Runner")
    print("This script tests the basic functionality of the MCP server.")
    print()
    
    # Check if running in virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Warning: Not running in a virtual environment")
        print("   Consider activating your virtual environment first")
        print()
    
    # Run tests
    success = asyncio.run(test_server())
    
    if success:
        print("\n✅ All tests passed!")
        print("\nNext steps:")
        print("1. Set up your API keys in the .env file")
        print("2. Run the server: python src/server.py")
        print("3. Test with MCP inspector: mcp inspect")
        print("4. Deploy to your preferred cloud platform")
    else:
        print("\n❌ Some tests failed!")
        print("Check the error messages above and fix any issues.")
        sys.exit(1)


if __name__ == "__main__":
    main() 