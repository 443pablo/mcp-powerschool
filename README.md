# PowerSchool MCP Server

A [FastMCP](https://github.com/jlowin/fastmcp) server for PowerSchool that enables students to check grades, assignments, grade history, and attendance through the Model Context Protocol.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/443pablo/mcp-powerschool)

## Features

This MCP server provides the following tools for students:

- **get_student_info**: Get current student information (name, ID, grade level, school)
- **get_current_grades**: View current grades for all courses
- **get_assignments**: List assignments (optionally filter by course)
- **get_grade_history**: View historical grade data with date filtering
- **get_courses**: List all enrolled courses/sections
- **get_attendance**: View attendance records
- **get_server_info**: Check server configuration and status

## Configuration

### Required Environment Variables

You need to configure the following environment variables to connect to your PowerSchool instance:

```bash
# PowerSchool server URL (without trailing slash)
POWERSCHOOL_URL=https://your-school.powerschool.com

# OAuth2 Client Credentials from PowerSchool Plugin
POWERSCHOOL_CLIENT_ID=your_client_id
POWERSCHOOL_CLIENT_SECRET=your_client_secret

# Student Authentication (for password grant type)
POWERSCHOOL_USERNAME=student_username
POWERSCHOOL_PASSWORD=student_password
```

### PowerSchool Setup

This server requires a PowerSchool plugin with OAuth2 enabled. Your PowerSchool administrator needs to:

1. Install a PowerSchool plugin with `<oauth/>` enabled in `plugin.xml`
2. Configure API permissions for student data access
3. Generate OAuth2 client credentials (client ID and secret)
4. Enable the necessary API endpoints:
   - `/ws/v1/student` - Student information
   - `/ws/v1/student/grades` - Grade data
   - `/ws/v1/student/assignments` - Assignment data
   - `/ws/v1/student/sections` - Course/section data
   - `/ws/v1/student/attendance` - Attendance data

For more information about PowerSchool's API, see:
- [PowerSchool API Documentation](https://support.powerschool.com/developer)
- [Reverse-engineered API Reference](https://github.com/grantholle/powerschool-api)

## Local Development

### Setup

Fork the repo, then run:

```bash
git clone <your-repo-url>
cd mcp-powerschool
conda create -n mcp-powerschool python=3.13
conda activate mcp-powerschool
pip install -r requirements.txt
```

### Configure Environment Variables

Create a `.env` file or set environment variables:

```bash
export POWERSCHOOL_URL=https://your-school.powerschool.com
export POWERSCHOOL_CLIENT_ID=your_client_id
export POWERSCHOOL_CLIENT_SECRET=your_client_secret
export POWERSCHOOL_USERNAME=your_username
export POWERSCHOOL_PASSWORD=your_password
```

### Test Locally

```bash
python src/server.py
# then in another terminal run:
npx @modelcontextprotocol/inspector
```

Open http://localhost:3000 and connect to `http://localhost:8000/mcp` using "Streamable HTTP" transport (NOTE THE `/mcp`!).

### Available Tools

Once connected, you can test the following tools:

1. **get_server_info** - Verify configuration
2. **get_student_info** - Get student details
3. **get_current_grades** - View all current grades
4. **get_courses** - List enrolled courses
5. **get_assignments** - View assignments (optional: pass section_id)
6. **get_grade_history** - View historical grades (optional: pass start_date, end_date)
7. **get_attendance** - View attendance records

## Deployment

### Option 1: One-Click Deploy to Render

1. Click the "Deploy to Render" button above
2. Configure the required environment variables in Render's dashboard:
   - `POWERSCHOOL_URL`
   - `POWERSCHOOL_CLIENT_ID`
   - `POWERSCHOOL_CLIENT_SECRET`
   - `POWERSCHOOL_USERNAME`
   - `POWERSCHOOL_PASSWORD`

### Option 2: Manual Deployment

1. Fork this repository
2. Connect your GitHub account to Render
3. Create a new Web Service on Render
4. Connect your forked repository
5. Render will automatically detect the `render.yaml` configuration
6. Add the required environment variables in Render's dashboard

Your server will be available at `https://your-service-name.onrender.com/mcp` (NOTE THE `/mcp`!)

## Usage with AI Assistants

You can connect this MCP server to various AI assistants that support the Model Context Protocol:

### Claude Desktop

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "powerschool": {
      "url": "https://your-service-name.onrender.com/mcp"
    }
  }
}
```

### Poke

You can connect your MCP server to Poke at [poke.com/settings/connections](https://poke.com/settings/connections).

To test the connection explicitly, ask poke something like: `Tell the subagent to use the "powerschool" integration's "get_current_grades" tool`.

If you run into persistent issues of poke not calling the right MCP (e.g. after you've renamed the connection), you may send `clearhistory` to poke to delete all message history and start fresh.

## Example Usage

Here are some example queries you can make through your AI assistant:

- "What are my current grades?"
- "Show me my assignments for math class"
- "What's my attendance record this semester?"
- "How have my grades changed over the last month?"
- "List all my courses and teachers"
- "Show me my student information"

## API Reference

### PowerSchool API Endpoints

This server uses the PowerSchool REST API. The main endpoints are:

- `GET /ws/v1/student` - Get student information
- `GET /ws/v1/student/grades` - Get current grades
- `GET /ws/v1/student/assignments` - Get all assignments
- `GET /ws/v1/student/assignments/section/{id}` - Get assignments for a section
- `GET /ws/v1/student/sections` - Get enrolled sections/courses
- `GET /ws/v1/student/attendance` - Get attendance records
- `GET /ws/v1/student/grades/history` - Get historical grades

### Authentication

The server uses OAuth2 for authentication with PowerSchool. It supports both:

1. **Client Credentials Grant** - For server-to-server authentication
2. **Password Grant** - For student username/password authentication

The authentication token is automatically cached and refreshed as needed.

## Security Notes

⚠️ **Important Security Considerations:**

1. **Credentials Storage**: Store credentials securely using environment variables or secret management services. Never commit credentials to version control.

2. **HTTPS**: Always use HTTPS in production to protect credentials and student data in transit.

3. **Access Control**: This server is designed for individual student use. Each deployment should be configured with credentials for a single student.

4. **Token Security**: Authentication tokens are cached in memory and automatically refreshed. They are never persisted to disk.

5. **Production Deployment**: When deploying to production, ensure your hosting platform (like Render) properly secures environment variables.

## Troubleshooting

### Configuration Issues

If you get configuration errors, verify:
- All required environment variables are set
- PowerSchool URL doesn't have a trailing slash
- Client ID and secret are correct
- Student credentials are valid (if using password grant)

### Connection Issues

If the server can't connect to PowerSchool:
- Verify PowerSchool URL is accessible
- Check that the PowerSchool plugin is installed and OAuth is enabled
- Ensure API endpoints are enabled for student access
- Check firewall rules if running on-premises

### Authentication Issues

If authentication fails:
- Verify client credentials are correct
- Check that student username/password are valid
- Ensure the OAuth2 grant type (password or client_credentials) is enabled

Use the `get_server_info` tool to check configuration status.

## Development

### Adding New Tools

You can add more PowerSchool API endpoints by:

1. Adding a method to the `PowerSchoolAPI` class
2. Creating a corresponding MCP tool with `@mcp.tool` decorator
3. Following the existing pattern for error handling and response format

Example:

```python
@mcp.tool(description="Get school calendar events")
def get_calendar() -> dict:
    try:
        client = get_api_client()
        result = client._make_request("/ws/v1/student/calendar")
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
```

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues related to:
- **This MCP Server**: Open an issue on GitHub
- **PowerSchool API**: Contact PowerSchool support or your school administrator
- **MCP Protocol**: See [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
