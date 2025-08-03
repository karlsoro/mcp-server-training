# GitHub API Setup Guide for MCP Server 🔑

*So you want your AI assistant to actually manage your GitHub repos? Smart move! This guide will walk you through getting your GitHub Personal Access Token (PAT) set up so your MCP server can create issues, read repositories, and basically be your AI-powered GitHub assistant.*

## What's a GitHub Token Anyway?

Think of a GitHub Personal Access Token like a special key that gives your AI permission to act on your behalf in GitHub. It's way more secure than using your password, and you can control exactly what permissions it has. Pretty neat, right?

The MCP server uses this token to make API calls to GitHub, letting your AI assistant do things like:
- Read issues from your repositories
- Create new issues and pull requests
- Check repository status
- Manage project boards

## Prerequisites - What You'll Need

Before we dive in, make sure you have:
- A GitHub account (duh!)
- Access to GitHub settings (should be automatic)
- Basic understanding of GitHub permissions (we'll cover this)

## Step-by-Step: Getting Your Token

### Step 1: Navigate to GitHub Settings

First things first - let's get to the right place:

1. **Log in to GitHub** at [github.com](https://github.com)
2. **Click your profile picture** in the top-right corner (you know, where your avatar is)
3. **Select "Settings"** from the dropdown menu

*Pro tip: If you're already logged in, you can just go straight to [github.com/settings](https://github.com/settings)*

### Step 2: Access Developer Settings

Now we need to find the developer stuff:

1. **Scroll down** in the left sidebar (keep going, it's near the bottom)
2. **Click "Developer settings"** (it's usually the last option)
3. **Click "Personal access tokens"**
4. **Click "Tokens (classic)"**

*Why "classic"? GitHub has newer fine-grained tokens, but the classic ones work perfectly for our needs and are easier to set up.*

### Step 3: Generate New Token

Time to create your token:

1. **Click "Generate new token"**
2. **Select "Generate new token (classic)"**
3. **Give your token a descriptive name** like "MCP Server Integration" or "AI Assistant GitHub Access"

*Make the name meaningful - you might create multiple tokens for different purposes, so you want to remember what this one is for.*

### Step 4: Set Token Permissions

Here's where the magic happens. You need to select the right permissions for your AI to work properly:

#### Repository Access
- ✅ **repo** - Full control of private repositories
  - `repo:status` - Access commit status
  - `repo_deployment` - Access deployment status
  - `public_repo` - Access public repositories
  - `repo:invite` - Access repository invitations
  - `security_events` - Access security events

#### Issues and Pull Requests
- ✅ **issues** - Read and write issues
- ✅ **pull_request** - Read and write pull requests

#### User Information
- ✅ **read:user** - Read user profile data
- ✅ **user:email** - Read user email addresses

#### Optional (for advanced features)
- ✅ **workflow** - Update GitHub Action workflows
- ✅ **write:packages** - Upload packages to GitHub Package Registry

*Don't worry about the optional ones unless you're planning to do advanced stuff. The basic permissions are plenty for most use cases.*

### Step 5: Generate and Copy Token

Almost there! This is the critical part:

1. **Scroll to the bottom** of the page
2. **Click "Generate token"**
3. **Copy the token immediately** (you won't see it again!)
4. **Store it securely** (we'll use it in the next step)

⚠️ **Important**: The token will only be shown once. If you lose it, you'll need to generate a new one. No pressure, right?

## Adding Your Token to the MCP Server

Now that you've got your token, let's get it working with your MCP server. You've got a few options:

### Option 1: Environment Variable (Recommended)

This is the cleanest approach:

1. **Open your `.env` file** in the project root:
   ```bash
   nano .env
   ```

2. **Add your GitHub token**:
   ```bash
   GITHUB_TOKEN=ghp_your_actual_token_here
   ```

3. **Save the file** and restart your server

*Make sure there are no spaces around the equals sign, and don't put quotes around the token.*

### Option 2: Export Environment Variable

If you prefer to set it in your shell:

```bash
# For current session only
export GITHUB_TOKEN=ghp_your_actual_token_here

# For permanent setup (add to ~/.bashrc or ~/.zshrc)
echo 'export GITHUB_TOKEN=ghp_your_actual_token_here' >> ~/.bashrc
source ~/.bashrc
```

### Option 3: Direct in Terminal

Want to test it quickly?

```bash
# Run the server with the token
GITHUB_TOKEN=ghp_your_actual_token_here python src/server.py
```

## Testing Your GitHub Integration

Now let's make sure everything's working properly:

### 1. Run the GitHub Tests

```bash
# Activate your virtual environment
source venv/bin/activate

# Run GitHub integration tests
python -m pytest tests/test_server.py::TestGitHubIntegration -v
```

*You should see 3 out of 4 tests passing. The skipped test is for real API calls, which we'll test next.*

### 2. Test with Real API Call

Want to see it actually work? Try this:

```bash
# Test getting issues from a public repository
python -c "
import asyncio
import os
from src.server import MCPTrainingServer

async def test_github():
    server = MCPTrainingServer()
    try:
        issues = await server.get_github_issues('octocat', 'Hello-World')
        print(f'✅ Found {len(issues)} issues in octocat/Hello-World')
        for issue in issues[:3]:  # Show first 3 issues
            print(f'  - #{issue[\"number\"]}: {issue[\"title\"]}')
    except Exception as e:
        print(f'❌ Error: {e}')

asyncio.run(test_github())
"
```

*This tests with GitHub's sample repository, so it should work even if you don't have your own repos set up.*

### 3. Test Creating an Issue

Ready to create your first AI-generated issue?

```bash
# Test creating an issue (use your own repository)
python -c "
import asyncio
import os
from src.server import MCPTrainingServer

async def test_create_issue():
    server = MCPTrainingServer()
    try:
        result = await server.create_github_issue(
            'your-username', 
            'your-repo-name', 
            'Test Issue from MCP Server',
            'This is a test issue created by the MCP server integration.'
        )
        print(f'✅ {result}')
    except Exception as e:
        print(f'❌ Error: {e}')

asyncio.run(test_create_issue())
"
```

*Replace 'your-username' and 'your-repo-name' with your actual GitHub username and repository name.*

## Security Best Practices

Let's talk about keeping your token safe:

### 1. Token Security
- **Never commit tokens** to version control (GitHub will detect and revoke them automatically)
- **Use environment variables** instead of hardcoding
- **Rotate tokens regularly** (every 90 days is a good practice)
- **Use minimal permissions** (only what you need)

### 2. Repository Access
- **Test with public repositories** first
- **Use your own repositories** for testing
- **Be careful with private repository access**

### 3. Rate Limiting
- **GitHub has rate limits** (5,000 requests/hour for authenticated users)
- **Monitor your usage** to avoid hitting limits
- **Implement caching** for frequently accessed data

## Troubleshooting - When Things Go Wrong

### Common Issues and Solutions

#### 1. "GitHub token is required"
**Solution**: Make sure your token is properly set in the environment:
```bash
echo $GITHUB_TOKEN
```

#### 2. "Bad credentials" or "401 Unauthorized"
**Solution**: 
- Check that your token is correct
- Ensure the token hasn't expired
- Verify the token has the required permissions

#### 3. "Not Found" or "404"
**Solution**:
- Check that the repository exists
- Ensure you have access to the repository
- Verify the repository name is correct

#### 4. Rate Limiting
**Solution**:
- Wait for the rate limit to reset
- Implement caching in your application
- Use a different token if available

### Debugging Commands

```bash
# Check if token is set
echo "Token set: $([ -n "$GITHUB_TOKEN" ] && echo "Yes" || echo "No")"

# Test token format
echo "Token format: ${GITHUB_TOKEN:0:10}..."  # Show first 10 characters

# Test GitHub API directly
curl -H "Authorization: token $GITHUB_TOKEN" \
     https://api.github.com/user
```

## Additional Resources

### GitHub API Documentation
- [GitHub REST API](https://docs.github.com/en/rest) - Complete API reference
- [Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) - Official token documentation
- [Rate Limiting](https://docs.github.com/en/rest/overview/resources-in-the-rest-api#rate-limiting) - Understanding API limits

### MCP Server Documentation
- [MCP Server Setup](SETUP_GUIDE.md) - Complete server setup
- [Testing Guide](TESTING_GUIDE.md) - Comprehensive testing framework
- [API Documentation](docs/api.md) - Tool reference

## Success Criteria - How to Know You're Done

Your GitHub integration is working when:
- ✅ GitHub tests pass: `python -m pytest tests/test_server.py::TestGitHubIntegration -v`
- ✅ You can retrieve issues from public repositories
- ✅ You can create issues in your own repositories
- ✅ No authentication errors occur
- ✅ Rate limiting is respected

## Next Steps - What's Next?

1. **Test with your own repositories** - Try creating issues in your projects
2. **Explore additional GitHub API features** - There's a lot more you can do
3. **Implement caching** for better performance
4. **Set up monitoring** for rate limits
5. **Consider using GitHub Apps** for more advanced integrations

## Industry Context

GitHub's API is one of the most widely used developer APIs in the world, with over 100 million repositories and 40+ million developers. Companies like Microsoft, Google, and Netflix use GitHub's API extensively for automation and integration.

The Personal Access Token system was introduced in 2013 as a more secure alternative to password-based authentication, and it's now the standard for API access across the GitHub ecosystem.

---

**Need Help?** If you encounter issues, check the troubleshooting section above or refer to the GitHub API documentation for more detailed error messages. The GitHub community is also incredibly helpful - don't hesitate to ask questions!

## References

1. **GitHub REST API**: [Official Documentation](https://docs.github.com/en/rest)
2. **Personal Access Tokens**: [GitHub Security Documentation](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
3. **Rate Limiting**: [GitHub API Limits](https://docs.github.com/en/rest/overview/resources-in-the-rest-api#rate-limiting)
4. **GitHub Apps**: [Advanced Integration Guide](https://docs.github.com/en/apps)
5. **MCP Protocol**: [Model Context Protocol](https://modelcontextprotocol.io/)
6. **Python httpx**: [HTTP Client Library](https://www.python-httpx.org/)
7. **GitHub Developer Program**: [Developer Resources](https://docs.github.com/en/developers) 